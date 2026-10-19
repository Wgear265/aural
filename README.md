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

The prompt is the only required argument. Every flag below is optional.

### Required

- `prompt` is the quoted text after `aural`. It is the idea the script is written from. Put the scene, the tone, and any detail you care about in this string.

### Optional

- `--plain` turns delivery cues off. The writer is told to use only words a voice should speak, and any bracket tags still left in the script are removed when the file is saved. Leave this flag off when you want cues a later voice step can read. With cues on, the script may contain:
  - `[pause:2s]`
  - `[slower]` ... `[/slower]`
  - `[faster]` ... `[/faster]`
  - `[emphasis]` ... `[/emphasis]`
  - `[whisper]` ... `[/whisper]`
  - `[breath]`
- `--genre story|hypnosis|meditation|custom` picks the shape from `src/aural/genres.py`. `story` is a spoken scene with a beginning, a middle, and an end. `hypnosis` opens with an induction, moves through a deepener and suggestions, and ends with a count-up. `meditation` settles the listener, moves through the body, and brings them back to the room. `custom` follows the prompt, keeps one narrator, and ends clearly. Omit `--genre` and the planner picks one of those four from the prompt.
- `--minutes 15` sets the target length, from 1 to 180. The writer aims for about 140 spoken words per minute. Omit it and a length named in the prompt is used. If the prompt names no length, the target is about 10 minutes. A number passed here replaces a length written in the prompt.
- `--limits "no degradation, no names"` is a boundary written in your own words. There is no fixed list of values. The same sentence is sent to the planner, the writer, and the editor as hard limits they must not cross. Use it for anything that should hold even when the prompt is loose: acts to leave out, names to avoid, a place to stay inside. Omit it and the stages are told the limits are none. This text is checked by the same adult filter as the prompt.
- `--pipeline direct` selects the pipeline. `direct` is the only one implemented, and it is the default. It plans the beats, writes the lines, then edits them for speech.
- `--out output/my-script.md` sets the file path. The default is `output/<title>.md`, using the title the model chooses. If that file already exists, it is left in place and the new script is saved as `my-script-2.md`, then `my-script-3.md`.

```powershell
.\.venv\Scripts\aural.exe "the same idea, as a short story" --plain --minutes 8 --limits "no degradation"
```

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
