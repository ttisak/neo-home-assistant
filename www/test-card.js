console.info("TEST-CARD: Loading...");

class TestCard extends HTMLElement {
  // Required: Defines the configuration for the card
  setConfig(config) {
    console.info("TEST-CARD: setConfig called", config);

    if (!config.entity) {
      throw new Error("You need to define an entity");
    }

    this._config = config;

    // Create the card content
    this.innerHTML = `
      <ha-card header="Test Card">
        <div class="card-content">
          <p>This is a simple test card to verify custom cards are working</p>
          <p>Entity: ${config.entity}</p>
        </div>
        <div class="card-actions">
          <mwc-button @click="${this._handleAction}">Test Button</mwc-button>
        </div>
      </ha-card>
    `;

    console.info("TEST-CARD: DOM created");
  }

  // Called when the state of Home Assistant changes
  set hass(hass) {
    console.info("TEST-CARD: hass updated");
    this._hass = hass;

    // Update any dynamic content here if needed
    if (
      this._config &&
      this._config.entity &&
      hass.states[this._config.entity]
    ) {
      console.info(
        "TEST-CARD: entity state:",
        hass.states[this._config.entity].state,
      );
    }
  }

  // When the card is connected to the DOM
  connectedCallback() {
    console.info("TEST-CARD: connected to DOM");
  }

  // For sizing in the dashboard
  getCardSize() {
    return 2;
  }

  // Example button handler
  _handleAction() {
    console.info("TEST-CARD: button clicked");
    if (this._hass) {
      this._hass.callService("remote", "send_command", {
        entity_id: this._config.entity,
        command: "test_command",
      });
    }
  }
}

// Register the element with Home Assistant
customElements.define("test-card", TestCard);

// Declare card for the lovelace card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "test-card",
  name: "Test Card",
  description: "A simple test card to verify custom cards are working",
});

console.info("TEST-CARD: Registered successfully");
