import json
from .sse import MessageAnnouncer
import lib as lp

announcer = MessageAnnouncer()

def get_announcer() -> MessageAnnouncer:
   global announcer
   return announcer

class ChatNotifier(lp.IChatNotifier):
   def notify_assistant_message(self, message: str) -> None:
      get_announcer().announce(data=message, event='assistant')
   def notify_flow_step(self, name: str) -> None:
      get_announcer().announce(data=name, event='flow-step')
   def notify_search(self, query: str) -> None:
      get_announcer().announce(data=query, event='vector-search')
   def notify_final_response(self) -> None:
      get_announcer().announce(data='', event='final-response-start')

__all__ = ['ChatNotifier', 'get_announcer']
