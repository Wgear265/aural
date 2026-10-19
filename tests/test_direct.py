"""The direct pipeline, without calling xAI."""

import json

import pytest

from aural.cli import Refusal, assert_adult, execute
from aural.llm import StageError, ask_json
from aural.stages import _validate_outline

OUTLINE = {
    "title": "Warm Room",
    "genre": "meditation",
    "minutes": 5,
    "beats": [
        {"name": "settle", "minutes": 1, "summary": "Breath and shoulders."},
        {"name": "return", "minutes": 1, "summary": "Back to the room."},
    ],
}

DRAFT = {
    "title": "Warm Room",
    "genre": "meditation",
    "minutes": 5,
    "speakers": ["Narrator"],
    "lines": [
        {"speaker": "Narrator", "text": "[slower]Settle into the warm room.[/slower]"},
        {"speaker": "Side", "text": "A second voice the direct pipeline should fold in."},
    ],
}

EDITED = {
    "title": "Warm Room",
    "genre": "meditation",
    "minutes": 5,
    "speakers": ["Narrator", "Side"],
    "lines": [
        {"speaker": "Narrator", "text": "Settle back. [pause:2s] The room is warm."},
        {"speaker": "Side", "text": "You can let that warmth spread."},
    ],
}


def fake_complete(calls):
    def complete(system, user):
        if "You are the planner." in system:
            calls.append("plan")
            return json.dumps(OUTLINE)
        if "You are the writer." in system:
            calls.append("write")
            return json.dumps(DRAFT)
        if "You are the speech editor." in system:
            calls.append("edit")
            return json.dumps(EDITED)
        raise AssertionError(system)

    return complete


def test_direct_run_writes_one_narrator_and_strips_cues_when_plain(tmp_path):
    calls = []
    dest = tmp_path / "script.md"
    path = execute(
        [
            "a warm erotic meditation",
            "--plain",
            "--genre",
            "meditation",
            "--minutes",
            "5",
            "--out",
            str(dest),
        ],
        complete=fake_complete(calls),
    )
    text = path.read_text(encoding="utf-8")
    assert calls == ["plan", "write", "edit"]
    assert path == dest
    assert 'genre: "meditation"' in text
    assert "minutes: 5" in text
    assert 'plain: true' in text
    assert '  - "Narrator"' in text
    assert "Side" not in text
    assert "[pause" not in text
    assert "[slower]" not in text
    assert "Settle back. The room is warm." in text
    assert "You can let that warmth spread." in text
    assert "**Narrator:**" not in text


def test_existing_output_is_not_overwritten(tmp_path):
    dest = tmp_path / "script.md"
    dest.write_text("keep", encoding="utf-8")
    path = execute(
        ["a warm erotic meditation", "--out", str(dest)],
        complete=fake_complete([]),
    )
    assert dest.read_text(encoding="utf-8") == "keep"
    assert path.name == "script-2.md"
    saved = path.read_text(encoding="utf-8")
    assert "Settle back." in saved
    assert "[pause:2s]" in saved


def test_minor_prompt_does_not_call_the_model(tmp_path):
    def complete(system, user):
        raise AssertionError("model was called")

    with pytest.raises(Refusal):
        execute(
            ["an erotic story about a 16 year old", "--out", str(tmp_path / "x.md")],
            complete=complete,
        )


def test_minor_word_in_limits_does_not_call_the_model(tmp_path):
    def complete(system, user):
        raise AssertionError("model was called")

    with pytest.raises(Refusal):
        execute(
            ["a scene between lovers", "--limits", "include a child", "--out", str(tmp_path / "x.md")],
            complete=complete,
        )


def test_adult_wording_is_not_refused():
    assert_adult("You are kidding. A 25 year old waits in the warm room.")


def test_age_of_phrase_is_refused():
    with pytest.raises(Refusal):
        assert_adult("an erotic scene with someone age of 15")


def test_ask_json_retries_once_then_uses_the_second_reply():
    replies = iter(
        [
            "not json",
            json.dumps({"title": "Ok", "beats": [{"summary": "Hi"}]}),
        ]
    )
    seen = []

    def complete(system, user):
        seen.append(user)
        return next(replies)

    data = ask_json(complete, "plan", "You are the planner.", "go", _validate_outline)
    assert data["title"] == "Ok"
    assert "not json" in seen[1]


def test_ask_json_stops_after_the_second_bad_reply():
    def complete(system, user):
        return "still no"

    with pytest.raises(StageError) as caught:
        ask_json(complete, "plan", "You are the planner.", "go", _validate_outline)
    assert caught.value.raw == "still no"
