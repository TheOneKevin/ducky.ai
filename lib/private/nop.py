from lib import ChatGeneratorT, ChatContext, IChatProvider

class NoOpChatProvider(IChatProvider):
   """
   Do not use. See resolve_provider() instead.
   """
   
   async def fetch_response(self, _: ChatContext) -> ChatGeneratorT:
      yield('', 0, 0)

   def total_request_tokens(self) -> int:
      return 0

   def total_completion_tokens(self) -> int:
      return 0
