"""
Internal module to handle chat sessions and contexts.
"""

from dataclasses import dataclass, field
from typing import final, AsyncGenerator, Generator, Callable, Literal, Any
from .notify import IChatNotifier
from abc import ABC, abstractmethod

ChatGeneratorT = AsyncGenerator[tuple[str, int, int], None]
"""
A generator that yields strings (chunks of the response) and returns a tuple of
(request_tokens, completion_tokens) where request_tokens is the number of 
tokens in the request and completion_tokens is the number of tokens in the 
response.
"""

@dataclass
class ReferenceItem:
   """ Represents a single reference item. """
   type: Literal['text']  # TODO: add more types later
   data: str
   url: str

@dataclass
class ChatItem:
   """ Represents a single chat item. """
   type: Literal['user', 'assistant']
   text: str

@dataclass
class ChatContext:
   """
   Represents the context of a chat session. This includes the system prompt,
   the list of questions asked, the list of responses given, etc.
   """

   provider: 'IChatProvider'
   """
   The provider that is used to fetch responses. You should use resolve_provider
   to get a provider.
   """

   document: list[ChatItem]
   """
   The document is a list of chat items. Each chat item is either a user
   message or an assistant message. The document is updated after every request.
   """

   is_final_context: bool = False
   """
   If this is set to True, then the context is considered "final" and the
   session will stop after this context is processed.
   """

   model: str | None = None
   """
   The model that is used to generate responses. If this is None, then the
   default model is used. This is consumed by the chat provider.
   """

   system_prompt: str = ''
   """
   The system prompt is the prompt that is sent to the chat provider to generate
   a response.
   """

   temperature: float = 1.0
   max_tokens: int | None = None
   frequency_penalty: float = 0.0
   presence_penalty: float = 0.0

   request_tokens: int = 0
   """
   The number of tokens used in the request. This is updated after every request.
   """

   completion_tokens: int = 0
   """
   The number of tokens used in the response. This is updated after every request.
   """

   user_data: dict[str, Any] = field(default_factory=dict)
   """
   A dictionary that can be used to store user data. This is useful for
   keeping track of a stateful conversation.
   """

   def fetch_response(self) -> 'ChatGeneratorT':
      """ Do not use. See ChatContext.continue_context instead. """
      if self.provider is None:
         raise ValueError('Cannot fetch response without a provider')
      return self.provider.fetch_response(self)

@dataclass
class ChatCompletion:
   """
   Represents a user/response pair, including all the intermediate prompting
   steps that generated the response.
   """
   user_query: str = ''
   response: str = ''
   steps: list[ChatContext] = field(default_factory=list)
   flow_id: str | None = None
   references: list[ReferenceItem] = field(default_factory=list)

class ChatHistory:
   """
   Represents the history of a chat session, including all the user/response
   pairs.
   """
   __history: list[ChatCompletion]

   def __init__(self, history: list[ChatCompletion] | None = None):
      if history is None:
         self.__history = []
      else:
         self.__history = history

   def __iter__(self):
      return iter(self.__history)

   def __len__(self):
      return len(self.__history)

   def _current_completion(self) -> ChatCompletion:
      """ Used by ChatSession. Do not use. """
      return self.__history[-1]

   def _current_context(self) -> ChatContext:
      """ Used by ChatSession. Do not use. """
      return self.__history[-1].steps[-1]

   def _add_completion(self, completion: ChatCompletion) -> ChatCompletion:
      """ Used by ChatSession. Do not use. """
      self.__history.append(completion)
      return completion

class IChatProvider(ABC):
   """
   IChatProvider is a class that can provide responses to a given context. For
   example, IChatProvider could be a class that uses OpenAI's API to generate
   responses to a given context. The provider is usually stateful (due to
   authentication), hence the need for a session class (instead of just the
   fetch_response function).
   """

   @abstractmethod
   def fetch_response(self, request: ChatContext) -> ChatGeneratorT:
      """
      DO NOT CALL THIS METHOD DIRECTLY. Instead, use the ChatSession class.
      This method should yield the response text in chunks. At the end of the
      method, the context should NOT be updated with the response.
      """
      raise NotImplementedError()

   @abstractmethod
   def total_request_tokens(self) -> int:
      """ Returns the total number of tokens used in requests. """
      raise NotImplementedError()

   @abstractmethod
   def total_completion_tokens(self) -> int:
      """ Returns the total number of tokens used in responses. """
      raise NotImplementedError()

PromptFlowFunctionT = Callable[['ChatSession'], ChatContext]
"""
A function that takes in a ChatSession and returns a ChatContext.
"""

PromptFlowT = Generator[tuple[str, ChatContext], None, None]
"""
A generator that yields tuples of (name, function) where name is the name of
the flow step and function is the function that generates the context for that
step.
"""

