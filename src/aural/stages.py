"""The three model calls shared by pipelines.

plan() makes a timed beat sheet.
write() turns that sheet into spoken lines.
edit_for_speech() rewrites the lines so they are easy to say.

Each function builds a system string (the role) and a user string (the job),
then asks for JSON. A later pipeline can call these after it has a Brief,
for example after it has asked the user a few follow-up questions.
"""

import json

from aural.cues import CUE_HELP, PLAIN_HELP
from aural.genres import genre_note
from aural.llm import ask_json
from aural.models import Brief, Script

# Spoken pace used to turn minutes into a word target.
WORDS_PER_MINUTE = 140

ADULT_RULES = (
    "You write audio scripts for adult listeners. "
    "Every character is an adult, and so is the listener being addressed. "
    "Write the sexual content the prompt asks for, plainly and specifically. "
    "Do not fade to black, and do not put a disclaimer in the script. "
    "Never include anyone under 18. "
    "Reply with one JSON object and no other text."
)


def plan(complete, brief: Brief) -> dict:
    """Ask for a beat sheet. Returns the planner's JSON object."""
    system = (
        "You are the planner.\n"
        f"{ADULT_RULES}\n"
        "Break the piece into beats a narrator can speak. "
        "Give each beat a name, a length in minutes, and a summary of what is said.\n"
        'JSON shape: {"title": "short title", "genre": "story|hypnosis|meditation|custom", '
        '"minutes": 10, "beats": [{"name": "induction", "minutes": 2, '
        '"summary": "what is spoken"}]}'
    )
    user = _brief_block(brief)
    data = ask_json(complete, "plan", system, user, _validate_outline)
    if brief.genre:
        data["genre"] = brief.genre
    if brief.minutes:
        data["minutes"] = brief.minutes
    return data


def write(complete, brief: Brief, outline: dict) -> Script:
    """Draft the full script from the outline."""
    minutes = int(outline.get("minutes") or brief.minutes or 10)
    word_target = minutes * WORDS_PER_MINUTE
    cue_rule = PLAIN_HELP if brief.plain else CUE_HELP
    system = (
        "You are the writer.\n"
        f"{ADULT_RULES}\n"
        "Turn the outline into a script for one speaker named Narrator. "
        "Every line is something the narrator says. "
        f"Aim for about {word_target} words, near {WORDS_PER_MINUTE} words per minute. "
        "Use contractions and sentences a person can say in one breath.\n"
        f"{cue_rule}\n"
        'JSON shape: {"title": "...", "genre": "...", "minutes": 10, '
        '"speakers": ["Narrator"], "lines": [{"speaker": "Narrator", "text": "spoken line"}]}'
    )
    user = (
        _brief_block(brief)
        + "\n\nOutline:\n"
        + json.dumps(outline, indent=2)
    )
    # from_data raises when the JSON has no usable lines, which triggers one retry.
    data = ask_json(complete, "write", system, user, lambda payload: Script.from_data(payload, brief))
    return Script.from_data(data, brief)


def edit_for_speech(complete, brief: Brief, draft: Script) -> Script:
    """Rewrite the draft so it sounds spoken. Keep the same JSON shape."""
    cue_rule = PLAIN_HELP if brief.plain else CUE_HELP
    system = (
        "You are the speech editor.\n"
        f"{ADULT_RULES}\n"
        "Rewrite the script so it is easy to say aloud. "
        "Keep one speaker, Narrator. Keep the meaning, the sexual content, and the ending. "
        "Prefer short sentences and contractions. "
        "Drop anything that is not spoken, such as a chapter title inside a line.\n"
        f"{cue_rule}\n"
        'JSON shape: {"title": "...", "genre": "...", "minutes": 10, '
        '"speakers": ["Narrator"], "lines": [{"speaker": "Narrator", "text": "spoken line"}]}'
    )
    user = (
        _brief_block(brief)
        + "\n\nDraft:\n"
        + json.dumps(draft.to_dict(), indent=2)
    )
    # Same check as the writer: bad JSON, or JSON with no lines, is retried once.
    data = ask_json(complete, "edit", system, user, lambda payload: Script.from_data(payload, brief))
    edited = Script.from_data(data, brief)
    edited.minutes = edited.minutes or draft.minutes
    return edited


def _brief_block(brief: Brief) -> str:
    minutes = (
        str(brief.minutes)
        if brief.minutes
        else "use a length named in the prompt, otherwise 10"
    )
    limits = brief.limits.strip() if brief.limits else "none"
    return (
        f"Prompt:\n{brief.prompt.strip()}\n\n"
        f"Genre note:\n{genre_note(brief.genre)}\n\n"
        f"Target minutes: {minutes}\n"
        f"Hard limits (do not cross these): {limits}\n"
        f"Delivery cues: {'off' if brief.plain else 'on'}"
    )


def _validate_outline(data: dict) -> None:
    if not isinstance(data.get("beats"), list) or not data["beats"]:
        raise KeyError("beats")
    for beat in data["beats"]:
        if not isinstance(beat, dict) or "summary" not in beat:
            raise KeyError("summary")
    if not str(data.get("title") or "").strip():
        raise KeyError("title")
