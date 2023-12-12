from time import sleep
from lib import ChatGeneratorT, ChatContext, IChatProvider

LOREM_IPSUM_TEXT = """
Totam rem aperiam, **eaque ipsa quae ab illo** inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo **enim** ipsam voluptatem quia voluptas:
- sit aspernatur aut `odit` aut fugit `diffpass`
- sed quia consequuntur magni dolores eos `quack`
- qui ratione voluptatem sequi nesciunt `viewcfg`.
"""

class DummyChatProvider(IChatProvider):
   """
   Do not use. See resolve_provider() instead.
   """
   
   def __init__(self, delay: float = 0.05):
      self.delay = delay
   
   async def fetch_response(self, request: ChatContext) -> ChatGeneratorT:
      x, y = 6232, 9232
      assert len(request.document) > 0, "No questions to ask"
      for chunk in LOREM_IPSUM_TEXT.strip().split(' '):
         yield (chunk, x, y)
         sleep(self.delay)
         yield(' ', x, y)

   def total_request_tokens(self) -> int:
      return 69696

   def total_completion_tokens(self) -> int:
      return 6969
