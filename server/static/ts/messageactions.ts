/// This file contains the classes that represent the actions that can be
/// performed on a chat message. This is the small icons that appear on the
/// bottom left of a chat message when you hover over it.

/**
 * Actions associated with an assistant message.
 */
export class AssistantActions {
   private step_label: HTMLSpanElement;
   private current_step: number | null;
   private parent: string;
   private btn_prev: HTMLSpanElement;
   private btn_next: HTMLSpanElement;
   private btn_copy: HTMLSpanElement;
   private btn_details: HTMLSpanElement;
   private btn_link: HTMLSpanElement;

   constructor(parent: string) {
      this.step_label = createLabel("Step");
      this.current_step = null;
      this.parent = parent;
      this.btn_prev = createButtons("arrow-left", "Previous step", this.onPrevStepClick.bind(this));
      this.btn_next = createButtons("arrow-right", "Next step", this.onNextStepClick.bind(this));
      this.btn_copy = createButtons("clipboard", "Copy", this.onCopyClick.bind(this));
      this.btn_details = createButtons("layers", "Show prompt flow", this.onShowDetailsClick.bind(this));
      this.btn_link = createButtons("link", "Show references", null);
      this.btn_prev.classList.add("hide");
      this.step_label.classList.add("hide");
      this.btn_next.classList.add("hide");
   }

   public get(): HTMLSpanElement[] {
      return [
         this.btn_copy, this.btn_details, this.btn_link,
         this.btn_prev, this.step_label, this.btn_next,
      ]
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

   private getChildren() {
      return document.querySelectorAll(
         `#chat-message-list > div[data-parent="${this.parent}"]`
      );
   }

   private hideAll() {
      this.getChildren().forEach(child => {
         child.classList.add("hide");
      });
   }
}

/**
 * Actions associated with a user message.
 */
export class UserActions {
   private btn_edit: HTMLSpanElement;
   constructor() {
      this.btn_edit = createButtons("edit-2", "Edit", null);
   }
   public get(): HTMLSpanElement[] {
      return [this.btn_edit]
   }
}

function createButtons(
   iconName: feather.FeatherIconNames, text: string,
   onclick: ((this: GlobalEventHandlers, ev: MouseEvent) => any) | null
): HTMLSpanElement {
   const span = document.createElement("span");
   // @ts-ignore
   const icon = feather.icons[iconName].toSvg({
      'stroke-width': 2.5
   });
   span.classList.add("btn-small-icons");
   span.classList.add("tooltip-bottom");
   span.innerHTML += icon;
   span.dataset.tooltip = text;
   span.onclick = onclick;
   return span;
}

function createLabel(text: string): HTMLSpanElement {
   const span = document.createElement("span");
   span.classList.add("label");
   span.innerText = text;
   return span;
}
