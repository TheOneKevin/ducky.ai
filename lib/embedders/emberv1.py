"""
This is a wrapper around LLMRails/emberv1 model.

See: https://huggingface.co/llmrails/ember-v1

Citations:

N/A

"""

from docarray.typing import NdArray
import torch, numpy as np
from lib import (
   IEmbedder,
   load_model_and_tokenizer,
   is_model_cached,
   is_tokenizer_cached
)

def _average_pool(last_hidden_states, attention_mask):
   last_hidden = last_hidden_states.masked_fill(
      ~attention_mask[..., None].bool(), 0.0)
   return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

class EmberV1Embedder(IEmbedder):
   def __init__(self):
      self.model, self.tokenizer = load_model_and_tokenizer(
         'llmrails/ember-v1')

   def embed_nl_query(self, N: int):
      data: list[str] = []
      def append(s: str): data.append(s)
      for _ in range(N):
         yield append
      return self.run_batch(data)

   def embed_nl_key(self, N: int):
      return self.embed_nl_query(N)

   def run_batch(self, data: list[str]):
      if len(data) == 0:
         return np.empty((0, 1024))
      inputs = self.tokenizer(
         data, max_length=512,
         padding=True, truncation=True,
         return_tensors='pt'
      )
      with torch.no_grad():
         outputs = self.model(**inputs)
         # Average pooling
         embeddings = _average_pool(
            outputs.last_hidden_state, inputs['attention_mask']
         )
         # Normalize embeddings
         embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
      return embeddings.detach().numpy()

   def vector_type(self) -> NdArray:
      return NdArray[1024,]  # type: ignore

   @classmethod
   def is_cached(cls) -> bool:
      return is_model_cached('llmrails/ember-v1') and is_tokenizer_cached('llmrails/ember-v1')

__all__ = ['EmberV1Embedder']
