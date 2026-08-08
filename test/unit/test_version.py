import re
import importlib.metadata

import pytest


def test_version_is_semver():
    try:
        importlib.metadata.version("bank2ynab")
    except importlib.metadata.PackageNotFoundError:
        pytest.skip("package not installed; run pip install -e . to enable")

    import bank2ynab

    assert bank2ynab.__version__ != "unknown", "__version__ should be set when package is installed"
    assert re.match(
        r"^\d+\.\d+\.\d+$", bank2ynab.__version__
    ), f"__version__ should be semver, got {bank2ynab.__version__!r}"
