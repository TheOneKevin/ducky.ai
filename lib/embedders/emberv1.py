"""
This is a wrapper around LLMRails/emberv1 model.

See: https://huggingface.co/llmrails/ember-v1

Citations:

N/A

"""

import torch
from lib import IEmbedder
from transformers import AutoTokenizer, AutoModel

def _average_pool(last_hidden_states, attention_mask):
   last_hidden = last_hidden_states.masked_fill(
      ~attention_mask[..., None].bool(), 0.0)
   return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

class EmberV1Embedder(IEmbedder):
   def __init__(self):
      self.model = AutoModel.from_pretrained('llmrails/ember-v1')
      self.tokenizer = AutoTokenizer.from_pretrained('llmrails/ember-v1')

   def embed_nl_query(self, data: list[str]):
      return self._run_batch(data)

   def embed_nl_key(self, data: list[str]):
      return self._run_batch(data)

   def _run_batch(self, data: list[str]):
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

__all__ = ['EmberV1Embedder']
