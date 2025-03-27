# NEO Smartbox Remote Card

A custom card for Home Assistant that provides a remote control interface for NEO Smartbox devices, resembling the official NEO app.

## Installation

1. Copy the `neo-smartbox-remote-card.js` file to your Home Assistant `www/neo-smartbox-remote-card/` directory.
2. Add the following to your `configuration.yaml` file:

```yaml
lovelace:
  resources:
    - url: /local/neo-smartbox-remote-card/neo-smartbox-remote-card.js
      type: module
```

3. Alternatively, if you're using YAML mode, you can add it to your `ui-lovelace.yaml` file:

```yaml
resources:
  - url: /local/neo-smartbox-remote-card/neo-smartbox-remote-card.js
    type: module
```

4. If you're using the UI mode, you can add this as a resource through the Lovelace resource manager.

## Usage

Add the card to your dashboard:

```yaml
type: 'custom:neo-smartbox-remote-card'
entity: remote.neo_smartbox_living_room  # Replace with your NEO Smartbox entity
```

## Features

- Full remote control UI matching the NEO app design
- Media control buttons (rewind, play/pause, fast forward)
- D-pad navigation with OK button
- Power, home, back and menu buttons
- Volume control
- Voice control button

## Troubleshooting

If the card doesn't appear or work correctly, check the following:

1. Make sure the resource is correctly loaded (check browser console for errors)
2. Verify that the entity exists and is a valid NEO Smartbox remote entity
3. Ensure that the remote integration is correctly set up and functioning

## Support

This card is part of the NEO Smartbox integration for Home Assistant. For support or to report issues, please visit the GitHub repository.