import asyncio
import lib as lp
from uuid import uuid4
from dataclasses import dataclass
from typing import Literal
from .notify import ChatNotifier
from dataclasses import asdict

global_sessions: dict[str, 'ChatSessionWrapper'] = {}
global_flows: list[lp.FlowDescriptor]

@dataclass
class ChatSessionItem:
   type: Literal['user', 'assistant', 'system']
   message: str
   children: list['ChatSessionItem']
   tag: str | None = None

class ChatSessionWrapper:
   """
   Wrapper class for the chat session. This is used to store the chat session
   and its history, and to serialize it into a JSON-serializable format.
   """

   id: str
   session: lp.ChatSession
   selected_flow: lp.FlowDescriptor

   def __init__(self, id: str):
      self.id = id
      self.session = lp.ChatSession(notifier=ChatNotifier())
      self.selected_flow = get_flows()[0]

   def serialize(self) -> dict:
      """
      Serializes the chat session into a list of ChatSessionItem objects.
      This is used to send the chat history to the client.
      See also: static/renderer.js and render_chat_messages().
      """
      result: list[ChatSessionItem] = []
      for item in self.session.history:
         outer_steps = []
         for step in item.steps:
            steps = []
            if step.system_prompt != '':
               steps.append(ChatSessionItem(
                  type='system',
                  message=step.system_prompt,
                  children=[]
               ))
            for chatitem in step.document:
               steps.append(ChatSessionItem(
                  type=chatitem.type,
                  message=chatitem.text,
                  children=[]
               ))
            if len(steps) > 0:
               outer_steps.append(steps)
         result.append(ChatSessionItem(
            type='user',
            message=item.user_query,
            children=[]))
         result.append(ChatSessionItem(
            type='assistant',
            tag=_find_flow_name_by_id(item.flow_id),
            message=item.response,
            children=outer_steps))
      return {
         'id': self.id,
         'flow_id': self.selected_flow.id,
         'messages': [asdict(item) for item in result]
      }

   def send_message(self, message: str) -> str | None:
      """
      Sends a message to the chat session.
      """
      return asyncio.run(self.__send_message_safe(message))
   
   def select_flow(self, id: str) -> None:
      """
      Selects a flow by its id.
      """
      for flow in get_flows():
         if flow.name == id:
            self.selected_flow = flow
            return
      raise ValueError(f'No flow with id {id} exists')
   
   async def __send_message_safe(self, message: str) -> str | None:
      """
      Exception-safe wrapper for send_message so asyncio doesn't crash!
      """
      try:
         await self.session.start_flow(message, self.selected_flow)
      except Exception as e:
         # FIXME: Better error messages
         return f'Error {type(e)}: {e}'
      return None

def _find_flow_name_by_id(id: str | None) -> str | None:
   """
   Finds a flow by its id.
   """
   for flow in get_flows():
      if flow.id == id:
         return flow.name
   return None

def get_session(sessionid: str) -> ChatSessionWrapper:
   """
   Gets a session by its id.
   """
   global global_sessions
   if sessionid not in global_sessions:
      raise ValueError(f'No session with id {sessionid} exists')
   return global_sessions[sessionid]

def session_exists(sessionid: str | None) -> bool:
   """
   Checks if a session exists by its id.
   """
   global global_sessions
   if sessionid is None:
      return False
   return sessionid in global_sessions

def new_session() -> ChatSessionWrapper:
   """
   Creates a new session.
   """
   global global_sessions
   sessionid = str(uuid4())
   global_sessions[sessionid] = ChatSessionWrapper(id=sessionid)
   return global_sessions[sessionid]

def get_flows() -> list[lp.FlowDescriptor]:
   """
   Gets the list of flows.
   """
   global global_flows
   return global_flows

def reload_flows() -> None:
   """
   Reloads the list of flows.
   """
   global global_flows
   # Grab the flows from the resolver
   global_flows = lp.resolve_flows()
   # Sort the flows by name
   global_flows.sort(key=lambda x: x.name)

reload_flows()

__all__ = [
   'ChatSessionWrapper',
   'get_session',
   'session_exists',
   'new_session',
   'get_flows',
   'reload_flows'
]
