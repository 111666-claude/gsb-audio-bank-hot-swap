"""Sound-bank selection for a live game client."""


class BankResolver:
    def __init__(self):
        self._by_sound = {}   # sound -> [entry, ...] (live entries only)
        self._by_bank = {}    # bank -> [entry, ...]
        self._gens = {}       # bank -> current generation
        self.Work = 0

    def apply(self, event):
        op = event["op"]
        if op == "load":
            bank = event["bank"]
            gen = event["generation"]
            current = self._gens.get(bank)
            if current is not None:
                if gen < current:
                    return  # stale generation arrived late; ignore it
                if gen > current:
                    self._evict_bank(bank)  # newer generation replaces the old
            self._gens[bank] = gen
            entry = dict(event)
            self._by_sound.setdefault(entry["sound"], []).append(entry)
            self._by_bank.setdefault(bank, []).append(entry)
        elif op == "unload":
            bank = event["bank"]
            current = self._gens.get(bank)
            if current is None:
                return
            gen = event.get("generation")
            if gen is not None and gen < current:
                return  # expired unload must not evict a newer generation
            self._evict_bank(bank)
            del self._gens[bank]
        else:
            raise ValueError("unknown event")

    def _evict_bank(self, bank):
        for entry in self._by_bank.pop(bank, ()):
            entries = self._by_sound.get(entry["sound"])
            if entries is None:
                continue
            entries.remove(entry)
            if not entries:
                del self._by_sound[entry["sound"]]

    def resolve(self, sound, locale, budget):
        exact = []
        fallback = []
        for entry in self._by_sound.get(sound, ()):
            self.Work += 1
            if entry["locale"] == locale:
                exact.append(entry)
            elif entry["locale"] == "en":
                fallback.append(entry)
        # English fallback only when the target locale has no variant.
        candidates = exact if exact else fallback
        candidates.sort(key=lambda e: (-e["priority"], e["bank"]))
        selected = []
        remaining = budget
        for entry in candidates:
            if entry["bytes"] <= remaining:
                selected.append((entry["bank"], entry["locale"]))
                remaining -= entry["bytes"]
        return selected
