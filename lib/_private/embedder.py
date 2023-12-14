from abc import ABC, abstractmethod
from docarray import BaseDoc, DocList
from docarray.typing import NdArray
from typing import Callable, Generator, TypeVar, overload
from pydantic import create_model, Field
import numpy as np

class IEmbedder(ABC):
   """ Interface class for embedding providers. """
   @abstractmethod
   def vector_type() -> NdArray:
      raise NotImplementedError('vector_type() not implemented')

T = TypeVar('T')
U = TypeVar('U', bound=BaseDoc)
V = TypeVar('V', bound=BaseDoc)

QueueEmbedFn = Callable[[T], None]
EmbedderT = Callable[[int], Generator[QueueEmbedFn[T], None, np.ndarray]]
BatchEmbedderT = Generator[tuple[U, QueueEmbedFn[T]], None, None]

def batch_embed(docs: DocList[U], field: str,
                embedder: EmbedderT[T],
                batch_size: int = 8) -> BatchEmbedderT[U, T]:
   """
   This function is a generator that yields a tuple of the doc and a function that takes the embedding and sets the doc's field to the embedding.

   Args:
       docs (DocList[U]): The docs to embed.
       field (str): The field to set the embedding to.
       embedder (EmbedderT[T]): The embedding function to use.
       batch_size (int, optional): The batch size. Defaults to 8.

   Raises:
       e: Exception from the embedder.

   Returns:
       BatchEmbedderT[U, T]: The generator that yields the doc and the function to create the embedding.

   Yields:
       tuple[U, QueueEmbedFn[T]]: The doc and the function to create the embedding.
   """
   i = 0
   N = len(docs)
   while i < N:
      batch = min(batch_size, N - i)
      gen = embedder(batch)
      for j in range(i, i + batch):
         yield docs[j], next(gen)
      try:
         next(gen)
      except StopIteration as e:
         for j in range(i, i + batch):
            setattr(docs[j], field, e.value[j - i])
      except Exception as e:
         raise e
      i += batch

class _Generator:
   def __init__(self, gen): self.gen = gen
   def __iter__(self): self.value = yield from self.gen

def get_dimension(embedder: EmbedderT[T]) -> NdArray:
   dimension = _Generator(embedder(0))
   for _ in dimension:
      break
   return dimension.value.shape[1]

def batch_embed_raw(docs: list[T], embedder: EmbedderT[T],
                    batch_size: int = 8) -> np.ndarray:
   """This function will take a list of inputs to the embedder and return the final embedding vector. This is useful for embedding a list of queries that are batched together.

   Args:
       docs (list[T]): The inputs to the embedder.
       embedder (EmbedderT[T]): The embedder function to use.
       batch_size (int, optional): The batch size. Defaults to 8.

   Raises:
       e: Exception from the embedder.

   Returns:
       np.ndarray: The final embedding vector (concat all the batches).
   """
   i = 0
   N = len(docs)
   returnvec = np.empty((N, get_dimension(embedder)))
   while i < N:
      batch = min(batch_size, N - i)
      gen = embedder(batch)
      for j in range(i, i + batch):
         embed = next(gen)
         embed(docs[j])
      try:
         next(gen)
      except StopIteration as e:
         vector = e.value
         returnvec[i:i + batch] = vector
      except Exception as e:
         raise e
      i += batch
   return returnvec

def EmbeddedDoc(embeddings: dict[str, IEmbedder]):
   """This decorator adds the embeddings to the doc. The embedding fields are then added to the doc type.

   Args:
       embeddings (dict[str, IEmbedder]): The fields to add to the doc. The key is the field name and the value is the embedder that will be used to provide the embedding vector.
   """
   def impl(cls: type[V]) -> type[V]:
      fields = {
         name: (field.vector_type(), Field(None, alias=name))
         for name, field in embeddings.items()
      }
      fields.update({
         field.name: (field.outer_type_, field.field_info)
         for field in cls.__fields__.values()
      })
      return create_model(
         __model_name=f'{cls.__name__}WithEmbeddings',
         __base__=cls,
         **fields  # type: ignore
      )
   return impl

__all__ = [
   'IEmbedder',
   'batch_embed',
   'batch_embed_raw',
   'EmbeddedDoc'
]
