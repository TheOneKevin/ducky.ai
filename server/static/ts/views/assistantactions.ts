/// This file contains the classes that represent the actions that can be
/// performed on a chat message. This is the small icons that appear on the
/// bottom left of a chat message when you hover over it.

import { querySelectorSafe, replaceFeatherIconsIn } from "../utils.js";

/**
 * Actions associated with an assistant message.
 */
export class AssistantActionsView {
   private step_label: HTMLSpanElement;
   private current_step: number | null;
   private parent: string;
   private btn_prev: HTMLSpanElement;
   private btn_next: HTMLSpanElement;
   private btn_copy: HTMLSpanElement;
   private btn_details: HTMLSpanElement;
   private btn_ref: HTMLSpanElement;
   private clone: DocumentFragment;

   constructor(parent: string, numrefs: string) {
      this.current_step = null;
      this.parent = parent;

      const clone =
         querySelectorSafe<HTMLTemplateElement>("#template-chat-actions")
            .content.cloneNode(true) as DocumentFragment;
      this.clone = clone;

      this.btn_copy = clone.querySelector<HTMLSpanElement>("span[data-id='copy']")!;
      this.btn_details = clone.querySelector<HTMLSpanElement>("span[data-id='details']")!;
      this.btn_prev = clone.querySelector<HTMLSpanElement>("span[data-id='prev']")!;
      this.step_label = clone.querySelector<HTMLSpanElement>("span[data-id='step-label']")!;
      this.btn_next = clone.querySelector<HTMLSpanElement>("span[data-id='next']")!;
      this.btn_ref = clone.querySelector<HTMLSpanElement>("span[data-id='ref']")!;

      replaceFeatherIconsIn(clone);

      this.btn_copy.onclick = this.onCopyClick.bind(this);
      this.btn_details.onclick = this.onShowDetailsClick.bind(this);
      this.btn_prev.onclick = this.onPrevStepClick.bind(this);
      this.btn_next.onclick = this.onNextStepClick.bind(this);
      this.btn_ref.querySelector("span").textContent = `Used ${numrefs} references`

      if (numrefs == "0")
         this.btn_ref.classList.add("disabled");
      else {
         this.btn_ref.onclick = this.onRefClick.bind(this);
      }
   }

   public get() {
      return this.clone.childNodes as unknown as HTMLElement[];
   }

   private updateSelectedStep() {
      if (this.current_step === null)
         this.current_step = this.getChildren().length - 1;
      // Clamp index to the range [0, children.length-1]
      this.current_step = Math.max(0, Math.min(
         this.current_step, this.getChildren().length - 1
      ));
      for (let i = 0; i < this.getChildren().length; i++) {
         const child = this.getChildren()[i];
         if (i == this.current_step) {
            child.classList.remove("hide");
         } else {
            child.classList.add("hide");
         }
      }
      this.step_label.textContent =
         `Prompt step ${this.current_step + 1}/${this.getChildren().length}`;
   }

   private onPrevStepClick() {
      if (this.current_step != null)
         this.current_step--;
      this.updateSelectedStep();
   }

   private onNextStepClick() {
      if (this.current_step != null)
         this.current_step++;
      this.updateSelectedStep();
   }

   private onCopyClick() {
   }

   private onShowDetailsClick() {
      const children = this.getChildren();
      const message = document.getElementById(this.parent);
      if (children.length == 0 || message == null)
         return;
      if (message.classList.contains("chat-message--expanded"))
         this.hideAll();
      else {
         this.current_step = null;
         this.updateSelectedStep();
      }
      message.classList.toggle("chat-message--expanded");
      this.btn_prev.classList.toggle("hide");
      this.step_label.classList.toggle("hide");
      this.btn_next.classList.toggle("hide");
   }

   private onRefClick() {
      document.querySelector(
         `#chat-message-list > div.chat-message-reference[data-parent="${this.parent}"]`
      ).classList.toggle("hide");
   }
   
   private getChildren() {
      return document.querySelectorAll(
         `#chat-message-list > div:not(.chat-message-reference)[data-parent="${this.parent}"]`
      );
   }

   private hideAll() {
      this.getChildren().forEach(child => {
         child.classList.add("hide");
      });
   }
}
