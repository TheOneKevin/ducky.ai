import app from "../app.js";
import MessageView from "./message.js";
import { querySelectorSafe, waitForDomUpdate } from "../utils.js";

class ChatView {
   /// Properties //////////////////////////////////////////////////////////////

   private _messageView: MessageView;
   public get messageView(): MessageView {
      return this._messageView;
   }
   private chatboxBaseHeight: number;
   private c: Controls;

   constructor() {
      this.c = new Controls();
      this._messageView = new MessageView();
      this.c.taChatbox.onkeydown = this.onChatboxKeydown.bind(this);
      this.c.taChatbox.oninput = this.onChatboxInput.bind(this);
      this.c.btnSend.onclick = this.onSendClick.bind(this);
      this.c.btnSelectFlow.onclick = this.onSelectFlowClick.bind(this);
      this.c.btnNewChat.onclick = async _ => await app.newChat();
      this.c.btnReloadFlows.onclick = async _ => await app.reloadFlows();
      document.querySelectorAll<HTMLElement>(".dropdown-item").forEach(dropdown => {
         dropdown.onclick = this.onDropdownClick.bind(this, dropdown);
      });
   }

   /// Rendering related functions /////////////////////////////////////////////

   /**
    * Clears the chatbox.
    */
   public clearChatbox() {
      this.c.taChatbox.value = "";
      this.onChatboxInput(null);
   }

   /**
    * Clears the selected flow dropdown text.
    */
   public clearSelectedFlow() {
      this.c.pSelectedFlow.textContent = "";
   }

   /**
    * @returns True if the chatbox is empty, false otherwise.
    */
   public isChatboxEmpty() {
      return this.c.taChatbox.value.trim().length == 0;
   }

   /**
    * Sets the disabled state of the send button.
    * @param v If true, the send button will be disabled. If false, the send
    *         button will be enabled.
    */
   public setSendDisabled(v: boolean) {
      if (v) {
         this.c.btnSend.disabled = true;
      } else {
         this.c.btnSend.disabled = this.isChatboxEmpty();
      }
   }

   /**
    * Toggles the flow dropdown.
    * @param force If true, the dropdown will be shown. If false, the dropdown
    *              will be hidden. If undefined, the dropdown will be toggled.
    *              Defaults to undefined.
    */
   public toggleFlowDropdown(force?: boolean) {
      this.posititionDropdown();
      if (force === true) {
         this.c.divFlowDropdown.classList.remove("hide");
         this.c.btnSelectFlow.classList.add("active");
      } else if (force === false) {
         this.c.divFlowDropdown.classList.add("hide");
         this.c.btnSelectFlow.classList.remove("active");
      } else {
         this.c.divFlowDropdown.classList.toggle("hide");
         this.c.btnSelectFlow.classList.toggle("active");
      }
   }

   /**
    * Renders the entire app based on the local model.
    */
   public async render() {
      this.renderSelectedFlow();
      this.messageView.render();
      await waitForDomUpdate();
      this.messageView.scrollToBottom();
   }

   public showErrorModal(
      message: string,
      details: HTMLElement,
      callback?: () => void
   ) {
      // Add the error borders to the chatbox
      this.c.taChatbox.parentElement.classList.add("error");
      this.c.divErrorBanner.classList.remove("hide");
      // Change the modal details
      const modal_title = document.getElementById("modal-1-title");
      const modal_details = document.getElementById("modal-1-content");
      modal_title.innerText = `Error: ${message}`;
      modal_details.innerHTML = "";
      modal_details.appendChild(details);
      if (callback) callback();
   }

   /// Event handlers //////////////////////////////////////////////////////////

   private async onSendClick(_: Event) {
      // Check if the chat is empty, if so, do nothing
      if (this.isChatboxEmpty())
         return;
      // Check if the chat is locked
      if (app.chatLocked)
         return;
      // Send the message to the server
      const message = this.c.taChatbox.value;
      this.clearChatbox();
      await app.sendChat(message);
   }

