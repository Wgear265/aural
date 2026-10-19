# Aural

Aural turns a prompt into an adult erotic script for audio. You get a Markdown file with one narrator. A later voice engine can read that file. This version does not generate audio.

Every character, and the listener the script addresses, is an adult. Before any API call, the CLI refuses a prompt that names a minor or an age under 18. The check is a word list, so a phrase like "a minor detail" is refused too. Rephrase, or edit the list in `src/aural/cli.py`.

## Setup

From this folder, in PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Open `.env` and paste your key from the [xAI console](https://console.x.ai). The quickstart is at [docs.x.ai](https://docs.x.ai/developers/quickstart). `XAI_API_KEY` is the secret the program sends with each request. `AURAL_MODEL` is the model name. It defaults to `grok-4.7`.

## Generate a script

```powershell
.\.venv\Scripts\aural.exe "a 10 minute erotic hypnosis about falling asleep in a warm room"
```

That runs the `direct` pipeline: plan the beats, write the lines, then edit them so they are easy to say. It makes three API calls and writes `output/<title>.md`.

```powershell
.\.venv\Scripts\aural.exe "the same idea, as a short story" --plain --minutes 8
```

`--plain` leaves out delivery cues, so a TTS engine will not read brackets aloud. Without `--plain`, the script may contain:

- `[pause:2s]`
- `[slower]` ... `[/slower]`
- `[faster]` ... `[/faster]`
- `[emphasis]` ... `[/emphasis]`
- `[whisper]` ... `[/whisper]`
- `[breath]`

Other flags:

- `--genre story|hypnosis|meditation|custom` sets the shape. Omit it and the planner infers one.
- `--minutes 15` sets the target length (about 140 spoken words per minute).
- `--limits "no degradation"` is added to the instructions for that run.
- `--pipeline direct` picks the pipeline. `direct` is the only one implemented.
- `--out output/my-script.md` sets the file path. An existing file is left in place and a new name is used.

One speaker is written as plain paragraphs. The name Narrator is only in the header, so a voice engine does not say it. A script with two or more speakers labels each paragraph. Nothing in this version produces that yet.

## Where to change things

| You want to | Open |
| --- | --- |
| Change the model or the API key | `.env` and `src/aural/config.py` |
| See the actual xAI call | `src/aural/llm.py` |
| Change story, hypnosis, meditation, or custom | `src/aural/genres.py` |
| Change the cue tags | `src/aural/cues.py` |
| Change what each stage asks for | `src/aural/stages.py` |
| See the three steps of a run | `src/aural/pipelines/direct.py` |
| Add a pipeline | a new file in `src/aural/pipelines/`, then one line in `registry.py` |
| Connect a voice engine later | `src/aural/tts.py` |
| Change which prompts are refused locally | `src/aural/cli.py` (`assert_adult`) |

`registry.py` already has commented slots for an interview pipeline (ask follow-up questions, then write) and a cast pipeline (narrator plus characters). The script model stores a speaker on every line, so those can be added without changing the file format.

## Tests

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The tests use a fake reply function. They do not call xAI and do not spend credit.
