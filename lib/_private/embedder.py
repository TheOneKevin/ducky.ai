from abc import ABC, abstractmethod
from docarray import BaseDoc, DocList
from typing import Callable, Generator, TypeVar, Generic

import numpy as np

class IEmbedder(ABC):
   pass

T = TypeVar('T')
U = TypeVar('U', bound=BaseDoc)

QueueEmbedFn = Callable[[T], None]
EmbedderT = Callable[[int], Generator[QueueEmbedFn[T], None, np.ndarray]]
BatchEmbedderT = Generator[tuple[U, QueueEmbedFn[T]], None, np.ndarray]

def batch_embed_impl(docs: DocList[U],
                     embedder: EmbedderT[T]) -> BatchEmbedderT[U, T]:
   N = len(docs)
   gen = embedder(N)
   for i in range(N):
      yield docs[i], next(gen)
   try:
      next(gen)
   except StopIteration as e:
      return e.value
   except Exception as e:
      raise e
   return np.zeros((0, 0))

class BatchEmbedder(Generic[T, U]):
   def __init__(self, docs: DocList[U], embedder: EmbedderT[T]):
      self.gen = batch_embed_impl(docs, embedder)

   def __iter__(self) -> Generator[tuple[U, QueueEmbedFn[T]], None, None]:
      self.value = yield from self.gen

__all__ = ['IEmbedder', 'BatchEmbedder']
