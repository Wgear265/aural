"""Pipelines by name.

The CLI --pipeline flag looks names up in PIPELINES.
To add a pipeline: make a class with run(brief, complete) in a new file,
import it here, and add one line to the dict.
"""

from aural.pipelines.base import Pipeline
from aural.pipelines.direct import DirectPipeline

PIPELINES: dict[str, type[Pipeline]] = {
    "direct": DirectPipeline,  # prompt -> one narrator (this version)
    # "interview": InterviewPipeline,  # later: ask follow-up questions, then write
    # "cast": CastPipeline,  # later: narrator plus named characters
}


class UnknownPipeline(Exception):
    pass


def get_pipeline(name: str) -> Pipeline:
    try:
        cls = PIPELINES[name]
    except KeyError:
        known = ", ".join(PIPELINES)
        raise UnknownPipeline(
            f"Unknown pipeline {name!r}. Known pipelines: {known}"
        ) from None
    return cls()
