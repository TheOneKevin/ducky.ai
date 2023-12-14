"""
This is a wrapper for the BAII/bge-* class of embedders.

See: https://huggingface.co/BAAI/llm-embedder
See: https://github.com/xlang-ai/instructor-embedding

Citations:

@misc{bge_embedding,
   title={C-Pack: Packaged Resources To Advance General Chinese Embedding}, 
   author={Shitao Xiao and Zheng Liu and Peitian Zhang and Niklas Muennighoff},
   year={2023},
   eprint={2309.07597},
   archivePrefix={arXiv},
   primaryClass={cs.CL}
}

@misc{llm_embedder,
   title={Retrieve Anything To Augment Large Language Models}, 
   author={Peitian Zhang and Shitao Xiao and Zheng Liu and Zhicheng Dou and Jian-Yun Nie},
   year={2023},
   eprint={2310.07554},
   archivePrefix={arXiv},
   primaryClass={cs.IR}
}
"""

import torch
import numpy as np
from enum import Enum
from docarray.typing import NdArray
from lib import IEmbedder, load_model_and_tokenizer

_bgeInstructions = {
   "qa": {
      "query": "Represent this query for retrieving relevant documents: ",
      "key": "Represent this document for retrieval: ",
   },
   "icl": {
      "query": "Convert this example into vector to look for useful examples: ",
      "key": "Convert this example into vector for retrieval: ",
    },
   "chat": {
      "query": "Embed this dialogue to find useful historical dialogues: ",
      "key": "Embed this historical dialogue for retrieval: ",
    },
   "lrlm": {
      "query": "Embed this text chunk for finding useful historical chunks: ",
      "key": "Embed this historical text chunk for retrieval: ",
   },
   "tool": {
      "query": "Transform this user request for fetching helpful tool descriptions: ",
      "key": "Transform this tool description for retrieval: "
   },
   "convsearch": {
      "query": "Encode this query and context for searching relevant passages: ",
      "key": "Encode this passage for retrieval: ",
   },
}

class BgeInstructionType(str, Enum):
   """ The type of embedding for BGE. """
   qa = 'qa'
   """ For Q&A document retrieval. """
   icl = 'icl'
   """ For example retrieval. """
   chat = 'chat'
   """ For chat dialogue history retrieval. """
   lrlm = 'lrlm'
   """ For long-range historical retrieval. """
   tool = 'tool'
   """ For tool description retrieval. """
   convsearch = 'convsearch'
   """ For conversational search passage retrieval. """

class BgeLLMEmbedder(IEmbedder):
   def __init__(self):
      self.model, self.tokenizer = load_model_and_tokenizer(
         'BAAI/llm-embedder')

   def embed_nl_query(self, N: int):
      data: list[tuple[BgeInstructionType, str]] = []
      def append(s: tuple[BgeInstructionType, str]): data.append(s)
      for _ in range(N):
         yield append
      return self.run_batch([
         _bgeInstructions[type]['query'] + text
         for type, text in data
      ])

   def embed_nl_key(self, N: int):
      data: list[tuple[BgeInstructionType, str]] = []
      def append(s: tuple[BgeInstructionType, str]): data.append(s)
      for _ in range(N):
         yield append
      return self.run_batch([
         _bgeInstructions[type]['key'] + text
         for type, text in data
      ])

   def run_batch(self, data: list[str]):
      if len(data) == 0:
         return np.empty((0, 768))
      inputs = self.tokenizer(data, padding=True, return_tensors='pt')
      with torch.no_grad():
         outputs = self.model(**inputs)
         # CLS pooling
         embeddings = outputs.last_hidden_state[:, 0]
         # Normalize
         embeddings = torch.nn.functional.normalize(embeddings, p=2, dim=1)
      return embeddings.detach().numpy()

   def vector_type(self) -> NdArray:
      return NdArray[768,]  # type: ignore

__all__ = [
   'BgeInstructionType',
   'BgeLLMEmbedder'
]
