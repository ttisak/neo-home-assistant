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
}