   private onChatboxKeydown(e: KeyboardEvent) {
      if (e.key == "Enter" && !e.shiftKey) {
         e.preventDefault();
         this.c.btnSend.click();
      } else if (e.key == "Enter" && e.shiftKey) {
         // Do nothing, let the onChatboxInput handler handle it
      } else if (e.key == "Escape") {
         this.c.taChatbox.blur();
      }
   }

   private onChatboxInput(e: Event) {
      // Resize the chatbox
      const elem = this.c.taChatbox;
      const minRows = Number.parseInt(elem.dataset.minRows);
      !this.chatboxBaseHeight && this.getTextAreaHeight();
      elem.rows = minRows;
      const rows = Math.ceil((elem.scrollHeight - this.chatboxBaseHeight) / 21);
      elem.rows = Math.min(minRows + rows, 6);
      // Enable the send button if there is text
      const has_text = elem.value.trim().length > 0;
      if (!app.chatLocked)
         this.c.btnSend.disabled = !has_text;
   }

   private onDropdownClick(self: HTMLElement, _: Event) {
      this.toggleFlowDropdown(false);
      const id = self.dataset.flowid;
      app.setFlow(id);
   }

   private onSelectFlowClick(e: Event) {
      this.toggleFlowDropdown();
      this.c.divFlowDropdown.focus();
      e.stopPropagation();
   }

   /// Random private functions ////////////////////////////////////////////////

   private renderSelectedFlow() {
      const id = app.model.flow_id;
      const dropdown = document.querySelector(`div[data-flowid="${id}"]`);
      const dropdown_title = dropdown.querySelector(".dropdown-title");
      this.c.pSelectedFlow.textContent = dropdown_title.textContent;
   }

   private posititionDropdown() {
      const offsetX = 0;
      const offsetY = 10;
      // Get the x, y of the button
      const rect = this.c.btnSelectFlow.getBoundingClientRect();
      const btn_height = this.c.btnSelectFlow.offsetHeight;
      rect.x += offsetX;
      rect.y += btn_height + offsetY;
      // Set the translate of the dropdown to the button's position
      this.c.divFlowDropdown.style.transform =
         `translate(${rect.x}px, ${rect.y}px)`;
   }

   private getTextAreaHeight() {
      const savedValue = this.c.taChatbox.value;
      this.c.taChatbox.value = "";
      this.chatboxBaseHeight = this.c.taChatbox.scrollHeight;
      this.c.taChatbox.value = savedValue;
   }
}

class Controls {
   taChatbox: HTMLTextAreaElement;
   btnSelectFlow: HTMLButtonElement;
   divFlowDropdown: HTMLDivElement;
   btnNewChat: HTMLButtonElement;
   btnSend: HTMLButtonElement;
   btnReloadFlows: HTMLButtonElement;
   pSelectedFlow: HTMLParagraphElement;
   divChatList: HTMLDivElement;
   divErrorBanner: HTMLDivElement;
   constructor() {
      this.taChatbox = querySelectorSafe<HTMLTextAreaElement>("#ta-chat");
      this.btnSelectFlow = querySelectorSafe<HTMLButtonElement>("#btn-model");
      this.divFlowDropdown = querySelectorSafe<HTMLDivElement>("#dpd-sel-model");
      this.btnNewChat = querySelectorSafe<HTMLButtonElement>("#btn-new-chat");
      this.btnReloadFlows = querySelectorSafe<HTMLButtonElement>("#btn-reload-flows");
      this.btnSend = querySelectorSafe<HTMLButtonElement>("#btn-send");
      this.pSelectedFlow = querySelectorSafe<HTMLParagraphElement>("#model-name");
      this.divChatList = querySelectorSafe<HTMLDivElement>("#chat-body");
      this.divErrorBanner = querySelectorSafe<HTMLDivElement>("#error-banner");
   }
}

export default ChatView;
