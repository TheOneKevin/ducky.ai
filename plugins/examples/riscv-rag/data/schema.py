import os, json

from sympy import li
from lib import *
from lib.embedders import EmberV1Embedder
from docarray import BaseDoc, DocList
from docarray.index.backends.hnswlib import HnswDocumentIndex

db_path_hardcoded = os.path.join(os.path.dirname(__file__), 'riscv.vdb')
work_dir_hardcoded = os.path.join(os.path.dirname(__file__), 'tmp_0')

@EmbeddedDoc({'embedding': EmberV1Embedder()})
class RiscVDoc(BaseDoc):
   text: str

def build_embeddings():
   input_file = os.path.join(
       os.path.dirname(__file__),
       'output_tokens_combined.json'
   )
   with open(input_file, 'r') as f:
      document = json.load(f)
   docs: DocList[RiscVDoc] = DocList()
   for section in document:
      for subsection in section['sections']:
         if subsection['type'] in {'code', 'table'}:
            continue
         for text in subsection['text']:
            docs.append(RiscVDoc(text=text))
   for doc, embed in batch_embed(
      docs, 'embedding', EmberV1Embedder().embed_nl_key, batch_size=64
   ):
      embed(doc.text)
   docs.push(f'file://{db_path_hardcoded}')

def load_embeddings():
   docs = DocList[RiscVDoc].pull(
      f'file://{db_path_hardcoded}', local_cache=False)
   doc_index = HnswDocumentIndex[RiscVDoc](work_dir=work_dir_hardcoded)
   doc_index.index(docs)
   return doc_index

def query_db(index: HnswDocumentIndex[RiscVDoc], queries: DocList[RiscVDoc],
             limit: int = 10, batch_size: int = 1):
   for doc, embed in batch_embed(
      queries, 'embedding', EmberV1Embedder().embed_nl_key,
      batch_size=batch_size
   ):
      embed(doc.text)
   return index.find_batched(queries, 'embedding', limit=limit)

__all__ = [
   'RiscVDoc',
   'build_embeddings',
   'query_db'
]
