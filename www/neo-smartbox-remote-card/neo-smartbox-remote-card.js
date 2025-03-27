// Add debug logging
console.log("NEO Smartbox remote card script is loading...");

// Wrap everything in an IIFE to avoid global scope pollution
(function () {
  class NeoSmartboxRemoteCard extends HTMLElement {
    // Define properties
    static get properties() {
      return {
        hass: {},
        config: {},
      };
    }

    constructor() {
      super();
      console.log("NEO Smartbox remote card constructor called");
      this.attachShadow({ mode: "open" });
    }

    set hass(hass) {
      this._hass = hass;
      this.render();
    }

    // Set card configuration
    setConfig(config) {
      if (!config.entity) {
        throw new Error("You need to define an entity");
      }

      this.config = config;
      this.render();
    }

    // Get the card size
    getCardSize() {
      return 6;
    }

    // Handle button clicks
    _handleAction(action) {
      if (!this._hass || !this.config) return;

      const entityId = this.config.entity;

      this._hass.callService("remote", "send_command", {
        entity_id: entityId,
        command: action,
      });
    }

    // Render the card
    render() {
      if (!this._hass || !this.config) return;

      const entityId = this.config.entity;
      const stateObj = this._hass.states[entityId];

      if (!stateObj) {
        this.shadowRoot.innerHTML = `
        <ha-card>
          <div class="not-found">Entity ${entityId} not found.</div>
        </ha-card>
      `;
        return;
      }

      const available = stateObj.state !== "unavailable";
      const deviceName = stateObj.attributes.friendly_name || entityId;

      this.shadowRoot.innerHTML = `
      <style>
        :host {
          --primary-color: var(--primary-color, #03a9f4);
          --text-primary-color: var(--text-primary-color, #fff);
          --card-background-color: var(--card-background-color, #1c1c1c);
          --secondary-background-color: var(--secondary-background-color, #2d2d2d);
          --disabled-color: var(--disabled-color, #626262);
          --button-color: var(--primary-color, #03a9f4);
        }

        ha-card {
          padding: 16px;
          background-color: var(--card-background-color);
          color: var(--text-primary-color);
          border-radius: 12px;
        }

        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }

        .card-title {
          font-size: 18px;
          font-weight: 500;
        }

        .power-button {
          width: 36px;
          height: 36px;
          border-radius: 50%;
          background-color: var(--secondary-background-color);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .power-button svg {
          fill: var(--button-color);
          width: 20px;
          height: 20px;
        }

        .remote-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 24px;
        }

        .control-row {
          display: flex;
          justify-content: center;
          align-items: center;
          width: 100%;
          gap: 8px;
        }

        .remote-button {
          border-radius: 32px;
          background-color: var(--secondary-background-color);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background-color 0.2s;
        }

        .remote-button.disabled {
          opacity: 0.5;
          cursor: default;
        }

        .remote-button:not(.disabled):hover {
          background-color: #3d3d3d;
        }

        .media-controls {
          width: 100%;
          height: 60px;
          border-radius: 32px;
          background-color: var(--secondary-background-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 10px;
        }

        .media-button {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .media-button svg {
          fill: var(--button-color);
          width: 20px;
          height: 20px;
        }

        .play-pause {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background-color: var(--button-color);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .play-pause svg {
          fill: #fff;
          width: 24px;
          height: 24px;
        }

        .dpad {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          grid-template-rows: 1fr 1fr 1fr;
          width: 180px;
          height: 180px;
          position: relative;
        }

        .dpad-button {
          width: 60px;
          height: 60px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .dpad-button svg {
          fill: var(--button-color);
          width: 24px;
          height: 24px;
        }

        .dpad-center {
          grid-column: 2;
          grid-row: 2;
          width: 80px;
          height: 80px;
          border-radius: 50%;
          border: 2px solid #3d3d3d;
          display: flex;
          align-items: center;
          justify-content: center;
          position: absolute;
          top: 50px;
          left: 50px;
          background-color: transparent;
          cursor: pointer;
        }

        .dpad-center-text {
          color: var(--button-color);
          font-size: 22px;
          font-weight: bold;
        }

        .nav-row {
          display: flex;
          justify-content: space-between;
          width: 100%;
          margin-top: 8px;
        }

        .nav-button {
          width: 50px;
          height: 50px;
          border-radius: 50%;
          background-color: var(--secondary-background-color);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .nav-button svg {
          fill: var(--button-color);
          width: 20px;
          height: 20px;
        }

        .voice-controls {
          width: 100%;
          height: 60px;
          border-radius: 32px;
          background-color: var(--secondary-background-color);
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 10px;
          margin-top: 8px;
        }

        .voice-button {
          width: 40px;
          height: 40px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .voice-button svg {
          fill: var(--button-color);
          width: 20px;
          height: 20px;
        }

        .mic-button {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          background-color: var(--button-color);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
        }

        .mic-button svg {
          fill: #fff;
          width: 24px;
          height: 24px;
        }
      </style>

      <ha-card>
        <div class="card-header">
          <div class="card-title">${deviceName}</div>
          <div class="power-button" @click="${() =>
            this._handleAction("power")}">
            <svg viewBox="0 0 24 24"><path d="M13,3H11V13H13V3M17.83,5.17L16.41,6.59C17.99,7.86 19,9.81 19,12C19,15.87 15.87,19 12,19C8.13,19 5,15.87 5,12C5,9.81 6.01,7.86 7.58,6.58L6.17,5.17C4.23,6.82 3,9.26 3,12C3,16.97 7.03,21 12,21C16.97,21 21,16.97 21,12C21,9.26 19.77,6.82 17.83,5.17Z"></path></svg>
          </div>
        </div>

        <div class="remote-container">
          <!-- Media control buttons (rewind, play/pause, forward) -->
          <div class="media-controls">
            <div class="media-button" @click="${() =>
              this._handleAction("rewind")}">
              <svg viewBox="0 0 24 24"><path d="M11.5,12L20,18V6M11,18V6L2.5,12L11,18Z"></path></svg>
            </div>
            <div class="play-pause" @click="${() =>
              this._handleAction("play_pause")}">
              <svg viewBox="0 0 24 24"><path d="M14,19H18V5H14M6,19H10V5H6V19Z"></path></svg>
            </div>
            <div class="media-button" @click="${() =>
              this._handleAction("fast_forward")}">
              <svg viewBox="0 0 24 24"><path d="M13,6V18L21.5,12M4,18L12.5,12L4,6V18Z"></path></svg>
            </div>
          </div>

          <!-- D-Pad controls -->
          <div class="dpad">
            <div class="dpad-button" style="grid-column: 2; grid-row: 1;" @click="${() =>
              this._handleAction("up")}">
              <svg viewBox="0 0 24 24"><path d="M7.41,15.41L12,10.83L16.59,15.41L18,14L12,8L6,14L7.41,15.41Z"></path></svg>
            </div>
            <div class="dpad-button" style="grid-column: 1; grid-row: 2;" @click="${() =>
              this._handleAction("left")}">
              <svg viewBox="0 0 24 24"><path d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z"></path></svg>
            </div>
            <div class="dpad-center" @click="${() =>
              this._handleAction("select")}">
              <div class="dpad-center-text">ok</div>
            </div>
            <div class="dpad-button" style="grid-column: 3; grid-row: 2;" @click="${() =>
              this._handleAction("right")}">
              <svg viewBox="0 0 24 24"><path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z"></path></svg>
            </div>
            <div class="dpad-button" style="grid-column: 2; grid-row: 3;" @click="${() =>
              this._handleAction("down")}">
              <svg viewBox="0 0 24 24"><path d="M7.41,8.58L12,13.17L16.59,8.58L18,10L12,16L6,10L7.41,8.58Z"></path></svg>
            </div>
          </div>

          <!-- Navigation buttons (back, home, menu) -->
          <div class="nav-row">
            <div class="nav-button" @click="${() =>
              this._handleAction("back")}">
              <svg viewBox="0 0 24 24"><path d="M20,11V13H8L13.5,18.5L12.08,19.92L4.16,12L12.08,4.08L13.5,5.5L8,11H20Z"></path></svg>
            </div>
            <div class="nav-button" @click="${() =>
              this._handleAction("home")}">
              <svg viewBox="0 0 24 24"><path d="M10,20V14H14V20H19V12H22L12,3L2,12H5V20H10Z"></path></svg>
            </div>
            <div class="nav-button" @click="${() =>
              this._handleAction("menu")}">
              <svg viewBox="0 0 24 24"><path d="M3,6H21V8H3V6M3,11H21V13H3V11M3,16H21V18H3V16Z"></path></svg>
            </div>
          </div>

          <!-- Voice control buttons (volume down, mic, volume up) -->
          <div class="voice-controls">
            <div class="voice-button" @click="${() =>
              this._handleAction("volume_down")}">
              <svg viewBox="0 0 24 24"><path d="M12,4L9.91,6.09L12,8.18M4.27,3L3,4.27L7.73,9H3V15H7L12,20V13.27L16.25,17.53C15.58,18.04 14.83,18.46 14,18.7V20.77C15.38,20.45 16.63,19.82 17.68,18.96L19.73,21L21,19.73L12,10.73M19,12C19,12.94 18.8,13.82 18.46,14.64L19.97,16.15C20.62,14.91 21,13.5 21,12C21,7.72 18,4.14 14,3.23V5.29C16.89,6.15 19,8.83 19,12M16.5,12C16.5,10.23 15.5,8.71 14,7.97V10.18L16.45,12.63C16.5,12.43 16.5,12.21 16.5,12Z"></path></svg>
            </div>
            <div class="mic-button" @click="${() =>
              this._handleAction("voice_search")}">
              <svg viewBox="0 0 24 24"><path d="M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z"></path></svg>
            </div>
            <div class="voice-button" @click="${() =>
              this._handleAction("volume_up")}">
              <svg viewBox="0 0 24 24"><path d="M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.84 14,18.7V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16C15.5,15.29 16.5,13.76 16.5,12M3,9V15H7L12,20V4L7,9H3Z"></path></svg>
            </div>
          </div>
        </div>
      </ha-card>
    `;

      // Add event listeners manually since we're using innerHTML
      this._addEventListeners();
    }

    // Add event listeners to buttons
    _addEventListeners() {
      // Power button
      this.shadowRoot
        .querySelector(".power-button")
        ?.addEventListener("click", () => {
          this._handleAction("power");
        });

      // Media control buttons
      this.shadowRoot
        .querySelector(".media-button:first-child")
        ?.addEventListener("click", () => {
          this._handleAction("rewind");
        });

      this.shadowRoot
        .querySelector(".play-pause")
        ?.addEventListener("click", () => {
          this._handleAction("play_pause");
        });

      this.shadowRoot
        .querySelector(".media-button:last-child")
        ?.addEventListener("click", () => {
          this._handleAction("fast_forward");
        });

      // D-Pad buttons
      const dpadButtons = this.shadowRoot.querySelectorAll(".dpad-button");
      dpadButtons[0]?.addEventListener("click", () => this._handleAction("up"));
      dpadButtons[1]?.addEventListener("click", () =>
        this._handleAction("left"),
      );
      dpadButtons[2]?.addEventListener("click", () =>
        this._handleAction("right"),
      );
      dpadButtons[3]?.addEventListener("click", () =>
        this._handleAction("down"),
      );

      // Center OK button
      this.shadowRoot
        .querySelector(".dpad-center")
        ?.addEventListener("click", () => {
          this._handleAction("select");
        });

      // Navigation buttons
      const navButtons = this.shadowRoot.querySelectorAll(".nav-button");
      navButtons[0]?.addEventListener("click", () =>
        this._handleAction("back"),
      );
      navButtons[1]?.addEventListener("click", () =>
        this._handleAction("home"),
      );
      navButtons[2]?.addEventListener("click", () =>
        this._handleAction("menu"),
      );

      // Voice control buttons
      const voiceButtons = this.shadowRoot.querySelectorAll(".voice-button");
      voiceButtons[0]?.addEventListener("click", () =>
        this._handleAction("volume_down"),
      );
      voiceButtons[1]?.addEventListener("click", () =>
        this._handleAction("volume_up"),
      );

      // Mic button
      this.shadowRoot
        .querySelector(".mic-button")
        ?.addEventListener("click", () => {
          this._handleAction("voice_search");
        });
    }
  }

  // Register the card
  console.log("About to register neo-smartbox-remote-card custom element");
  try {
    customElements.define("neo-smartbox-remote-card", NeoSmartboxRemoteCard);
    console.log(
      "Successfully registered neo-smartbox-remote-card custom element",
    );

    // Define card type
    window.customCards = window.customCards || [];
    window.customCards.push({
      type: "neo-smartbox-remote-card",
      name: "NEO Smartbox Remote Card",
      description: "A remote control card for NEO Smartbox devices",
    });
    console.log("Added card to window.customCards");
  } catch (error) {
    console.error("Error registering neo-smartbox-remote-card:", error);
  }

  // End of IIFE
})();
