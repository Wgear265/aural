"""Cue tags stay in the normal script and disappear with --plain."""

from aural.cues import strip_cues
from aural.models import Line, Script
from aural.render import render_markdown


def test_strip_known_cue_tags():
    text = (
        "Hello [pause:2s] there. [slower]Come closer.[/slower] "
        "[emphasis]Now[/emphasis] [breath] [whisper]yes[/whisper]."
    )
    assert strip_cues(text) == "Hello there. Come closer. Now yes."


def test_plain_render_strips_cues_and_hides_the_only_speaker():
    script = Script(
        title="Warm Room",
        genre="meditation",
        speakers=["Narrator"],
        lines=[Line("Narrator", "Settle back. [pause:2s] The room is warm.")],
        minutes=5,
        plain=True,
    )
    text = render_markdown(script)
    assert "[pause" not in text
    assert "**Narrator:**" not in text
    assert "Settle back. The room is warm." in text
    assert 'plain: true' in text


def test_render_labels_each_speaker_when_there_are_several():
    script = Script(
        title="Two voices",
        genre="story",
        speakers=["Narrator", "Alex"],
        lines=[
            Line("Narrator", "You hear a knock."),
            Line("Alex", "I brought wine."),
        ],
    )
    text = render_markdown(script)
    assert "**Narrator:** You hear a knock." in text
    assert "**Alex:** I brought wine." in text
