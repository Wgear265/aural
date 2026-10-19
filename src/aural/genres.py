"""How each kind of audio script is shaped.

The planner and the writer both receive the note for the genre on the
brief. Edit the strings here to change the structure without touching
the API call.

When genre is None, the planner is told to infer one from the prompt.
"""

GENRE_NOTES = {
    "story": (
        "Shape: a spoken erotic story with a beginning, a middle, and a finish. "
        "Use second person (you) unless the prompt asks for another point of view. "
        "Stay in one narrator's voice."
    ),
    "hypnosis": (
        "Shape: erotic hypnosis for a listener who chose to press play. "
        "Open with an induction, move into a deepener, give suggestions that "
        "follow the prompt, and end with a count-up that brings the listener "
        "back awake. Use short sentences and repeated images so there is room to pause."
    ),
    "meditation": (
        "Shape: an erotic meditation. Settle the listener, focus on breath or "
        "the body, move into the erotic imagery the prompt asks for, then "
        "bring them back to the room."
    ),
    "custom": (
        "Shape: follow the prompt. It may be a guided scene, affirmations, a "
        "wake-up, or another explicit audio form. Keep a single narrator and "
        "give the piece a clear ending."
    ),
}


def genre_note(genre: str | None) -> str:
    if genre is None:
        return (
            "No genre was chosen. From the prompt, pick one of story, hypnosis, "
            "meditation, or custom, and follow that shape. Put the chosen name "
            "in the genre field."
        )
    try:
        return GENRE_NOTES[genre]
    except KeyError:
        known = ", ".join(GENRE_NOTES)
        raise ValueError(f"Unknown genre {genre!r}. Known genres: {known}") from None
