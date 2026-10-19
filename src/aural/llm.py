"""The only place this project talks to the xAI API.

A chat message has a role:
- system: standing instructions for this stage ("you are the planner")
- user: the job for this one call (the prompt, the outline, or the draft)

live_complete() sends both and returns the model's text.
ask_json() is what the stages use. It expects a JSON object, and if the
reply is not usable it asks one more time, then stops.

Tests pass their own complete function into the pipeline, so they never
reach the network. The SDK is imported inside live_complete() for the
same reason: you can read and test the rest of the program without a key.
"""

import json
import re

from aural.config import require_api_key

# Long enough for a full script. The xAI quickstart uses a long timeout
# because a reasoning model can sit for a while before the first token.
REQUEST_TIMEOUT_SECONDS = 3600


class StageError(Exception):
    """A stage replied twice without JSON the program could use."""

    def __init__(self, stage: str, raw: str):
        self.stage = stage
        self.raw = raw
        super().__init__(
            f"The {stage} stage did not return JSON the program could read."
        )


def live_complete(system_text: str, user_text: str) -> str:
    """Send one system message and one user message. Return the reply text."""
    settings = require_api_key()

    # Imported here so tests and `aural --help` work before you call the API.
    from xai_sdk import Client
    from xai_sdk.chat import system, user

    # Each stage creates its own chat. That is one request per stage.
    # client.chat.create picks the model. append() adds messages in order.
    # sample() waits for the model. .content is the reply as a string.
    client = Client(api_key=settings.api_key, timeout=REQUEST_TIMEOUT_SECONDS)
    chat = client.chat.create(model=settings.model)
    chat.append(system(system_text))
    chat.append(user(user_text))
    return chat.sample().content


def ask_json(complete, stage: str, system_text: str, user_text: str, validate) -> dict:
    """Call complete(), parse one JSON object, and check it with validate.

    validate(data) should raise KeyError, TypeError, or ValueError when the
    shape is wrong. Those failures get one retry, same as bad JSON.
    """
    raw = complete(system_text, user_text)
    try:
        data = parse_json_object(raw)
        validate(data)
        return data
    except (json.JSONDecodeError, ValueError, KeyError, TypeError):
        pass

    retry_user = (
        user_text
        + "\n\nYour previous reply could not be used. "
        "Reply again with one JSON object and no markdown.\n\n"
        "Previous reply:\n"
        + raw
    )
    second = complete(system_text, retry_user)
    try:
        data = parse_json_object(second)
        validate(data)
        return data
    except (json.JSONDecodeError, ValueError, KeyError, TypeError) as exc:
        raise StageError(stage, second) from exc


def parse_json_object(raw: str) -> dict:
    """Pull one JSON object out of a reply.

    Models often wrap JSON in ```json fences, or add a sentence first.
    This accepts a bare object, a fenced object, or text that contains one.
    """
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end <= start:
            raise
        value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("reply JSON was not an object")
    return value
