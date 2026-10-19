"""Turn a Script into a Markdown file.

A single speaker is written as bare paragraphs, so a TTS engine does not
say the name "Narrator". When a script has two or more speakers, each
paragraph is labeled. That path is unused by the direct pipeline and is
here for a later cast pipeline.

--plain strips cue tags at save time, even if the model left some in.
"""

import re
from pathlib import Path

from aural.cues import strip_cues
from aural.models import Script


def save_script(script: Script, dest: Path | None) -> Path:
    path = unique_path(dest or default_output_path(script))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_markdown(script), encoding="utf-8")
    return path


def default_output_path(script: Script) -> Path:
    return Path("output") / f"{slugify(script.title)}.md"


def render_markdown(script: Script) -> str:
    header = [
        "---",
        f"title: {yaml_quote(script.title)}",
        f"genre: {yaml_quote(script.genre)}",
    ]
    if script.minutes is not None:
        header.append(f"minutes: {script.minutes}")
    header.append(f"plain: {'true' if script.plain else 'false'}")
    header.append(f"words: {spoken_word_count(script)}")
    header.append("speakers:")
    for speaker in script.speakers:
        header.append(f"  - {yaml_quote(speaker)}")
    header.append("---")

    show_names = len(script.speakers) > 1
    paragraphs: list[str] = []
    for line in script.lines:
        text = strip_cues(line.text) if script.plain else line.text.strip()
        if not text:
            continue
        if show_names:
            paragraphs.append(f"**{line.speaker}:** {text}")
        else:
            paragraphs.append(text)

    body = "\n\n".join(paragraphs)
    return "\n".join(header) + "\n\n" + body + "\n"


def spoken_word_count(script: Script) -> int:
    """Count words the listener would hear, with cue tags removed."""
    text = " ".join(strip_cues(line.text) for line in script.lines)
    return len(text.split())


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug[:60] or "script"


def unique_path(path: Path) -> Path:
    """If path exists, use name-2, name-3, and so on."""
    if not path.exists():
        return path
    for number in range(2, 1000):
        candidate = path.with_name(f"{path.stem}-{number}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise FileExistsError(path)


def yaml_quote(value: str) -> str:
    """Quote a header value so a colon in a title does not break the file."""
    text = " ".join(value.split())
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'
