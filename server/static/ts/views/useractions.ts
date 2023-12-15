import { querySelectorSafe, replaceFeatherIconsIn } from "../utils.js";

/**
 * Actions associated with a user message.
 */
export class UserActionsView {
   private clone: DocumentFragment;

   constructor() {
      const clone =
         querySelectorSafe<HTMLTemplateElement>("#template-user-actions")
            .content.cloneNode(true) as DocumentFragment;
      this.clone = clone;
      replaceFeatherIconsIn(clone);
   }

   public get() {
      return this.clone.childNodes as unknown as HTMLElement[];
   }
}
