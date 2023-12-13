"""
Internal module that contains the IChatNotifier interface.
"""

from abc import ABC, abstractmethod

class IChatNotifier(ABC):
   """
   IChatNotifier is an interface that represents a chat notifier. It is used to
   send messages to the client.
   """

   @abstractmethod
   def notify_assistant_message(self, message: str) -> None:
      """ Notifies that a new assistant message chunk has arrived. """
      raise NotImplementedError()

   @abstractmethod
   def notify_flow_step(self, name: str) -> None:
      """ Notifies that a new flow step has begun. """
      raise NotImplementedError()

   @abstractmethod
   def notify_search(self, query: str) -> None:
      """ Notifies that a search query is being performed. """
      raise NotImplementedError()

   @abstractmethod
   def notify_final_response(self) -> None:
      """ Notifies that the final response is being generated. """
      raise NotImplementedError()

__all__ = ['IChatNotifier']
