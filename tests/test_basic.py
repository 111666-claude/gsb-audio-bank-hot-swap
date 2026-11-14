import unittest

from bank import BankResolver


class BankResolverBasicTests(unittest.TestCase):
    def test_one_sound(self):
        r = BankResolver()
        r.apply({"op": "load", "bank": "base", "generation": 1, "sound": "hit", "locale": "en", "priority": 1, "bytes": 1})
        self.assertEqual(r.resolve("hit", "en", 1), [("base", "en")])


if __name__ == "__main__":
    unittest.main()
