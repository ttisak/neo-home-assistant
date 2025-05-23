"""Test helpers for NEO Smartbox tests."""

import pytest

from homeassistant.components.neo_smartbox.const import DOMAIN


# This fixture overrides the default `check_translations` fixture behavior
# to ignore all translations related to the NEO Smartbox domain in tests
@pytest.fixture
def ignore_translations_for_mock_domains():
    """Fixture to ignore translation for domain."""
    return DOMAIN
