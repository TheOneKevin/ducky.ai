import app from "./app.js";
import { registerSSEHandlers } from "./sse.js";

// Register window events here

window.onload = async () => {
   registerSSEHandlers();
   await app.model.updateFromServer();
   app.view.render();
};

window.onclick = (e: Event) => {
   if (e.target != app.view.c.btnSelectFlow) {
      app.view.toggleFlowDropdown(false);
   }
}

// For debugging purposes
// @ts-ignore
window.app = app;
