import os
import time

import pytest
import requests


BASE_URL = os.getenv("AZURE_WEBAPP_URL", "").rstrip("/")
HEALTH_PATH = os.getenv("AZURE_WEBAPP_HEALTH_PATH", "/")
READY_TIMEOUT_SECONDS = int(os.getenv("AZURE_WEBAPP_READY_TIMEOUT", "60"))
POLL_INTERVAL_SECONDS = float(os.getenv("AZURE_WEBAPP_POLL_INTERVAL", "2"))


@pytest.fixture(scope="session")
def app_url() -> str:
    if not BASE_URL:
        pytest.skip("Set AZURE_WEBAPP_URL to run Azure Web App tests")
    return f"{BASE_URL}{HEALTH_PATH}"


def wait_until_ready(url: str, timeout_seconds: int) -> requests.Response:
    """Poll a URL until it returns a non-5xx status or timeout."""
    deadline = time.time() + timeout_seconds
    last_response = None

    while time.time() < deadline:
        try:
            response = requests.get(url, timeout=10)
            last_response = response
            if response.status_code < 500:
                return response
        except requests.RequestException:
            pass

        time.sleep(POLL_INTERVAL_SECONDS)

    if last_response is not None:
        return last_response

    raise AssertionError(f"{url} did not respond within {timeout_seconds} seconds")


def test_webapp_is_reachable(app_url: str) -> None:
    response = wait_until_ready(app_url, READY_TIMEOUT_SECONDS)
    assert response.status_code < 500, (
        f"Expected non-5xx response from {app_url}, got {response.status_code}"
    )


def test_webapp_returns_expected_content_type(app_url: str) -> None:
    response = requests.get(app_url, timeout=10)
    assert response.status_code < 500

    content_type = response.headers.get("Content-Type", "")
    assert content_type, "Response did not include Content-Type header"


def test_webapp_response_time_under_threshold(app_url: str) -> None:
    start = time.perf_counter()
    response = requests.get(app_url, timeout=10)
    elapsed = time.perf_counter() - start

    assert response.status_code < 500
    assert elapsed < 2.0, f"Expected response under 2.0s, got {elapsed:.3f}s"
