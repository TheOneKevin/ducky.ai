import app from "./app.js";
import MessageView from "./messageview.js";
import { querySelectorSafe, waitForDomUpdate } from "./utils.js";

class AppView {
   public c: Controls;
   private _messageView: MessageView;
   public get messageView(): MessageView {
      return this._messageView;
   }
   private _isChatMultiline: boolean = false;

   constructor() {
      this.c = new Controls();
      this._messageView = new MessageView();
      this.c.taChatbox.onkeydown = this.onChatboxKeydown.bind(this);
      this.c.taChatbox.oninput = this.onChatboxInput.bind(this);
      this.c.btnSend.onclick = this.onSendClick.bind(this);
      this.c.btnSelectFlow.onclick = this.onSelectFlowClick.bind(this);
      this.c.btnNewChat.onclick = this.onNewChatClick.bind(this);
      document.querySelectorAll<HTMLElement>(".dropdown-item").forEach(dropdown => {
         dropdown.onclick = this.onDropdownClick.bind(this, dropdown);
      });
   }

   /// Rendering related functions /////////////////////////////////////////////

   public posititionDropdown() {
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

   public clearChatbox() {
      this.c.taChatbox.value = "";
   }

   public isChatboxEmpty() {
      return this.c.taChatbox.value.trim().length == 0;
   }

   public setSendDisabled(v: boolean) {
      if (v) {
         this.c.btnSend.disabled = true;
      } else {
         this.c.btnSend.disabled = this.isChatboxEmpty();
      }
   }

   public toggleFlowDropdown(force?: boolean) {
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

   private renderSelectedFlow() {
      const id = app.model.flow_id;
      const dropdown = document.querySelector(`div[data-flowid="${id}"]`);
      const dropdown_title = dropdown.querySelector(".dropdown-title");
      this.c.pSelectedFlow.textContent = dropdown_title.textContent;
   }

   public async render() {
      this.renderSelectedFlow();
      this.messageView.render();
      await waitForDomUpdate();
      this.messageView.scrollToBottom();
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
      if (this._isChatMultiline || e.key !== "Enter")
         return;
      e.preventDefault();
      if (e.shiftKey) {
         // Shift+Enter: Multiline mode
         this._isChatMultiline = true;
         this.c.taChatbox.value += '\n';
         this.c.taChatbox.rows = 2;
         this.c.taChatbox.wrap = "soft";
      } else {
         // Enter: Send message
         this.c.btnSend.click();
      }
   }

   private onChatboxInput(e: Event) {
      // Remove newlines if not in multiline mode
      if (!this._isChatMultiline)
         this.c.taChatbox.value = this.c.taChatbox.value.replace(/\n/g, '');
      // Set the rows to the number of newlines (max 6)
      this.c.taChatbox.rows = Math.min(
         this.c.taChatbox.value.split('\n').length, 6);
      // But if the rows becomes 1, we disable multiline mode
      if (this.c.taChatbox.rows === 1) {
         this._isChatMultiline = false;
         this.c.taChatbox.wrap = "off";
      }
      // Check if there is non-whitespace text in the textarea
      const has_text = this.c.taChatbox.value.trim().length > 0;
      // Enable the send button if there is text
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

   private async onNewChatClick(_: Event) {
      await app.newChat();
   }
}

class Controls {
   taChatbox: HTMLTextAreaElement;
   btnSelectFlow: HTMLButtonElement;
   divFlowDropdown: HTMLDivElement;
   btnNewChat: HTMLButtonElement;
   btnSend: HTMLButtonElement;
   pSelectedFlow: HTMLParagraphElement;
   divChatList: HTMLDivElement;
   constructor() {
      this.taChatbox = querySelectorSafe<HTMLTextAreaElement>("#ta-chat");
      this.btnSelectFlow = querySelectorSafe<HTMLButtonElement>("#btn-model");
      this.divFlowDropdown = querySelectorSafe<HTMLDivElement>("#dpd-sel-model");
      this.btnNewChat = querySelectorSafe<HTMLButtonElement>("#btn-new-chat");
      this.btnSend = querySelectorSafe<HTMLButtonElement>("#btn-send");
      this.pSelectedFlow = querySelectorSafe<HTMLParagraphElement>("#model-name");
      this.divChatList = querySelectorSafe<HTMLDivElement>("#chat-body");
   }
}

export default AppView;
