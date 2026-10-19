"""Delivery cues such as [pause:2s] and [slower].

Cues are notes to a human reader, or to a future TTS adapter that knows
how to map them. Most voice models will speak the brackets aloud, so
--plain strips these tags before the file is saved.

The patterns live here so the writer instructions and the stripper stay
in agreement. Add a new cue in both CUE_PATTERN and CUE_HELP.
"""

import re

# Optional slash so closing tags like [/slower] match too.
# pause may carry a duration: [pause:2s] or [pause:2.5s].
CUE_PATTERN = re.compile(
    r"\[/?pause(?::\s*[\d.]+\s*s)?\]"
    r"|\[/?(?:slower|faster|emphasis|whisper|soft|breath|beat)\]",
    re.IGNORECASE,
)

CUE_HELP = (
    "You may mark delivery with only these cues, inline in the spoken text: "
    "[pause:2s] (you may change the number), [slower]...[/slower], "
    "[faster]...[/faster], [emphasis]...[/emphasis], "
    "[whisper]...[/whisper], [breath]. "
    "Do not invent other brackets. Do not write camera shots or action lines."
)

PLAIN_HELP = (
    "Do not use brackets, cue tags, or stage directions. "
    "Write only the words a voice should speak."
)


def strip_cues(text: str) -> str:
    """Remove cue tags and the extra spaces they leave behind."""
    cleaned = CUE_PATTERN.sub("", text)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\s+([,.!?;:])", r"\1", cleaned)
    return cleaned.strip()
