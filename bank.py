"""Sound-bank selection for a live game client."""


class BankResolver:
    def __init__(self):
        self.entries = []
        self.Work = 0

    def apply(self, event):
        if event["op"] == "load":
            self.entries.append(dict(event))
        elif event["op"] == "unload":
            self.entries = [e for e in self.entries if e["bank"] != event["bank"]]
        else:
            raise ValueError("unknown event")

    def resolve(self, sound, locale, budget):
        selected = []
        for entry in sorted(self.entries, key=lambda e: (e["priority"], e["bank"])):
            self.Work += 1
            if entry["sound"] == sound and entry["locale"] in (locale, "en") and entry["bytes"] <= budget:
                selected.append((entry["bank"], entry["locale"]))
        return selected
