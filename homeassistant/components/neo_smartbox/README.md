# NEO Smartbox Integration

This integration allows you to control your NEO Smartbox device through Home Assistant.

## Features

- Remote control of your NEO Smartbox device
- Custom remote control card for easy access to all functions
- Device actions for automation
- Service calls for programmatic control

## Installation

This integration is built into Home Assistant Core. No additional installation is required.

## Configuration

1. Go to **Configuration** > **Integrations** in Home Assistant
2. Click "Add Integration" and search for "NEO Smartbox"
3. Follow the steps to add your device using your API key

## Using the Remote Control Card

The integration adds a custom card for your dashboard that provides an intuitive remote control interface.

### Adding the Card to Your Dashboard:

1. Edit your dashboard
2. Click "Add Card"
3. Scroll down to "Custom: NEO Smartbox Remote Card"
4. Configure the card with your remote entity:

```yaml
type: 'custom:neo-smartbox-remote-card'
entity: remote.neo_smartbox_remote
```

### Manual Resource Addition

If the card doesn't appear in your card picker, you may need to add the resource manually:

1. Go to **Configuration** > **Lovelace Dashboards** > **Resources**
2. Add a new resource with:
   - URL: `/static/neo_smartbox-card.js`
   - Type: JavaScript Module

## Device Actions

The integration provides device actions that can be used in automations. Available actions include:

- All remote control buttons (with both normal and long-press variants)
- Power control
- Navigation (up, down, left, right, ok)
- Media control (play, pause, etc.)

## Services

The integration provides the following services:

### `neo_smartbox.remote_key_action`

Send a remote key action to your NEO Smartbox.

| Service Data | Description |
|--------------|-------------|
| `device_id` | The ID of the device to control |
| `action` | The action to perform (from the list of available actions) |
| `long_press` | Whether to perform a long press (default: false) |

Example service call:

```yaml
service: neo_smartbox.remote_key_action
data:
  device_id: your_device_id
  action: POWER
  long_press: false
```

## Technical Details

The NEO Smartbox integration includes:

1. Custom lovelace card: `neo-smartbox-remote-card.js`
2. Frontend resources management
3. Device actions for automation
4. Remote platform implementation

## Troubleshooting

If you encounter issues:

1. Check that the card resource is properly loaded in your Lovelace resources
2. Verify that your device is properly connected and shows as available
3. Check Home Assistant logs for any error messages

## Development

For developers extending this integration:

- Frontend card source is in: `frontend/card/neo-smartbox-remote-card.js`
- Device actions are defined in: `device_action.py`
- Main API implementation is in: `remote.py`