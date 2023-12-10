from dataclasses import dataclass, field
from typing import final, AsyncGenerator, Generator, Callable, Literal
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
   model: str | None = None
   system_prompt: str = ''
   document: list[ChatItem] = field(default_factory=list)
   temperature: float = 1.0
   max_tokens: int | None = None
   frequency_penalty: float = 0.0
   presence_penalty: float = 0.0
   request_tokens: int = 0
   completion_tokens: int = 0
   is_final_context: bool = False
   provider: 'IChatProvider | None' = None

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

@dataclass
class ChatHistory:
   """
   Represents the history of a chat session, including all the user/response
   pairs.
   """
   history: list[ChatCompletion] = field(default_factory=list)

   def __iter__(self):
      return iter(self.history)

   def __len__(self):
      return len(self.history)

   def current_completion(self) -> ChatCompletion:
      return self.history[-1]

   def current_context(self) -> ChatContext:
      return self.history[-1].steps[-1]

   def add_completion(self, completion: ChatCompletion) -> ChatCompletion:
      self.history.append(completion)
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

PromptFlowT = Generator[tuple[str, PromptFlowFunctionT], None, None]
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

   def start_flow_stream(self, user_query: str,
                         flow_entry: PromptFlowT) -> PromptFlowIteratorT:
      """
      Given a list of flows, this method will start each flow and yield the
      resulting context and the iterator for the response. The iterator for the
      response should be consumed before the next flow is started, otherwise nothing will work :)
      """
      completion = self.__history.add_completion(ChatCompletion(
         user_query=user_query,
         response='',
         steps=[]
      ))
      for name, fn in flow_entry:
         new_context = fn(self)
         completion.steps.append(new_context)
         if new_context.is_final_context:
            yield (completion, self.continue_context())
         else:
            yield (name, self.continue_context())
         if new_context.is_final_context:
            completion.response = new_context.document[-1].text
   
   async def start_flow(self, user_query: str, flow_entry: PromptFlowT):
      """
      Given a list of flows, this method will start each flow and automatically notify the notifier when a new flow is started.
      """
      flow = self.start_flow_stream(user_query, flow_entry)
      for x, response in flow:
         if type(x) == str:
            self.notifier.notify_flow_step(x)
         elif type(x) == ChatCompletion:
            self.notifier.notify_final_response()
         async for chunk in response:
            if type(x) == ChatCompletion:
               self.notifier.notify_assistant_message(chunk)

   def current_context(self) -> ChatContext:
      """ Returns the current context. """
      context = self.__history.current_context()
      assert context is not None
      return context

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
