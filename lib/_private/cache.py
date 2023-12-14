from typing import Any
from transformers import (
   PreTrainedTokenizer,
   PreTrainedTokenizerFast,
   AutoModel,
   AutoTokenizer
)

_model_cache: dict[str, Any] = {}
_tokenizer_cache: dict[str, PreTrainedTokenizer | PreTrainedTokenizerFast] = {}

def load_model_and_tokenizer(name: str):
   if name not in _model_cache:
      _model_cache[name] = AutoModel.from_pretrained(name)
   if name not in _tokenizer_cache:
      _tokenizer_cache[name] = AutoTokenizer.from_pretrained(name)
   return _model_cache[name], _tokenizer_cache[name]

__all__ = ['load_model_and_tokenizer']
