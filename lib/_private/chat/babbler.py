from time import sleep
from lib import ChatGeneratorT, ChatContext, IChatProvider

LOREM_IPSUM_TEXT = """
Totam rem aperiam, **eaque ipsa quae ab illo** inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo **enim** ipsam voluptatem quia voluptas:
1. sit aspernatur aut `odit` aut `fugit`
2. sed quia consequuntur magni dolores eos `quack`
3. qui ratione `voluptatem` sequi nesciunt
"""

class DummyChatProvider(IChatProvider):
   def __init__(self, delay: float = 0.05):
      self.delay = delay

   async def fetch_response(self, request: ChatContext) -> ChatGeneratorT:
      x, y = 6232, 9232
      assert len(request.document) > 0, "No questions to ask"
      for chunk in LOREM_IPSUM_TEXT.strip().split(' '):
         yield (chunk, x, y)
         sleep(self.delay)
         yield (' ', x, y)

   def total_request_tokens(self) -> int:
      return 69696

   def total_completion_tokens(self) -> int:
      return 6969
