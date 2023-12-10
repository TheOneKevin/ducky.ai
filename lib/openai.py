import tiktoken
import openai
from openai import AsyncOpenAI
from .session import ChatGeneratorT, ChatContext, IChatProvider

DEFAULT_MODEL = 'gpt-3.5-turbo-1106'

class OpenAIChatProvider(IChatProvider):
   """
   Do not use. See resolve_provider() instead.
   """

   models: set[str]
   total_reqtoks_ctr: int
   total_cmpltoks_ctr: int
   api_key: str | None
   encoding: tiktoken.Encoding

   def __init__(self, api_key: str | None = None):
      super().__init__()
      self.api_key = api_key
      # Test the API key
      try:
         model_list = openai.models.list().data
         self.models = set([ d.id for d in model_list ])
      except:
         raise ValueError("Invalid OpenAI API key")
      self.total_cmpltoks_ctr = 0
      self.total_reqtoks_ctr = 0
      self.encoding = tiktoken.encoding_for_model(DEFAULT_MODEL)

   def get_num_tokens(self, request: ChatContext) -> int:
      entire_prompt: list[str] = []
      if request.system_prompt:
         entire_prompt.append(request.system_prompt)
      entire_prompt.extend([ x.text for x in request.document ])
      prompt_encoding = self.encoding.encode_batch(entire_prompt)
      prompt_tokens = sum([ len(x) for x in prompt_encoding ])
      # TODO: Add system tokens and other special tokens
      # Let's estimate the special token counts for now...
      if request.system_prompt:
         prompt_tokens += 2
      prompt_tokens += 2 * len(request.document)
      return prompt_tokens

   async def fetch_response(self, request: ChatContext) -> ChatGeneratorT:
      assert len(request.document) > 0, "Empty document"
      # Check if the model exists
      model = request.model or DEFAULT_MODEL
      if model not in self.models:
         raise ValueError(f"Invalid OpenAI model: {model}")
      # Grab the number of prompt tokens
      prompt_tokens = self.get_num_tokens(request)
      self.total_reqtoks_ctr += prompt_tokens
      # Build the prompt
      messages = []
      if request.system_prompt:
         messages.append({
            'role': 'system',
            'content': request.system_prompt
         })
      for doc in request.document:
         if doc.type == 'user':
            messages.append({
               'role': 'user',
               'content': doc.text
            })
         elif doc.type == 'assistant':
            messages.append({
               'role': 'assistant',
               'content': doc.text
            })
      # Send the prompt to OpenAI
      # FIXME: We cannot cache the client... why?
      client = AsyncOpenAI(api_key=self.api_key)
      response = await client.chat.completions.create(
         model=model,
         messages=messages,
         frequency_penalty=request.frequency_penalty,
         presence_penalty=request.presence_penalty,
         max_tokens=request.max_tokens,
         temperature=request.temperature,
         stream=True,
         timeout=10,
      )
      # Now iterate over the response and yield each chunk
      completion_tokens = 0
      async for chunk in response:
         # Update the token counters
         completion_tokens += 1
         self.total_cmpltoks_ctr += 1
         # Yield the chunk
         content = chunk.choices[0].delta.content
         if content is None:
            continue
         yield (content, prompt_tokens, completion_tokens)

   def total_request_tokens(self) -> int:
      return self.total_reqtoks_ctr

   def total_completion_tokens(self) -> int:
      return self.total_cmpltoks_ctr
