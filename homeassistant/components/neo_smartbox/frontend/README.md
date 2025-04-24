# NEO Smartbox Remote Card

This directory contains the frontend resources for the NEO Smartbox integration.

## Usage

The card will be automatically registered as a resource in Home Assistant when the integration is loaded.

To use the card in your Lovelace UI:

1. Go to your dashboard
2. Add a new card
3. Scroll down to "Custom: NEO Smartbox Remote Card"
4. Configure the card with your remote entity:

```yaml
type: 'custom:neo-smartbox-remote-card'
entity: remote.neo_smartbox_remote
```

## Manual Installation

If the card doesn't appear automatically in your custom cards, you can add it manually:

1. Go to Configuration -> Lovelace Dashboards -> Resources
2. Add a new resource with:
   - URL: `/static/neo_smartbox-card.js`
   - Type: JavaScript Module

## Development

If you're developing or modifying the card, you can find the source code in the `card/` subdirectory.