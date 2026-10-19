"""The first pipeline: one prompt in, one narrator script out.

run() is the whole agent workflow:
1. plan() asks for a beat sheet
2. write() drafts the spoken lines
3. edit_for_speech() rewrites them for the ear

A later pipeline can do its own setup, then call the same three functions.
"""

from aural.models import Line, Script
from aural.pipelines.base import Pipeline
from aural.stages import edit_for_speech, plan, write


class DirectPipeline(Pipeline):
    name = "direct"
    description = "Turn one prompt into a single-narrator script."

    def run(self, brief, complete) -> Script:
        print("Planning the beats...")
        outline = plan(complete, brief)
        print("Writing the script...")
        draft = write(complete, brief, outline)
        print("Editing for speech...")
        final = edit_for_speech(complete, brief, draft)
        # The direct pipeline promises one voice, even if a stage adds names.
        script = as_single_narrator(final)
        script.genre = brief.genre or outline.get("genre") or script.genre
        script.minutes = brief.minutes or _as_int(outline.get("minutes")) or script.minutes
        script.plain = brief.plain
        if not script.title or script.title == "Untitled":
            title = outline.get("title")
            if title:
                script.title = " ".join(str(title).split())
        return script


def as_single_narrator(script: Script) -> Script:
    script.speakers = ["Narrator"]
    script.lines = [Line("Narrator", line.text) for line in script.lines]
    return script


def _as_int(value):
    if value is None or value == "":
        return None
    return int(value)
