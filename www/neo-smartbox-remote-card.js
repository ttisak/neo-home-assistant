console.info("NEO-SMARTBOX-REMOTE-CARD: Loading...");

class NeoSmartboxRemoteCard extends HTMLElement {
  constructor() {
    super();
    console.info("NEO-SMARTBOX-REMOTE-CARD: Constructor called");
    this.attachShadow({ mode: "open" });
  }

  // Required: Defines the configuration for the card
  setConfig(config) {
    console.info("NEO-SMARTBOX-REMOTE-CARD: setConfig called", config);

    if (!config.entity) {
      throw new Error("You need to define an entity");
    }

    this._config = config;
    this._render();
  }

  // Called when the state of Home Assistant changes
  set hass(hass) {
    console.info("NEO-SMARTBOX-REMOTE-CARD: hass updated");
    this._hass = hass;

    // Re-render to update any dynamic content
    if (this._config) {
      this._render();
    }
  }

  // For sizing in the dashboard
  getCardSize() {
    return 5; // Larger card
  }

  // Render the card
  _render() {
    if (!this._config || !this._hass) return;

    const entityId = this._config.entity;
    const state = this._hass.states[entityId];
    const name = state ? state.attributes.friendly_name || entityId : entityId;

    console.info(
      "NEO-SMARTBOX-REMOTE-CARD: Rendering card for entity",
      entityId,
    );

    this.shadowRoot.innerHTML = `
      <style>
        :host {
          --primary-color: var(--primary-color, #03a9f4);
          --text-primary-color: var(--text-primary-color, white);
          --card-background-color: var(--card-background-color, var(--paper-card-background-color, white));
        }
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
          height: 40px;
          border-radius: 4px;
          background-color: var(--primary-color);
          color: var(--text-primary-color);
          border: none;
          cursor: pointer;
          font-size: 14px;
        }
        .row-label {
          width: 100%;
          text-align: center;
          margin: 8px 0;
          opacity: 0.7;
        }
        .dpad {
          display: grid;
          grid-template-columns: repeat(3, 60px);
          grid-template-rows: repeat(3, 60px);
          gap: 8px;
        }
        .center-button {
          background-color: var(--accent-color, #ff9800);
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
          <div class="dpad">
            <div></div>
            <button @click="${() => this._sendCommand("up")}">Up</button>
            <div></div>

            <button @click="${() => this._sendCommand("left")}">Left</button>
            <button class="center-button" @click="${() =>
              this._sendCommand("select")}">OK</button>
            <button @click="${() => this._sendCommand("right")}">Right</button>

            <div></div>
            <button @click="${() => this._sendCommand("down")}">Down</button>
            <div></div>
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

          <div class="row-label">Voice</div>
          <div class="button-row">
            <button @click="${() =>
              this._sendCommand("voice_search")}">Voice Search</button>
          </div>
        </div>
      </ha-card>
    `;
  }

  // Send a command to the device
  _sendCommand(command) {
    if (!this._hass || !this._config) return;

    console.info(
      `NEO-SMARTBOX-REMOTE-CARD: Sending command "${command}" to entity ${this._config.entity}`,
    );

    this._hass.callService("remote", "send_command", {
      entity_id: this._config.entity,
      command: command,
    });
  }
}

// Register the element with Home Assistant
customElements.define("neo-smartbox-remote-card", NeoSmartboxRemoteCard);

// Declare card for the lovelace card picker
window.customCards = window.customCards || [];
window.customCards.push({
  type: "neo-smartbox-remote-card",
  name: "NEO Smartbox Remote",
  description: "Remote control card for NEO Smartbox devices",
});

console.info("NEO-SMARTBOX-REMOTE-CARD: Registered successfully");
