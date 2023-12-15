import ChatView from "./views/chat.js";
import AppModel from "./model.js";
import { api } from "./api.js";

class Application {

   /// Properties //////////////////////////////////////////////////////////////

   private _model: AppModel;
   private _view: ChatView;
   private _chatLocked: boolean;

   public get model(): AppModel {
      return this._model;
   }

   public get view(): ChatView {
      return this._view;
   }

   public get chatLocked(): boolean {
      return this._chatLocked;
   }

   private set chatLocked(v: boolean) {
      this._chatLocked = v;
      this.view.setSendDisabled(v);
   }

   constructor() {
      this._model = new AppModel();
      this._view = new ChatView();
      this._chatLocked = false;
   }

   /// App control functions ////////////////////////////////////////////////////

   /**
    * Sends a chat message to the server. Will not perform any validation.
    * @param message The message to send.
    * @returns Resolves when the response is finished streaming.
    */
   public async sendChat(message: string) {
      const isLocked = this.chatLocked;
      this.chatLocked = true;
      this._model.messages.push({
         type: 'user',
         message: message,
         children: []
      });
      this._model.messages.push({
         type: 'assistant',
         message: '',
         children: [],
         tag: 'Thinking...'
      });
      await this.view.render();
      await api.session_send(message);
      await this.model.updateFromServer();
      await this.view.render();
      this.chatLocked = isLocked;
   }

   /**
    * Sets the flow for the current session.
    * @param id The ID of the flow to set.
    */
   public async setFlow(id: string) {
      const isLocked = this.chatLocked;
      this.chatLocked = true;
      this.view.clearSelectedFlow();
      await api.session_flow(id);
      await this.model.updateFromServer();
      await this.view.render();
      this.chatLocked = isLocked;
   }

   /**
    * Starts a new chat session.
    */
   public async newChat() {
      const flowId = this.model.flow_id
      const isLocked = this.chatLocked;
      this.chatLocked = true;
      await api.session_new();
      if (flowId)
         await this.setFlow(flowId);
      else {
         await this.model.updateFromServer();
         await this.view.render();
      }
      this.chatLocked = isLocked;
   }

   /**
    * Reloads the flows list from the server, then reloads the page.
    */
   public async reloadFlows() {
      this.chatLocked = true;
      await api.flows_reload();
      window.location.reload();
   }

   /**
    * Puts the application into an error state.
    * @param message The error message.
    * @param details The details of the error (HTML element).
    * @param callback Called when the modal is constructed.
    */
   public enterErrorState(
      message: string,
      details: HTMLElement,
      callback?: () => void
   ) {
      console.error('Something bad has happened!', message);
      // Enter the error state
      this.chatLocked = true;
      // Disable all the buttons except the modal buttons
      document.querySelectorAll<HTMLButtonElement>("button").forEach(button => {
         button.disabled = true;
      });
      document.querySelectorAll<HTMLButtonElement>(".modal button").forEach(button => {
         button.disabled = false;
      });
      // Show the modal
      this.view.showErrorModal(message, details, callback);
   }
}

/// The global application object.
const app = new Application();

export default app;
