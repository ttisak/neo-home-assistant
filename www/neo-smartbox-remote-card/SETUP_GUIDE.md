# NEO Smartbox Remote Setup Guide

This guide will help you set up and use the NEO Smartbox remote card in Home Assistant, which provides a UI similar to the official NEO app.

## Prerequisites

1. A working Home Assistant installation
2. NEO Smartbox integration properly configured with your API key
3. At least one NEO Smartbox device discovered and set up

## Installation Steps

### 1. Install the Custom Card

1. Download the `neo-smartbox-remote-card.js` file from this directory
2. Create a folder in your Home Assistant configuration directory: `www/neo-smartbox-remote-card/`
3. Copy the downloaded JS file to this folder

### 2. Add the Resource to Lovelace

#### Method 1: Using the UI

1. Go to **Configuration** → **Lovelace Dashboards** → **Resources**
2. Click the **Add Resource** button
3. Enter the URL: `/local/neo-smartbox-remote-card/neo-smartbox-remote-card.js`
4. Set the resource type to **JavaScript Module**
5. Click **Create**

#### Method 2: Using YAML configuration

Add the following to your `configuration.yaml` file:

```yaml
lovelace:
  resources:
    - url: /local/neo-smartbox-remote-card/neo-smartbox-remote-card.js
      type: module
```

Then restart Home Assistant.

### 3. Add the Card to Your Dashboard

1. Go to the dashboard where you want to add the remote
2. Click the **Edit Dashboard** button (three dots in the top right corner)
3. Click the **Add Card** button
4. Select **Manual** at the bottom of the card picker
5. Enter the following YAML:

```yaml
type: 'custom:neo-smartbox-remote-card'
entity: remote.neo_smartbox_XXXX  # Replace with your actual entity ID
```

6. Click **Save**

### 4. Using the Remote

The remote interface provides the following controls:

- **Power Button**: Turn the device on/off
- **Media Controls**: Play/Pause, Rewind, Fast-Forward
- **D-Pad Navigation**: Move up, down, left, right with an OK button in the center
- **Navigation Buttons**: Back, Home, Menu
- **Volume Controls**: Volume Up, Volume Down, Mute
- **Voice Control**: Microphone button for voice commands

## Troubleshooting

### Card Not Loading

If the card doesn't appear or shows an error:

1. Check your browser's console for JavaScript errors
2. Make sure the resource URL is correct and points to where you placed the file
3. Verify that the file permissions allow Home Assistant to read it

### Commands Not Working

If the remote buttons don't send commands:

1. Check that your NEO Smartbox entity is correctly set up and online
2. Verify that the API key is valid and has the necessary permissions
3. Check the Home Assistant logs for any errors related to the NEO Smartbox integration

### Card Shows "Entity Not Found"

This usually means the entity ID you specified doesn't exist or is not accessible:

1. Go to **Developer Tools** → **States** to find the correct entity ID for your NEO Smartbox
2. Update the card configuration with the correct entity ID

## Advanced Configuration

You can customize the card by adding additional parameters:

```yaml
type: 'custom:neo-smartbox-remote-card'
entity: remote.neo_smartbox_XXXX  # Replace with your actual entity ID
name: Living Room TV  # Optional: Custom name for the card
show_power_button: true  # Optional: Show/hide power button
```

## Support

If you encounter any issues:

1. Check the Home Assistant logs for errors
2. Review the [NEO Smartbox integration documentation](https://github.com/ttisak/neo-home-assistant)
3. Report issues on the GitHub repository