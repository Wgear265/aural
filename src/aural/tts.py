"""Hook for a later text-to-speech engine.

This version only writes a script file. When you choose an explicit or
open-source voice model, implement SpeechEngine and call it from the CLI
after save_script().

Pass --plain when the engine would otherwise read bracket tags aloud.
An engine that understands its own pause markup can take the cue version
and translate tags such as [pause:2s] inside synthesize().
"""

from pathlib import Path

from aural.models import Script


class SpeechEngine:
    """One method. dest is the audio file you want the engine to create."""

    def synthesize(self, script: Script, dest: Path) -> Path:
        raise NotImplementedError("No voice engine is connected yet.")
