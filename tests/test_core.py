import unittest

from semver import Version, bump_major, bump_minor, bump_patch
from semver.core import InvalidVersion


class ParseTests(unittest.TestCase):
    def test_basic(self):
        v = Version.parse("1.2.3")
        self.assertEqual((v.major, v.minor, v.patch), (1, 2, 3))
        self.assertEqual(v.prerelease, "")
        self.assertEqual(v.build, "")

    def test_prerelease(self):
        v = Version.parse("1.0.0-alpha.1")
        self.assertEqual(v.prerelease, "alpha.1")
        self.assertEqual(v.build, "")

    def test_build(self):
        v = Version.parse("1.0.0+exp.sha.5114f85")
        self.assertEqual(v.build, "exp.sha.5114f85")
        self.assertEqual(v.prerelease, "")

    def test_prerelease_and_build(self):
        v = Version.parse("1.0.0-beta+002")
        self.assertEqual(v.prerelease, "beta")
        self.assertEqual(v.build, "002")

    def test_roundtrip(self):
        for s in ["0.0.0", "10.20.30", "1.2.3-rc.0", "1.2.3+x.7.z"]:
            self.assertEqual(str(Version.parse(s)), s)

    def test_rejects_leading_zero_major(self):
        with self.assertRaises(InvalidVersion):
            Version.parse("01.2.3")

    def test_rejects_leading_zero_minor(self):
        with self.assertRaises(InvalidVersion):
            Version.parse("1.02.3")

    def test_rejects_missing_patch(self):
        with self.assertRaises(InvalidVersion):
            Version.parse("1.2")

    def test_rejects_empty_prerelease(self):
        with self.assertRaises(InvalidVersion):
            Version.parse("1.0.0-")

    def test_rejects_empty_build(self):
        with self.assertRaises(InvalidVersion):
            Version.parse("1.0.0+")

    def test_rejects_garbage(self):
        with self.assertRaises(InvalidVersion):
            Version.parse("not a version")

    def test_rejects_plain(self):
        with self.assertRaises(InvalidVersion):
            Version.parse("1")


class CompareTests(unittest.TestCase):
    def test_equal(self):
        self.assertEqual(Version.parse("1.0.0"), Version.parse("1.0.0"))

    def test_unequal(self):
        self.assertNotEqual(Version.parse("1.0.0"), Version.parse("2.0.0"))

    def test_major(self):
        self.assertLess(Version.parse("1.9.9"), Version.parse("2.0.0"))

    def test_minor(self):
        self.assertLess(Version.parse("1.1.9"), Version.parse("1.2.0"))

    def test_patch(self):
        self.assertLess(Version.parse("1.1.1"), Version.parse("1.1.2"))

    def test_release_beats_prerelease(self):
        self.assertGreater(Version.parse("1.0.0"), Version.parse("1.0.0-rc.1"))

    def test_prerelease_order_text(self):
        self.assertLess(Version.parse("1.0.0-alpha"), Version.parse("1.0.0-beta"))

    def test_prerelease_order_numeric(self):
        # 2 must sort before 10 numerically, not lexicographically.
        self.assertLess(Version.parse("1.0.0-2"), Version.parse("1.0.0-10"))

    def test_prerelease_dotted(self):
        self.assertLess(Version.parse("1.0.0-alpha.1"), Version.parse("1.0.0-alpha.2"))

    def test_numeric_before_text(self):
        # Per spec, numeric identifiers have lower precedence than textual ones.
        self.assertLess(Version.parse("1.0.0-1"), Version.parse("1.0.0-alpha"))

    def test_shorter_prerelease_lower(self):
        self.assertLess(
            Version.parse("1.0.0-alpha"), Version.parse("1.0.0-alpha.1")
        )

    def test_build_ignored_for_order(self):
        a = Version.parse("1.0.0+x")
        b = Version.parse("1.0.0+y")
        self.assertEqual(a, b)
        self.assertFalse(a < b)
        self.assertFalse(a > b)

    def test_build_kept_on_string(self):
        self.assertEqual(str(Version.parse("1.0.0+sha")), "1.0.0+sha")

    def test_hash_equal_for_same_precedence(self):
        a = Version.parse("1.0.0+sha")
        b = Version.parse("1.0.0+other")
        self.assertEqual(hash(a), hash(b))

    def test_sort_list(self):
        versions = [
            Version.parse("1.0.0"),
            Version.parse("1.0.0-rc.1"),
            Version.parse("1.0.0-rc.2"),
            Version.parse("1.0.0-alpha"),
            Version.parse("0.9.0"),
        ]
        got = [str(v) for v in sorted(versions)]
        self.assertEqual(
            got,
            ["0.9.0", "1.0.0-alpha", "1.0.0-rc.1", "1.0.0-rc.2", "1.0.0"],
        )

    def test_max(self):
        v = max(Version.parse("1.0.0"), Version.parse("2.0.0"))
        self.assertEqual(v, Version.parse("2.0.0"))


class BumpTests(unittest.TestCase):
    def test_bump_major_zeroes_rest(self):
        v = Version.parse("1.2.3-rc+build")
        self.assertEqual(str(bump_major(v)), "2.0.0")

    def test_bump_minor_zeroes_patch(self):
        v = Version.parse("1.2.3-rc+build")
        self.assertEqual(str(bump_minor(v)), "1.3.0")

    def test_bump_patch(self):
        v = Version.parse("1.2.3-rc+build")
        self.assertEqual(str(bump_patch(v)), "1.2.4")

    def test_bump_does_not_mutate(self):
        v = Version.parse("1.2.3")
        bump_major(v)
        self.assertEqual(str(v), "1.2.3")


if __name__ == "__main__":
    unittest.main()