ChatIteratorT = AsyncGenerator[str, None]
"""
A generator that yields strings (chunks of the response).
"""

PromptFlowIteratorT = Generator[
   tuple[ChatCompletion | str, ChatIteratorT], None, None]
"""
A generator that yields tuples of (completion, iterator) where completion is
the current completion and iterator is the iterator for the response. See
ChatSession.start_flow for more information.
"""

@dataclass
class FlowDescriptor:
   """
   A class that describes a flow. This should only be instantiated by the
   resolve_flows() function. If you need to invoke a flow given the generator
   PromptFlowT directly, just use the start_flow_raw() method.
   """
   id: str
   name: str
   description: str
   entry: Callable[['ChatSession'], PromptFlowT]

@final
class ChatSession():
   """
   ChatSession is a class that represents a chat session. It is stateful and
   keeps track of the current context and the history of contexts. It also
   provides methods to start a new context, continue the current context, etc.
   """

   __history: ChatHistory
   __notifier: IChatNotifier

   def __init__(self, notifier: IChatNotifier):
      self.__history = ChatHistory()
      self.__notifier = notifier

   @property
   def history(self) -> ChatHistory:
      """ Returns the history of the chat session. """
      return self.__history

   @property
   def notifier(self) -> IChatNotifier:
      """ Returns the notifier for the chat session. """
      return self.__notifier

   def __start_flow_stream(self, user_query: str,
                           flow_entry: PromptFlowT) -> PromptFlowIteratorT:
      """
      Given a flow generator, this method will start each flow and yield the
      resulting context and the iterator for the response. The iterator for the
      response should be consumed before the next flow is started, otherwise
      nothing will work :)
      """
      completion = self.__history._add_completion(ChatCompletion(
         user_query=user_query,
         response='',
         steps=[],
         flow_id=getattr(flow_entry, 'flow_id', None)
      ))
      for name, new_context in flow_entry:
         completion.steps.append(new_context)
         if new_context.is_final_context:
            yield (completion, self.continue_context())
         else:
            yield (name, self.continue_context())
         if new_context.is_final_context:
            completion.response = new_context.document[-1].text

   async def start_flow_raw(self, user_query: str, flow_entry: PromptFlowT):
      """
      Given a flow generator, this method will start each flow and
      automatically notify the notifier when a new flow is started.
      """
      flow = self.__start_flow_stream(user_query, flow_entry)
      for x, response in flow:
         if type(x) == str:
            self.notifier.notify_flow_step(x)
         elif type(x) == ChatCompletion:
            self.notifier.notify_final_response()
         async for chunk in response:
            if type(x) == ChatCompletion:
               self.notifier.notify_assistant_message(chunk)

   async def start_flow(self, user_query: str, flow_entry: FlowDescriptor):
      """
      Given a flow descriptor, start the flow. See start_flow_raw and
      start_flow_stream for more information.
      """
      await self.start_flow_raw(user_query, flow_entry.entry(self))
      self.current_completion().flow_id = flow_entry.id

   def current_context(self) -> ChatContext:
      """ Returns the current context. """
      context = self.__history._current_context()
      assert context is not None
      return context

   def current_completion(self) -> ChatCompletion:
      """ Returns the current completion. """
      completion = self.__history._current_completion()
      assert completion is not None
      return completion

   async def continue_context(self) -> ChatIteratorT:
      """
      Continues the current context by querying the chat provider (i.e.,
      OpenAI's API or otherwise) for a response.
      """
      # Check if the request is valid first
      context = self.current_context()
      if len(context.document) == 0:
         raise ValueError('Cannot continue context with empty chat')
      # If there is already a response "hint", then use that
      has_existing_response = context.document[-1].type == 'assistant'
      response_text = context.document[-1].text if has_existing_response else ''
      if has_existing_response and context.is_final_context:
         yield response_text
      # Ok, it's valid, get the response
      response = context.fetch_response()
      async for chunk, ptokens, ctokens in response:
         response_text += chunk
         # And also the token counts for the context (note this is never
         # cumulative, as contexts are "immutable" in the sense that every new
         # request re-sends the entire context).
         context.request_tokens = ptokens
         context.completion_tokens = ctokens
         yield chunk
      # Update the context now
      if has_existing_response:
         context.document[-1].text = response_text
      else:
         context.document.append(ChatItem(
            type='assistant',
            text=response_text
         ))

__all__ = [
   'ReferenceItem',
   'ChatGeneratorT',
   'ChatContext',
   'ChatItem',
   'ChatCompletion',
   'ChatHistory',
   'IChatProvider',
   'PromptFlowT',
   'PromptFlowFunctionT',
   'PromptFlowIteratorT',
   'ChatIteratorT',
   'ChatSession',
   'FlowDescriptor',
]
