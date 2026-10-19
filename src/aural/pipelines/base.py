"""What every pipeline implements.

run() receives the brief from the CLI and a complete function.
complete(system_text, user_text) returns the model's reply as text.
The real one is llm.live_complete. Tests pass a fake.
"""


class Pipeline:
    name = "base"
    description = ""

    def run(self, brief, complete):
        raise NotImplementedError
