"""Command line entry.

Example:
    aural "a 10 minute erotic hypnosis about a warm room"
    aural "the same idea" --plain

execute() is split from main() so tests can pass a fake complete function
and skip the network. The adult check runs before complete() is called.
"""

import argparse
import re
import sys
from pathlib import Path

from aural.config import ConfigError
from aural.genres import GENRE_NOTES
from aural.llm import StageError, live_complete
from aural.models import Brief
from aural.pipelines.registry import PIPELINES, UnknownPipeline, get_pipeline
from aural.render import save_script

# This project writes sexual scripts, so the check is about age, not about sex.
# It is a word list plus ages written with digits. "kid" does not match "kidding".
# "teen" is not listed: 18- and 19-year-olds are teens, and they are adults.
# An age under 18 written as digits is caught by _AGE_RE ("16 year old", "age of 15").
# Add a word here if you want it refused before any API call.
_MINOR_RE = re.compile(
    r"\b("
    r"children|child|kids|kid|underage|pre-?teens?|toddlers?|infants?|"
    r"lolitas?|lolis?|loli|shotas?|shota|jailbait|"
    r"pedophilia|pedophiles?|paedophiles?|pedos?|paedos?|"
    r"prepubescent|middle school|elementary school|grade school|"
    r"minors?"
    r")\b",
    re.IGNORECASE,
)
_AGE_RE = re.compile(
    r"\b(?:aged|age)(?:\s+of)?\s+(?P<age>\d{1,2})\b"
    r"|\b(?P<age2>\d{1,2})\s*[- ]?(?:year|yr)s?\s*[- ]?old\b"
    r"|\b(?P<age3>\d{1,2})\s*[- ]?(?:yo|y/o)\b",
    re.IGNORECASE,
)


class Refusal(Exception):
    """The prompt is out of bounds, so no model call is made."""

    def __init__(self, term: str):
        self.term = term
        super().__init__(
            "This project only writes scripts about adults. "
            f"The prompt matched {term!r}, so nothing was sent to the model."
        )


def find_minor_term(text: str) -> str | None:
    match = _MINOR_RE.search(text)
    if match:
        return match.group(0)
    for match in _AGE_RE.finditer(text):
        digits = next(group for group in match.groups() if group is not None)
        if int(digits) < 18:
            return match.group(0)
    return None


def assert_adult(*parts: str) -> None:
    for part in parts:
        term = find_minor_term(part or "")
        if term:
            raise Refusal(term)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="aural",
        description="Write an adult erotic audio script from a prompt.",
    )
    parser.add_argument("prompt", help="What the script should be")
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Leave out delivery cues so the file can go straight into TTS",
    )
    parser.add_argument(
        "--genre",
        choices=list(GENRE_NOTES),
        help="story, hypnosis, meditation, or custom. Default: infer from the prompt",
    )
    parser.add_argument(
        "--minutes",
        type=int,
        help="Target length. Default: a length named in the prompt, otherwise about 10",
    )
    parser.add_argument(
        "--limits",
        help="Hard limits for this run, for example: no degradation",
    )
    parser.add_argument(
        "--pipeline",
        default="direct",
        choices=list(PIPELINES),
        help="Which pipeline to run. Default: direct",
    )
    parser.add_argument(
        "--out",
        help="Output file. Default: output/<title>.md",
    )
    args = parser.parse_args(argv)
    if args.minutes is not None and not 1 <= args.minutes <= 180:
        parser.error("--minutes must be from 1 to 180")
    return args


def execute(argv: list[str] | None = None, complete=None) -> Path:
    """Build a brief, run the pipeline, and save the script.

    Pass complete(system, user) -> str to avoid the network. The default
    calls xAI through llm.live_complete.
    """
    args = parse_args(argv)
    assert_adult(args.prompt, args.limits or "")
    brief = Brief(
        prompt=args.prompt,
        genre=args.genre,
        minutes=args.minutes,
        limits=args.limits,
        plain=args.plain,
        pipeline=args.pipeline,
    )
    pipeline = get_pipeline(args.pipeline)
    script = pipeline.run(brief, complete or live_complete)
    dest = Path(args.out) if args.out else None
    return save_script(script, dest)


def main(argv: list[str] | None = None) -> int:
    try:
        path = execute(argv)
    except Refusal as exc:
        print(exc, file=sys.stderr)
        return 1
    except StageError as exc:
        print(exc, file=sys.stderr)
        print(exc.raw, file=sys.stderr)
        return 1
    except (ConfigError, UnknownPipeline) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
