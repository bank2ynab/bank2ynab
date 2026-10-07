"""Unit tests for bump-and-tag version logic (mirrors workflow inline Python)."""



def bump_version(current: str, bump_type: str) -> str:
    """Increment a semver string by bump_type (patch/minor/major)."""
    major, minor, patch = (int(x) for x in current.split("."))
    if bump_type == "major":
        return f"{major + 1}.0.0"
    if bump_type == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def resolve_bump_type(labels: list[str]) -> str:
    """Return the highest release bump type from a list of label names."""
    for level in ("major", "minor", "patch"):
        if f"release: {level}" in labels:
            return level
    return "patch"


class TestBumpVersion:
    def test_patch_bump(self):
        assert bump_version("1.2.3", "patch") == "1.2.4"

    def test_minor_bump(self):
        assert bump_version("1.2.3", "minor") == "1.3.0"

    def test_major_bump(self):
        assert bump_version("1.2.3", "major") == "2.0.0"

    def test_patch_resets_nothing(self):
        assert bump_version("1.2.9", "patch") == "1.2.10"

    def test_minor_zeros_patch(self):
        assert bump_version("1.2.3", "minor") == "1.3.0"

    def test_major_zeros_minor_and_patch(self):
        assert bump_version("1.2.3", "major") == "2.0.0"

    def test_from_zero_minor(self):
        assert bump_version("1.0.0", "patch") == "1.0.1"


class TestResolveBumpType:
    def test_no_release_labels_defaults_to_patch(self):
        assert resolve_bump_type([]) == "patch"

    def test_patch_label(self):
        assert resolve_bump_type(["release: patch"]) == "patch"

    def test_minor_label(self):
        assert resolve_bump_type(["release: minor"]) == "minor"

    def test_major_label(self):
        assert resolve_bump_type(["release: major"]) == "major"

    def test_major_wins_over_minor(self):
        assert resolve_bump_type(["release: minor", "release: major"]) == "major"

    def test_major_wins_over_patch(self):
        assert resolve_bump_type(["release: patch", "release: major"]) == "major"

    def test_minor_wins_over_patch(self):
        assert resolve_bump_type(["release: patch", "release: minor"]) == "minor"

    def test_unrelated_labels_ignored(self):
        assert resolve_bump_type(["bug", "enhancement"]) == "patch"

    def test_mixed_labels(self):
        assert resolve_bump_type(["bug", "release: minor", "AFK"]) == "minor"
