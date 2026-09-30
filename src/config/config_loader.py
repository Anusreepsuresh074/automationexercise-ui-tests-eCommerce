import os
from dataclasses import dataclass
from pathlib import Path

import yaml

_CONFIG_PATH = Path(__file__).resolve().parents[2] / "config" / "config.yaml"


@dataclass(frozen=True)
class Viewport:
    width: int
    height: int


@dataclass(frozen=True)
class Timeouts:
    navigation_ms: int
    action_ms: int
    expect_ms: int


class Secret(str):
    """A str that hides its value in repr(), so a password never shows up in
    pytest tracebacks, assertion diffs or Allure failure messages. It is
    still a plain str everywhere else (e.g. what Playwright types)."""

    def __repr__(self) -> str:
        return "'********'"


@dataclass(frozen=True)
class TestUser:
    """The fixed, pre-registered account authenticated tests log in as."""

    __test__ = False  # not a pytest test class, despite the name

    email: str
    password: Secret
    name: str


@dataclass(frozen=True)
class Config:
    env: str
    base_url: str
    viewport: Viewport
    timeouts: Timeouts


def load_config(env: str | None = None) -> Config:
    with open(_CONFIG_PATH) as f:
        raw = yaml.safe_load(f)

    env = env or os.environ.get("TEST_ENV", "prod")
    try:
        env_cfg = raw["environments"][env]
    except KeyError as exc:
        available = ", ".join(raw["environments"])
        raise ValueError(f"Unknown environment '{env}'. Available: {available}") from exc

    base_url = os.environ.get("BASE_URL") or env_cfg["base_url"]

    return Config(
        env=env,
        base_url=base_url,
        viewport=Viewport(**raw["viewport"]),
        timeouts=Timeouts(**raw["timeouts"]),
    )


def load_test_user() -> TestUser:
    """Reads the test account from the environment (.env locally, secrets in CI)."""
    keys = {"email": "TEST_EMAIL", "password": "TEST_PASSWORD", "name": "TEST_USER_NAME"}
    missing = [var for var in keys.values() if not os.environ.get(var)]
    if missing:
        raise RuntimeError(
            f"Missing test account settings: {', '.join(missing)}. Copy .env.example to .env and fill them in."
        )
    return TestUser(
        email=os.environ[keys["email"]],
        password=Secret(os.environ[keys["password"]]),
        name=os.environ[keys["name"]],
    )
