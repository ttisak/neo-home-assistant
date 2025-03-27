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
          --neo-primary: #0288d1;         /* NEO App blue */
          --neo-secondary: #01579b;       /* Darker blue for hover */
          --neo-accent: #29b6f6;          /* Lighter blue for select button */
          --neo-text: white;
          --neo-background: var(--card-background-color, var(--ha-card-background, #1c1c1c));
          --neo-card-radius: var(--ha-card-border-radius, 4px);
        }

        .card {
          background-color: var(--neo-background);
          border-radius: var(--neo-card-radius);
          color: var(--primary-text-color, white);
          box-shadow: var(--ha-card-box-shadow, 0 2px 2px rgba(0,0,0,0.24));
          padding: 16px;
          font-family: var(--primary-font-family, Roboto, sans-serif);
        }

        .remote {
          display: flex;
          flex-direction: column;
          align-items: center;
        }

        .title {
          font-size: 1.5em;
          font-weight: 500;
          margin-bottom: 20px;
          text-align: center;
        }

        .status {
          font-size: 0.9em;
          opacity: 0.8;
          margin-bottom: 16px;
        }

        .button-row {
          display: flex;
          margin: 8px 0;
          gap: 8px;
          justify-content: center;
          width: 100%;
        }

        button {
          min-width: 60px;
          height: 40px;
          border-radius: 8px;
          background-color: var(--neo-primary);
          color: var(--neo-text);
          border: none;
          cursor: pointer;
          font-size: 14px;
          transition: background-color 0.2s ease, transform 0.1s ease;
          font-weight: 500;
        }

        button:hover {
          background-color: var(--neo-secondary);
        }

        button:active {
          transform: scale(0.95);
        }

        .section {
          width: 100%;
          margin: 16px 0 8px 0;
          border-top: 1px solid rgba(255, 255, 255, 0.1);
          padding-top: 16px;
        }

        .section-title {
          width: 100%;
          text-align: center;
          margin-bottom: 12px;
          font-weight: 500;
          font-size: 0.9em;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          opacity: 0.7;
        }

        .dpad {
          display: grid;
          grid-template-columns: repeat(3, 60px);
          grid-template-rows: repeat(3, 60px);
          gap: 8px;
        }

        .center-button {
          background-color: var(--neo-accent);
          font-weight: bold;
        }

        .center-button:hover {
          background-color: var(--neo-primary);
        }

        .power-button {
          background-color: #e53935;  /* Red power button */
        }

        .power-button:hover {
          background-color: #c62828;
        }

        .media-button {
          display: flex;
          align-items: center;
          justify-content: center;
          flex: 1;
        }

        .voice-button {
          width: 100%;
          height: 48px;
          border-radius: 24px;
        }
      </style>

      <div class="card">
        <div class="remote">
          <div class="title">${name}</div>
          <div class="status">${state ? state.state : "unavailable"}</div>

          <div class="section">
            <div class="section-title">Power</div>
            <div class="button-row">
              <button class="power-button" @click="${() =>
                this._sendCommand("power")}">Power</button>
            </div>
          </div>

          <div class="section">
            <div class="section-title">Navigation</div>
            <div class="dpad">
              <div></div>
              <button @click="${() => this._sendCommand("up")}">Up</button>
              <div></div>

              <button @click="${() => this._sendCommand("left")}">Left</button>
              <button class="center-button" @click="${() =>
                this._sendCommand("select")}">OK</button>
              <button @click="${() =>
                this._sendCommand("right")}">Right</button>

              <div></div>
              <button @click="${() => this._sendCommand("down")}">Down</button>
              <div></div>
            </div>
          </div>

          <div class="section">
            <div class="section-title">Control</div>
            <div class="button-row">
              <button @click="${() => this._sendCommand("back")}">Back</button>
              <button @click="${() => this._sendCommand("home")}">Home</button>
              <button @click="${() => this._sendCommand("menu")}">Menu</button>
            </div>
          </div>

          <div class="section">
            <div class="section-title">Volume</div>
            <div class="button-row">
              <button @click="${() =>
                this._sendCommand("volume_down")}">Vol -</button>
              <button @click="${() => this._sendCommand("mute")}">Mute</button>
              <button @click="${() =>
                this._sendCommand("volume_up")}">Vol +</button>
            </div>
          </div>

          <div class="section">
            <div class="section-title">Media</div>
            <div class="button-row">
              <button class="media-button" @click="${() =>
                this._sendCommand("rewind")}">⏪</button>
              <button class="media-button" @click="${() =>
                this._sendCommand("play_pause")}">⏯️</button>
              <button class="media-button" @click="${() =>
                this._sendCommand("fast_forward")}">⏩</button>
            </div>
          </div>

          <div class="section">
            <div class="section-title">Voice</div>
            <div class="button-row">
              <button class="voice-button" @click="${() =>
                this._sendCommand("voice_search")}">Voice Search</button>
            </div>
          </div>
        </div>
      </div>
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
