// Simple version of the NEO Smartbox Remote Card
console.log("NEO Smartbox Remote Card - Simple Version Loading");

// Create the card class
class NeoSmartboxSimpleCard extends HTMLElement {
  constructor() {
    super();
    console.log("NEO Smartbox Remote Card - Constructor");
    this.attachShadow({ mode: "open" });
  }

  set hass(hass) {
    console.log("NEO Smartbox Remote Card - hass setter called");
    this._hass = hass;
    this.render();
  }

  setConfig(config) {
    console.log("NEO Smartbox Remote Card - setConfig called", config);
    if (!config.entity) {
      throw new Error("You need to define an entity");
    }
    this._config = config;
    this.render();
  }

  getCardSize() {
    return 4;
  }

  render() {
    if (!this._config || !this._hass) return;

    const entityId = this._config.entity;
    const state = this._hass.states[entityId];

    if (!state) {
      this.shadowRoot.innerHTML = `
        <style>
          ha-card {
            padding: 16px;
            color: var(--primary-text-color);
          }
        </style>
        <ha-card>
          <div>Entity ${entityId} not found.</div>
        </ha-card>
      `;
      return;
    }

    const name = state.attributes.friendly_name || entityId;

    this.shadowRoot.innerHTML = `
      <style>
        ha-card {
          padding: 16px;
          color: var(--primary-text-color);
        }
        .remote {
          display: flex;
          flex-direction: column;
          align-items: center;
        }
        .title {
          font-size: 1.2em;
          font-weight: bold;
          margin-bottom: 16px;
        }
        .button-row {
          display: flex;
          margin: 8px 0;
          gap: 8px;
        }
        button {
          min-width: 60px;
          height: 36px;
          border-radius: 4px;
          background-color: var(--primary-color);
          color: var(--text-primary-color);
          border: none;
          cursor: pointer;
        }
        .row-label {
          width: 100%;
          text-align: center;
          margin: 8px 0;
          opacity: 0.7;
        }
      </style>
      <ha-card>
        <div class="remote">
          <div class="title">${name}</div>

          <div class="row-label">Power</div>
          <div class="button-row">
            <button @click="${() => this._sendCommand("power")}">Power</button>
          </div>

          <div class="row-label">Navigation</div>
          <div class="button-row">
            <button @click="${() => this._sendCommand("up")}">Up</button>
          </div>
          <div class="button-row">
            <button @click="${() => this._sendCommand("left")}">Left</button>
            <button @click="${() => this._sendCommand("select")}">OK</button>
            <button @click="${() => this._sendCommand("right")}">Right</button>
          </div>
          <div class="button-row">
            <button @click="${() => this._sendCommand("down")}">Down</button>
          </div>

          <div class="row-label">Control</div>
          <div class="button-row">
            <button @click="${() => this._sendCommand("back")}">Back</button>
            <button @click="${() => this._sendCommand("home")}">Home</button>
            <button @click="${() => this._sendCommand("menu")}">Menu</button>
          </div>

          <div class="row-label">Volume</div>
          <div class="button-row">
            <button @click="${() =>
              this._sendCommand("volume_down")}">Vol -</button>
            <button @click="${() => this._sendCommand("mute")}">Mute</button>
            <button @click="${() =>
              this._sendCommand("volume_up")}">Vol +</button>
          </div>

          <div class="row-label">Media</div>
          <div class="button-row">
            <button @click="${() => this._sendCommand("rewind")}">⏪</button>
            <button @click="${() =>
              this._sendCommand("play_pause")}">⏯️</button>
            <button @click="${() =>
              this._sendCommand("fast_forward")}">⏩</button>
          </div>
        </div>
      </ha-card>
    `;

    // Add event listeners manually since we're using innerHTML
    this._addEventListeners();
  }

  _addEventListeners() {
    // All buttons already have inline event handlers from the template
    // This is just a placeholder in case we need additional event handling
  }

  _sendCommand(command) {
    if (!this._hass || !this._config) return;

    console.log("Sending command:", command);

    this._hass.callService("remote", "send_command", {
      entity_id: this._config.entity,
      command: command,
    });
  }
}

// Register the card
(function () {
  if (!window.customElements.get("neo-smartbox-simple-card")) {
    console.log("Registering neo-smartbox-simple-card");
    try {
      customElements.define("neo-smartbox-simple-card", NeoSmartboxSimpleCard);
      console.log("Successfully registered neo-smartbox-simple-card");

      window.customCards = window.customCards || [];
      window.customCards.push({
        type: "neo-smartbox-simple-card",
        name: "NEO Smartbox Simple Card",
        description:
          "A simplified remote control card for NEO Smartbox devices",
      });
    } catch (error) {
      console.error("Failed to register neo-smartbox-simple-card:", error);
    }
  }
})();
