#!/bin/bash

# Script to sync the neo-smartbox-remote-card files to the Home Assistant www directory

echo "Syncing NEO Smartbox Remote Card files..."
cp -v /workspaces/neo-home-assistant/www/neo-smartbox-remote-card/neo-smartbox-remote-card.js /workspaces/neo-home-assistant/config/www/neo-smartbox-remote-card/
echo "Done! The card has been copied to the Home Assistant www directory."
echo "You may need to restart Home Assistant and clear your browser cache."