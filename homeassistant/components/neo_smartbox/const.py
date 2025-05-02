"""Constants for the NEO Smartbox integration."""

from typing import Final

DOMAIN: Final = "neo_smartbox"

# API endpoints
API_BASE_URL: Final = "https://stargate.telekom.si/api"
API_DEVICE_LIST: Final = f"{API_BASE_URL}/titan.tv.CompanionService/DeviceList"
API_GET_SMART_TV_LIST: Final = (
    f"{API_BASE_URL}/titan.management.SelfCareService/GetSmartTVList"
)
API_SEND_KEY_ACTION: Final = f"{API_BASE_URL}/titan.tv.CompanionService/SendKeyAction"

API_ZAP_LIST: Final = f"{API_BASE_URL}/titan.tv.WebEpg/ZapList"

API_NAVIGATE_ACTION: Final = f"{API_BASE_URL}/titan.tv.CompanionService/NavigateAction"

# Configuration
CONF_API_KEY: Final = "api_key"

# Data update interval (in seconds)
UPDATE_INTERVAL: Final = 60  # Cloud polling minimum

# Remote commands for NEO Smartbox
REMOTE_COMMANDS = {
    "power": "Power",
    "rewind": "Rewind",
    "play_pause": "Play",
    "forward": "Forward",
    "up": "CursorUp",
    "down": "CursorDown",
    "left": "CursorLeft",
    "right": "CursorRight",
    "ok": "Select",
    "back": "Back",
    "home": "Home",
    "menu": "TvGuide",
    "volume_down": "VolumeDown",
    "volume_mute": "VolumeMute",
    "volume_up": "VolumeUp",
    "channel_up": "ChannelUp",
    "channel_down": "ChannelDown",
}

# NEO app command reference (for UI implementation)
NEO_APP_COMMANDS = {
    "power": "Power on/off the device",
    "rewind": "Rewind media",
    "play_pause": "Play or pause media",
    "forward": "Fast forward media",
    "up": "Navigate up",
    "down": "Navigate down",
    "left": "Navigate left",
    "right": "Navigate right",
    "ok": "Select (OK)",
    "back": "Go back",
    "home": "Return to home screen",
    "menu": "Open guide",
    "volume_down": "Decrease volume",
    "volume_mute": "Mute/unmute audio",
    "volume_up": "Increase volume",
    "channel_up": "Next channel",
    "channel_down": "Previous channel",
}
