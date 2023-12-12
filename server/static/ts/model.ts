/// The UI model for the application.

import { api } from './api.js';

/**
 * A single message step.
 */
export type MessageStepT = {
   type: 'user' | 'system' | 'assistant';
   message: string;
}

/**
 * A single chat completion, which may contain multiple steps.
 */
export type MessageT = {
   type: 'user' | 'assistant';
   message: string;
   children: MessageStepT[][];
   tag?: string | null;
}

/**
 * The application model, can be updated from the server.
 */
class AppModel {
   id: string;
   flow_id: string;
   messages: MessageT[];

   constructor() {
      this.id = '';
      this.flow_id = '';
      this.messages = [];
   }

   public async updateFromServer() {
      const data = await api.session_model();
      this.id = data.id;
      this.flow_id = data.flow_id;
      this.messages = data.messages;
   }

   public lastMessage() {
      return this.messages[this.messages.length - 1];
   }
}

export default AppModel;
