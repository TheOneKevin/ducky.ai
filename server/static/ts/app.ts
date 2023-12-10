import AppView from "./view.js";
import AppModel from "./model.js";
import { api } from "./api.js";

class Application {

   private _model: AppModel;
   private _view: AppView;
   private _chatLocked: boolean;

   public get model(): AppModel {
      return this._model;
   }

   public get view(): AppView {
      return this._view;
   }

   public get chatLocked(): boolean {
      return this._chatLocked;
   }

   public set chatLocked(v: boolean) {
      this._chatLocked = v;
      this.view.setSendDisabled(v);
   }

   constructor() {
      this._model = new AppModel();
      this._view = new AppView();
      this._chatLocked = false;
   }

   public async sendChat(message: string) {
      this._chatLocked = true;
      this._model.messages.push({
         type: 'user',
         message: message,
         children: []
      });
      this._model.messages.push({
         type: 'assistant',
         message: '',
         children: []
      });
      await this.view.render();
      await api.session_send(message);
      await this.model.updateFromServer();
      await this.view.render();
      this.chatLocked = false;
   }

   public async setFlow(id: string) {
      await api.session_flow(id);
      await this.model.updateFromServer();
      await this.view.render();
   }

   public async newChat() {
      this.chatLocked = true;
      await api.session_new();
      await this.model.updateFromServer();
      await this.view.render();
      this.chatLocked = false;
   }
}

const app = new Application();

export default app;
