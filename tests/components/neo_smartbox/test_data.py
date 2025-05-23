"""Test data for NEO Smartbox integration tests."""

from homeassistant.components.neo_smartbox.models import (
    NeoDeviceType,
    NeoSmartboxDevice,
)

# Mock API key for tests
API_KEY = "test_api_key"

# STB device ID
STB_DEVICE_ID = "device1"

# Smart TV device ID
SMART_TV_DEVICE_ID = "device2"

# Mock device data for testing
DEVICE_DATA = [
    NeoSmartboxDevice(
        id=STB_DEVICE_ID,
        name="Living Room Box",
        type=NeoDeviceType.STB,
    ),
    NeoSmartboxDevice(
        id=SMART_TV_DEVICE_ID,
        name="Bedroom TV",
        type=NeoDeviceType.SMART_TV,
    ),
]
