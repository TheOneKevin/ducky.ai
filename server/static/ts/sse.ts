/// Server-Sent Events (SSE) client-side handling
/// See private/libprompter/notify.py for the server-side interface
/// See notify.py for the server-side implementation
/// See sse.py for a caveat note on the implementation of SSE

import app from "./app.js";

function on_ping(data: any) {
   console.log('Ping received: ' + data);
}

function on_assistant_message(data: any) {
   app.model.lastMessage().message += data;
   app.view.messageView.updateLastMessage();
   app.view.messageView.scrollToBottom();
}

function on_flow_step(data: any) {
   app.model.lastMessage().message += `<b>Running prompt:</b> ${data}...<br />`;
   app.view.messageView.updateLastMessage();
   app.view.messageView.scrollToBottom();
}

function on_notify_search(data: any) {
   app.model.lastMessage().message += `<b>Searching:</b> ${data}...<br />`;
   app.view.messageView.updateLastMessage();
   app.view.messageView.scrollToBottom();
}

function on_notify_final_response_start(_: any) {
   app.model.lastMessage().message = '';
   app.view.messageView.updateLastMessage();
   app.view.messageView.scrollToBottom();
}

const event_src = new EventSource("/api/listen");

/**
* Register the SSE (Server-Sent Events) handlers
*/
export function registerSSEHandlers() {
   const handlers = {
      'ping': on_ping,
      'assistant': on_assistant_message,
      'flow-step': on_flow_step,
      'vector-search': on_notify_search,
      'final-response-start': on_notify_final_response_start,
   }
   event_src.onmessage = (event) => {
      // Grab the event data and base64-decode it, then parse it as JSON
      const data = JSON.parse(atob(event.data));
      // The event name and data will always be present
      const event_name = data['event'];
      const event_data = data['data'];
      // Call the appropriate handler
      if (event_name in handlers) {
         handlers[event_name](event_data);
      } else {
         console.log("Unhandled event", data);
      }
   }
}
