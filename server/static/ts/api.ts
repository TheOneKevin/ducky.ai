import AppModel from "./model.js";

async function _safe_fetch(
   url: URL, options: RequestInit = {}, error_message: string
): Promise<Response | null> {
   let details: string = "";
   let response: Response;

   // Try to perform the fetch, if no error is thrown, return the response
   try {
      response = await fetch(url.toString(), options);
      if (!response.ok) {
         throw new Error();
      }
      return response;
   } catch (e) {
      if (e instanceof TypeError) {
         details = `TypeError: ${e.message}`;
      }
      if (e instanceof Error) {
         details += `Stack:\n${e.stack}`;
      }
   }

   // Otherwise, we have the message and details
   const result_text = await response.text();

   // If it's error 500, then the server probably returned an HTML
   // page with the error message. We can construct a link to that HTML
   // page and ask the user if they want to see it.
   if (response.status == 500) {
      const iframe = document.createElement("iframe");
      iframe.style.width = "90vw";
      iframe.style.height = "70vh";
      iframe.style.border = "1px solid #ccc";

   } else {

   }
   return null;
}

export namespace api {
   export async function session_model(): Promise<AppModel> {
      const url = new URL("/api/session/model", window.location.origin);
      const response = await _safe_fetch(url, {}, "Could not get session model");
      if (response == null)
         return new AppModel();
      const model = await response.json() as AppModel;
      return model;
   }

   export async function session_send(message: string) {
      // Send the message to the server
      const url = new URL("/api/session/send", window.location.origin);
      await _safe_fetch(url, {
         method: "POST",
         body: JSON.stringify({
            message: message
         }),
         headers: {
            "Content-Type": "application/json"
         }
      }, "Failed to send message");
      // The chat is done streaming here.
   }

   export async function session_new() {
      const url = new URL("/api/session/new", window.location.origin);
      await _safe_fetch(url, {}, "Failed to create new chat");
   }

   export async function session_flow(id: string) {
      const url = new URL(`/api/session/flow/${id}`, window.location.origin);
      await _safe_fetch(url, {
         method: "POST"
      }, `Failed to set flow to: ${id}`);
   }
}
