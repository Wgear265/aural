"""The objects passed between the CLI, the pipelines, and the file writer.

A Brief is the input. A Script is the output. A Line is one stretch of
speech from one speaker. The direct pipeline only uses Narrator, but
Line.speaker is here so a later multi-voice pipeline can fill it in.
"""

from dataclasses import dataclass, field


@dataclass
class Brief:
    prompt: str
    genre: str | None = None
    minutes: int | None = None
    limits: str | None = None
    plain: bool = False
    pipeline: str = "direct"


@dataclass
class Line:
    speaker: str
    text: str


@dataclass
class Script:
    title: str
    genre: str
    speakers: list[str]
    lines: list[Line] = field(default_factory=list)
    minutes: int | None = None
    plain: bool = False

    def to_dict(self) -> dict:
        """JSON-shaped copy used when one stage hands a script to the next."""
        return {
            "title": self.title,
            "genre": self.genre,
            "minutes": self.minutes,
            "speakers": list(self.speakers),
            "lines": [
                {"speaker": line.speaker, "text": line.text} for line in self.lines
            ],
        }

    @classmethod
    def from_data(cls, data: dict, brief: Brief) -> "Script":
        """Build a Script from a model's JSON object.

        Raises KeyError or TypeError when the shape is wrong so the caller
        can retry the stage once.
        """
        if not isinstance(data, dict):
            raise TypeError("script JSON must be an object")
        raw_lines = data["lines"]
        if not isinstance(raw_lines, list) or not raw_lines:
            raise KeyError("lines")

        lines: list[Line] = []
        for item in raw_lines:
            if isinstance(item, str):
                speaker, text = "Narrator", item
            elif isinstance(item, dict):
                speaker = str(item.get("speaker") or "Narrator")
                text = item["text"]
            else:
                raise TypeError("each line must be a string or an object")
            text = " ".join(str(text).split())
            if text:
                lines.append(Line(speaker=speaker, text=text))
        if not lines:
            raise KeyError("lines")

        raw_speakers = data.get("speakers") or []
        if isinstance(raw_speakers, list) and raw_speakers:
            speakers = [str(name) for name in raw_speakers]
        else:
            speakers = list(dict.fromkeys(line.speaker for line in lines))

        title = " ".join(str(data.get("title") or "Untitled").split()) or "Untitled"
        genre = str(data.get("genre") or brief.genre or "custom")
        return cls(
            title=title,
            genre=genre,
            speakers=speakers,
            lines=lines,
            minutes=_as_minutes(data.get("minutes"), brief.minutes),
            plain=brief.plain,
        )


def _as_minutes(value, fallback: int | None) -> int | None:
    if value is None or value == "":
        return fallback
    return int(value)
