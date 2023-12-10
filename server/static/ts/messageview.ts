/// This file contains the MessageView class, which is responsible for
/// rendering the chat messages in the chat list.

import { querySelectorSafe } from "./utils.js";
import type feather from 'feather-icons';
import app from "./app.js";
import { MessageStepT, MessageT } from "./model.js";
import { AssistantActions, UserActions } from "./messageactions.js";

const DUCKY_IMG_SRC = "https://api.dicebear.com/7.x/bottts-neutral/svg?seed=Socks&backgroundColor=fdd835&eyes=frame2&mouth=smile01"
const USER_IMG_SRC = "https://api.dicebear.com/7.x/thumbs/svg?seed=Rocky"
const SYSTEM_IMG_SRC = "https://api.dicebear.com/7.x/shapes/svg?seed=Chester"

// MessageView /////////////////////////////////////////////////////////////////

class MessageView {
   private id_counter: number;
   private c: Controls;

   constructor() {
      this.c = new Controls();
      this.id_counter = 0;
   }

   /**
    * Scrolls the chat list to the bottom.
    */
   public scrollToBottom() {
      this.c.divChatBody.scrollTop = this.c.divChatBody.scrollHeight;
   }

   /**
    * Updates the last message in the chat list based on the app model.
    * Will not clear the chat list before rendering.
    */
   public updateLastMessage() {
      const messages = app.model.messages;
      const messageList = document.querySelectorAll<HTMLDivElement>("#chat-message-list > .chat-message");
      if (messageList.length == 0)
         return;
      const lastMessage = messageList[messageList.length - 1]
         .querySelector<HTMLParagraphElement>(".chat-message-stack > section > p");
      if (!lastMessage) {
         debugger;
         throw new Error("Could not find last message");
      }
      const message = messages[messages.length - 1].message;
      lastMessage.innerHTML = parseMdSafe(message);
   }

   /**
    * Renders the chat messages in the app.model.messages array.
    * Will clear the chat list before rendering.
    * @param render_math Whether to render math in the message
    */
   public render(render_math: boolean = true) {
      this.c.divChatList.innerHTML = "";
      for (let m of app.model.messages) {
         const hasChildren = m.children.length > 0;
         const node = this.createChatMessage(m);
         const nodeDom = node.querySelector<HTMLElement>(".chat-message");
         const id = nodeDom.id;
         nodeDom.dataset.numsteps =
            (hasChildren ? m.children.length : 0).toString();
         this.c.divChatList.appendChild(node);
         for (let i = 0; i < m.children.length; i++) {
            const container = document.createElement("div");
            container.classList.add("chat-message-details");
            for (let child of m.children[i]) {
               const childNode = this.createChatMessage(child, true);
               container.appendChild(childNode);
            }
            container.classList.add("hide");
            container.dataset.parent = id;
            this.c.divChatList.appendChild(container);
         }
         if (render_math) {
            renderMathInElement(nodeDom.querySelector("p.markdown"), {
               delimiters: [
                  { left: '$$', right: '$$', display: true },
                  { left: '$', right: '$', display: false },
                  { left: '\\(', right: '\\)', display: false },
                  { left: '\\[', right: '\\]', display: true }
               ],
               throwOnError: false
            });
         }
      }
   }

   // Private functions ////////////////////////////////////////////////////////

   private getID() {
      return this.id_counter++;
   }

   private createChatMessage(
      m: MessageT | MessageStepT, details: boolean = false
   ) {
      let image: string;
      let author: string;
      let text: string;
      let actions: HTMLSpanElement[] = [];
      const id = this.getID().toString();
      if (m.type === 'user') {
         image = USER_IMG_SRC;
         author = "You";
         text = m.message;
         actions = new UserActions().get();
      } else if (m.type === 'system') {
         image = SYSTEM_IMG_SRC;
         author = "System";
         text = m.message;
      } else if (m.type === 'assistant') {
         image = DUCKY_IMG_SRC;
         author = "Ducky";
         text = m.message;
         actions = new AssistantActions(id).get();
      }
      const node = createChatMessageElem(image, author, text, actions);
      node.querySelector(".chat-message").id = id;
      if (details) {
         node.querySelector(".chat-message-stack > footer").remove();
      }
      return node;
   }
}

class Controls {
   divChatBody: HTMLDivElement;
   divChatList: HTMLDivElement;
   constructor() {
      this.divChatBody = querySelectorSafe<HTMLDivElement>("#chat-body");
      this.divChatList = querySelectorSafe<HTMLDivElement>("#chat-message-list");
   }
}

// Helper functions ////////////////////////////////////////////////////////////

// @ts-ignore Import module
import { marked } from "https://cdn.jsdelivr.net/npm/marked/lib/marked.esm.js";
// @ts-ignore Import module
import renderMathInElement from "https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.mjs";

function parseMdSafe(md: string): string {
   // @ts-ignore
   return DOMPurify.sanitize(marked.parse(md));
}

function createChatMessageElem(
   image: string, author: string, message: string, actions: HTMLSpanElement[]
) {
   const template = querySelectorSafe<HTMLTemplateElement>("#template-chat-message");
   const clone = template.content.cloneNode(true) as DocumentFragment;
   clone.querySelector<HTMLImageElement>("img").src = image;
   clone.querySelector(".chat-message-stack > header").textContent = author;
   clone.querySelector(".chat-message-stack > section > p")
      .innerHTML = parseMdSafe(message);
   if (actions.length > 0)
      clone.querySelector(".chat-message-stack > footer")
         .replaceChildren(...actions);
   return clone;
}

export default MessageView;
