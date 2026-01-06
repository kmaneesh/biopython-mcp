import os

import pytest


def _is_truthy_env(name: str) -> bool:
    value = os.getenv(name, "").strip().lower()
    return value in {"1", "true", "yes", "on"}


def pytest_runtest_setup(item: pytest.Item) -> None:
    # Opt-in network tests to avoid CI flakiness/rate limits.
    if item.get_closest_marker("network") and not _is_truthy_env("RUN_NETWORK_TESTS"):
        pytest.skip("Network tests disabled (set RUN_NETWORK_TESTS=1 to enable)")

    if item.get_closest_marker("entrez"):
        if not _is_truthy_env("RUN_ENTREZ_TESTS"):
            pytest.skip("Entrez tests disabled (set RUN_ENTREZ_TESTS=1 to enable)")
        if not os.getenv("NCBI_EMAIL"):
            pytest.skip("NCBI_EMAIL not set (required for Entrez tests)")
