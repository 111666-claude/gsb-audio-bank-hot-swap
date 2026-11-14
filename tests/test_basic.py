import unittest

from bank import BankResolver


def load(bank, generation, sound, locale, priority, bytes_):
    return {"op": "load", "bank": bank, "generation": generation,
            "sound": sound, "locale": locale, "priority": priority,
            "bytes": bytes_}


class BankResolverBasicTests(unittest.TestCase):
    def test_one_sound(self):
        r = BankResolver()
        r.apply(load("base", 1, "hit", "en", 1, 1))
        self.assertEqual(r.resolve("hit", "en", 1), [("base", "en")])


class GenerationTests(unittest.TestCase):
    def test_stale_load_after_newer_generation_is_ignored(self):
        r = BankResolver()
        r.apply(load("pack", 2, "hit", "en", 1, 1))
        r.apply(load("pack", 1, "hit", "en", 9, 1))  # late, older generation
        self.assertEqual(r.resolve("hit", "en", 10), [("pack", "en")])

    def test_newer_generation_replaces_older(self):
        r = BankResolver()
        r.apply(load("pack", 1, "hit", "en", 1, 1))
        r.apply(load("pack", 2, "hit", "en", 1, 1))
        self.assertEqual(r.resolve("hit", "en", 10), [("pack", "en")])

    def test_expired_unload_does_not_evict_newer_generation(self):
        r = BankResolver()
        r.apply(load("pack", 1, "hit", "en", 1, 1))
        r.apply(load("pack", 2, "hit", "en", 1, 1))
        r.apply({"op": "unload", "bank": "pack", "generation": 1})
        self.assertEqual(r.resolve("hit", "en", 10), [("pack", "en")])

    def test_unload_of_current_generation_removes_bank(self):
        r = BankResolver()
        r.apply(load("pack", 2, "hit", "en", 1, 1))
        r.apply({"op": "unload", "bank": "pack", "generation": 2})
        self.assertEqual(r.resolve("hit", "en", 10), [])


class LocaleTests(unittest.TestCase):
    def test_exact_locale_excludes_english_fallback(self):
        r = BankResolver()
        r.apply(load("loc", 1, "hit", "fr", 1, 1))
        r.apply(load("base", 1, "hit", "en", 9, 1))
        self.assertEqual(r.resolve("hit", "fr", 10), [("loc", "fr")])

    def test_english_fallback_when_locale_missing(self):
        r = BankResolver()
        r.apply(load("base", 1, "hit", "en", 1, 1))
        self.assertEqual(r.resolve("hit", "fr", 10), [("base", "en")])


class BudgetAndOrderTests(unittest.TestCase):
    def test_shared_remaining_budget_no_partial_variant(self):
        r = BankResolver()
        r.apply(load("a", 1, "hit", "en", 3, 4))
        r.apply(load("b", 1, "hit", "en", 2, 4))
        r.apply(load("c", 1, "hit", "en", 1, 4))
        # budget 9 fits two 4-byte variants, not three
        self.assertEqual(r.resolve("hit", "en", 9), [("a", "en"), ("b", "en")])

    def test_higher_priority_first_then_bank_id(self):
        r = BankResolver()
        r.apply(load("zeta", 1, "hit", "en", 5, 1))
        r.apply(load("alpha", 1, "hit", "en", 5, 1))
        r.apply(load("mid", 1, "hit", "en", 7, 1))
        self.assertEqual(
            r.resolve("hit", "en", 10),
            [("mid", "en"), ("alpha", "en"), ("zeta", "en")],
        )


class WorkTests(unittest.TestCase):
    def test_unrelated_history_does_not_inflate_work(self):
        r = BankResolver()
        for i in range(3000):
            r.apply(load(f"bank{i}", 1, f"noise{i}", "en", 1, 1))
        for i in range(30):
            r.apply(load(f"hot{i}", 1, "hit", "en", i, 1))
        for _ in range(200):
            r.resolve("hit", "en", 100)
        self.assertLessEqual(r.Work, 6000)

    def test_basic_lookup_still_works_after_history(self):
        r = BankResolver()
        for i in range(3000):
            r.apply(load(f"bank{i}", 1, f"noise{i}", "en", 1, 1))
        r.apply(load("base", 1, "hit", "en", 1, 1))
        self.assertEqual(r.resolve("hit", "en", 1), [("base", "en")])


if __name__ == "__main__":
    unittest.main()
