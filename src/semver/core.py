from __future__ import annotations

import re
from functools import total_ordering
from typing import List, Optional, Tuple

# Canonical semver 2.0.0 grammar, taken verbatim from the spec and translated
# into Python's re syntax. Keeping the spec's productions as named groups means
# the parser cannot silently drift from semver's published rules.
_CORE = r"""
    (?P<major>0|[1-9][0-9]*)
    \.
    (?P<minor>0|[1-9][0-9]*)
    \.
    (?P<patch>0|[1-9][0-9]*)
"""
_PRE = r"""
    (?:
        -
        (?P<prerelease>
            (?:0|[1-9][0-9]*|[A-Za-z-][0-9A-Za-z-]*)
            (?:\.(?:0|[1-9][0-9]*|[A-Za-z-][0-9A-Za-z-]*))*
        )
    )?
"""
_BUILD = r"""
    (?:
        \+
        (?P<build>
            [0-9A-Za-z-]+
            (?:\.[0-9A-Za-z-]+)*
        )
    )?
"""
_VERSION_RE = re.compile(
    r"^" + _CORE + _PRE + _BUILD + r"$",
    re.VERBOSE,
)


class InvalidVersion(ValueError):
    """Raised when a string is not a valid semantic version."""


def _split_identifiers(value: str) -> List[object]:
    """Split a dotted identifier string into typed comparison atoms.

    Numeric identifiers become ``int`` so that 10 sorts after 2; textual ones
    stay as ``str``. The tuple ordering then falls out for free from Python's
    rule that ints and strs are not directly comparable, so we wrap each str in
    a 1-tuple and each int in a 0-tuple to give every atom a common, sortable
    shape: ``(kind, payload)``.
    """
    out: List[object] = []
    for part in value.split("."):
        if part.isdigit():
            out.append((0, int(part)))
        else:
            out.append((1, part))
    return out


@total_ordering
class Version:
    """An immutable semantic version.

    Build metadata (the ``+`` segment) is parsed and preserved but never
    participates in ordering, per semver 2.0.0 §10. A version with no
    prerelease is greater than any version of the same core that has one.
    """

    __slots__ = ("major", "minor", "patch", "prerelease", "_build", "_str")

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        prerelease: str = "",
        build: str = "",
    ) -> None:
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self._build = build
        self._str = self._render()

    @classmethod
    def parse(cls, text: str) -> "Version":
        m = _VERSION_RE.match(text)
        if m is None:
            raise InvalidVersion(f"not a semantic version: {text!r}")
        return cls(
            int(m["major"]),
            int(m["minor"]),
            int(m["patch"]),
            m["prerelease"] or "",
            m["build"] or "",
        )

    def _render(self) -> str:
        s = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            s += "-" + self.prerelease
        if self._build:
            s += "+" + self._build
        return s

    def __str__(self) -> str:
        return self._str

    def __repr__(self) -> str:
        return f"Version({self._str!r})"

    def _cmp_key(self) -> Tuple[object, ...]:
        # A version with NO prerelease sorts ABOVE one with a prerelease.
        # Represented here as (1, ()) > (0, <prerelease atoms>).
        if self.prerelease:
            pre = (0, tuple(_split_identifiers(self.prerelease)))
        else:
            pre = (1, ())
        return (self.major, self.minor, self.patch, pre)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() == other._cmp_key()

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Version):
            return NotImplemented
        return self._cmp_key() < other._cmp_key()

    def __hash__(self) -> int:
        # Hash by the comparison key so equal versions hash equally, even when
        # their build metadata strings differ.
        return hash(self._cmp_key())

    def bump_major(self) -> "Version":
        return Version(self.major + 1, 0, 0)

    def bump_minor(self) -> "Version":
        return Version(self.major, self.minor + 1, 0)

    def bump_patch(self) -> "Version":
        return Version(self.major, self.minor, self.patch + 1)

    @property
    def build(self) -> str:
        return self._build


def bump_major(v: Version) -> Version:
    return v.bump_major()


def bump_minor(v: Version) -> Version:
    return v.bump_minor()


def bump_patch(v: Version) -> Version:
    return v.bump_patch()
