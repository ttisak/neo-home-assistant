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

      const deviceName =
        stateObj?.attributes.friendly_name || entityId || "NEO Smartbox";

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

        /* Header */
        .card-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 16px;
        }
        .card-title {
          font-size: 18px;
          font-weight: 500;
          color: lightgray;
        }

        /* Power Button */
        .power-button {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: linear-gradient(135deg, #2B2B2E, #2B2B2E);
          display: flex
      ;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
          transition: transform 0.1s;
        }
        .power-button:hover {
          transform: scale(1.05);
        }
        .power-button svg {
          fill: deepskyblue;
          width: 24px;
          height: 24px;
        }

        /* Remote Container */
        .remote-container {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 24px;
        }

        /* Media Controls */
        .media-controls {
          width: 50%;
          height: 60px;
          border-radius: 32px;
          background-color: #2B2B2E;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 20px;
        }
        .media-button {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background-color 0.2s;
          border-radius: 50%;
        }
        .media-button:hover {
          background-color: #3a3a3a;
        }
        .media-button svg {
          fill: deepskyblue;
          width: 24px;
          height: 24px;
        }
        .play-pause {
          width: 70px;
          height: 70px;
          border-radius: 50%;
          background: linear-gradient(135deg, deepskyblue, #8DAFFF);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
          transition: transform 0.1s;
        }
        .play-pause:hover {
          transform: scale(1.05);
        }
        .play-pause svg {
          margin-right: -4px;
          fill: #005391;
          width: 48px;
          height: 28px;
        }


        /* D-Pad */
        .dpad {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          grid-template-rows: repeat(3, 1fr);
          width: 200px;
          height: 200px;
          position: relative;
          border-radius: 50%;
          background: #2B2B2E;
        }
        .dpad-button {
          width: 66px;
          height: 66px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background-color 0.2s;
          border-radius: 50%;
        }
        .dpad-button:hover {
          background-color: #3a3a3a;
        }
        .dpad-button svg {
          fill: deepskyblue;
          width: 26px;
          height: 26px;
        }
        .dpad-center {
          grid-column: 2;
          grid-row: 2;
          width: 90px;
          height: 90px;
          border-radius: 50%;
          border: 3px solid black;
          display: flex;
          align-items: center;
          justify-content: center;
          position: absolute;
          top: -14px;
          left: -14px;
          background-color: #2B2B2E;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        .dpad-center:hover {
          background-color: rgba(0, 0, 0, 0.4);
        }
        .dpad-center-text {
          color: deepskyblue;
          font-size: 24px;
          font-weight: bold;
        }

        /* Navigation Buttons */
        .nav-row {
          display: flex;
          justify-content: space-between;
          width: 50%;
          margin-top: 16px;
        }
        .nav-button {
          width: 53px;
          height: 53px;
          border-radius: 50%;
          background-color: #2B2B2E;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        .nav-button:hover {
          background-color: #3a3a3a;
        }
        .nav-button svg {
          fill: deepskyblue;
          width: 24px;
          height: 24px;
        }

        /* Voice Controls */
        .voice-controls {
          width: 50%;
          height: 60px;
          border-radius: 32px;
          background-color: #2B2B2E;
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0 20px;
          margin-top: 16px;
        }
        .voice-button {
          width: 48px;
          height: 48px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: background-color 0.2s;
          border-radius: 50%;
        }
        .voice-button:hover {
          background-color: #3a3a3a;
        }
        .voice-button svg {
          fill: deepskyblue;
          width: 24px;
          height: 24px;
        }
        .mic-button {
          width: 70px;
          height: 70px;
          border-radius: 50%;
          background: linear-gradient(135deg, deepskyblue, #8DAFFF);
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);
          transition: transform 0.1s;
        }
        .mic-button:hover {
          transform: scale(1.05);
        }
        .mic-button svg {
          fill: #005391;
          width: 28px;
          height: 28px;
        }

      </style>

      <ha-card>
        <div class="card-header">
          <div class="card-title">${deviceName.substring(
            0,
            deviceName.length / 2,
          )}</div>
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
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#e3e3e3"><path d="M0 0h24v24H0V0z" fill="none"/>
              <path d="M18 9.86v4.28L14.97 12 18 9.86m-9 0v4.28L5.97 12 9 9.86M20 6l-8.5 6 8.5 6V6zm-9 0l-8.5 6 8.5 6V6z"/>
            </svg>            </div>
            <div class="play-pause" @click="${() =>
              this._handleAction("play_pause")}">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 1920 960" width="48px" fill="#e3e3e3">
              <g transform="translate(0, 0)">
                  <path d="M320-200v-560l440 280-440 280Zm80-280Zm0 134 210-134-210-134v268Z"/>
              </g>
              <g transform="translate(500, 0)">
                  <path d="M520-200v-560h240v560H520Zm-320 0v-560h240v560H200Zm400-80h80v-400h-80v400Zm-320 0h80v-400h-80v400Zm0-400v400-400Zm320 0v400-400Z"/>
              </g>
              </svg>
            </div>
            <div class="media-button" @click="${() =>
              this._handleAction("forward")}">
              <svg xmlns="http://www.w3.org/2000/svg" enable-background="new 0 0 24 24" height="24px" viewBox="0 0 24 24" width="24px" fill="#e3e3e3"><g><rect fill="none" height="24" width="24"/><rect fill="none" height="24" width="24"/><rect fill="none" height="24" width="24"/></g><g><g/>
                <path d="M15,9.86L18.03,12L15,14.14V9.86 M6,9.86L9.03,12L6,14.14V9.86 M13,6v12l8.5-6L13,6L13,6z M4,6v12l8.5-6L4,6L4,6z"/></g>
              </svg>
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
            <div class="dpad-center" @click="${() => this._handleAction("ok")}">
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
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#e3e3e3"><path d="M0 0h24v24H0V0z" fill="none"/>
              <path d="M10 9V5l-7 7 7 7v-4.1c5 0 8.5 1.6 11 5.1-1-5-4-10-11-11z"/>
              </svg>
            </div>
            <div class="nav-button" @click="${() =>
              this._handleAction("home")}">
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#e3e3e3">
              <path d="M0 0h24v24H0V0z" fill="none"/><path d="M12 5.69l5 4.5V18h-2v-6H9v6H7v-7.81l5-4.5M12 3L2 12h3v8h6v-6h2v6h6v-8h3L12 3z"/>
              </svg>
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
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" width="24px" fill="#e3e3e3"><path d="M0 0h24v24H0V0z" fill="none"/>
              <path d="M16 7.97v8.05c1.48-.73 2.5-2.25 2.5-4.02 0-1.77-1.02-3.29-2.5-4.03zM5 9v6h4l5 5V4L9 9H5zm7-.17v6.34L9.83 13H7v-2h2.83L12 8.83z"/>
              </svg>
            </div>
            <div class="mic-button" @click="${() =>
              this._handleAction("voice_search")}">
              <svg viewBox="0 0 24 24"><path d="M12,2A3,3 0 0,1 15,5V11A3,3 0 0,1 12,14A3,3 0 0,1 9,11V5A3,3 0 0,1 12,2M19,11C19,14.53 16.39,17.44 13,17.93V21H11V17.93C7.61,17.44 5,14.53 5,11H7A5,5 0 0,0 12,16A5,5 0 0,0 17,11H19Z"></path></svg>
            </div>
            <div class="voice-button" @click="${() =>
              this._handleAction("volume_up")}">
              <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" ><path d="M0 0h24v24H0V0z" fill="none"/>
              <path d="M3 9v6h4l5 5V4L7 9H3zm7-.17v6.34L7.83 13H5v-2h2.83L10 8.83zM16.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77 0-4.28-2.99-7.86-7-8.77z"/>
              </svg>
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
          this._handleAction("forward");
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
          this._handleAction("ok");
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

  // Register the custom element
  if (!customElements.get("neo-smartbox-remote-card")) {
    customElements.define("neo-smartbox-remote-card", NeoSmartboxRemoteCard);
    console.log("NEO Smartbox remote card registered");
  } else {
    console.warn("NEO Smartbox remote card already registered");
  }

  // Add card to card picker
  window.customCards = window.customCards || [];
  window.customCards.push({
    type: "neo-smartbox-remote-card",
    name: "NEO Smartbox Remote",
    description: "A card to control your NEO Smartbox device.",
    preview: true,
  });
})();
