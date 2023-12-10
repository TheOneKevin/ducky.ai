from queue import Queue, Full
from base64 import b64encode
import json

class MessageAnnouncer:
   listeners: list[Queue]

   def __init__(self):
      self.listeners = []

   def listen(self) -> Queue:
      q = Queue(maxsize=8196)
      self.listeners.append(q)
      return q

   def announce(self, data: str, event=None):
      # We don't follow the event-stream spec here because we want to be able
      # to tell when an event happens but the client missed it. We do this by
      # omitting the 'event: ' field from the SSE payload and instead form it
      # as a JSON object with the event name as a field.
      data = json.dumps({
         'data': data,
         'event': event
      })
      # Base64 encode the data so that we can send it as a string
      data = b64encode(data.encode('utf-8')).decode('utf-8')
      msg = f'data: {data}\n\n'
      for i in reversed(range(len(self.listeners))):
         try:
            self.listeners[i].put_nowait(msg)
         except Full:
            del self.listeners[i]
