# semver

A small, zero-dependency semantic version parser, comparator, and sorter for Python 3.8+. Implements Semantic Versioning 2.0.0.

## Usage

```python
from semver import Version, bump_major, bump_minor, bump_patch

v = Version.parse("1.2.3-rc.1+build.42")
assert v.major == 1
assert v.minor == 2
assert v.patch == 3
assert v.prerelease == "rc.1"
assert v.build == "build.42"

# Ordering follows semver precedence rules.
assert Version.parse("1.0.0-alpha") < Version.parse("1.0.0")
assert Version.parse("1.0.0-alpha") < Version.parse("1.0.0-alpha.1")
assert Version.parse("1.0.0-rc.1") < Version.parse("1.0.0-rc.2")
assert Version.parse("1.0.0-2") < Version.parse("1.0.0-10")  # numeric, not lexical

# Build metadata is ignored when comparing.
assert Version.parse("1.0.0+a") == Version.parse("1.0.0+b")

# Sorted works directly on Version instances.
ordered = sorted([Version.parse("2.0.0"), Version.parse("1.0.0")])
assert ordered[0] == Version.parse("1.0.0")

# Bump helpers drop prerelease and build, returning a new Version.
assert str(bump_major(v)) == "2.0.0"
assert str(bump_minor(v)) == "1.3.0"
assert str(bump_patch(v)) == "1.2.4"
```

## Why

The Python ecosystem has a few semver libraries, most of which pull in optional dependencies or grow toward range-matching syntax (`^`, `~`, `>=`). This one does exactly three things and stops: parse a version string, compare two versions by semver precedence, and sort a list of them. No ranges, no constraint resolution, no `requirements.txt` hooks. The trade-off is a smaller surface area that is easy to read end-to-end and easy to audit.

## Exports

- `Version` — immutable version type. Construct with `Version(major, minor, patch, prerelease="", build="")` or parse via `Version.parse(text)`.
- `Version.parse(text)` — returns a `Version`, raises `semver.core.InvalidVersion` (a `ValueError` subclass) on malformed input.
- `bump_major(v)`, `bump_minor(v)`, `bump_patch(v)` — return a new `Version` with the given field incremented and all lower fields (plus prerelease/build) cleared.

## Edge you will hit

Prerelease comparison is the one place semver gets fiddly. Numeric identifiers compare numerically (so `1.0.0-2` < `1.0.0-10`), textual ones compare lexically, and numeric identifiers always sort below textual ones at the same position (`1.0.0-1` < `1.0.0-alpha`). A version with no prerelease is always greater than one with a prerelease at the same `major.minor.patch`. Build metadata (`+...`) is parsed and kept on the string form but never affects comparison or hashing.

## Running tests

```
PYTHONPATH=src python -m unittest discover -s tests
```
