"""Constants for the NEO Smartbox integration."""

from typing import Final

DOMAIN: Final = "neo_smartbox"

# API endpoints
API_BASE_URL: Final = "https://stargate.telekom.si/api"
API_DEVICE_LIST: Final = f"{API_BASE_URL}/titan.tv.CompanionService/DeviceList"
API_SEND_KEY_ACTION: Final = f"{API_BASE_URL}/titan.tv.CompanionService/SendKeyAction"

# Configuration
CONF_API_KEY: Final = "api_key"

# Data update interval (in seconds)
UPDATE_INTERVAL: Final = 60  # Cloud polling minimum

# Remote commands
REMOTE_COMMANDS = {
    "home": "Home",
    "power": "Power",
    "volume_up": "VolumeUp",
    "volume_down": "VolumeDown",
    "channel_up": "ChannelUp",
    "channel_down": "ChannelDown",
    "right": "Right",
    "left": "Left",
    "up": "Up",
    "down": "Down",
    "select": "Ok",
    "back": "Back",
    "guide": "Guide",
    "menu": "Menu",
    "mute": "Mute",
    "play_pause": "PlayPause",
    "rewind": "Rewind",
    "fast_forward": "FastForward",
    "voice_search": "VoiceSearch",  # Added for voice search functionality
    # Add any additional commands that may be needed
}

# NEO app command reference (for UI implementation)
NEO_APP_COMMANDS = {
    "power": "Power on/off the device",
    "home": "Return to home screen",
    "menu": "Open menu",
    "back": "Go back",
    "up": "Navigate up",
    "down": "Navigate down",
    "left": "Navigate left",
    "right": "Navigate right",
    "select": "Select (OK)",
    "volume_up": "Increase volume",
    "volume_down": "Decrease volume",
    "channel_up": "Next channel",
    "channel_down": "Previous channel",
    "mute": "Mute audio",
    "play_pause": "Play or pause media",
    "rewind": "Rewind media",
    "fast_forward": "Fast forward media",
    "guide": "Open guide",
    "voice_search": "Activate voice search",
}
