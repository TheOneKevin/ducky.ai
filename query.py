import os
import json
from threading import local
from docarray import BaseDoc, DocList
from lib import *
from lib.embedders import EmberV1Embedder
from docarray.index.backends.hnswlib import HnswDocumentIndex

@EmbeddedDoc({'embedding': EmberV1Embedder()})
class RiscVDoc(BaseDoc):
   text: str

abs_path = os.path.join(os.path.dirname(__file__), 'simple_dl')
docs = DocList[RiscVDoc].pull(f'file://{abs_path}', local_cache=False)
doc_index = HnswDocumentIndex[RiscVDoc](work_dir='./tmp_0')
doc_index.index(docs)

# Get input from user?
query = 'What is the purpose of the CSR instruction?'

# Embed query
querydoc = DocList[RiscVDoc]([RiscVDoc(text=query)])
for doc, embed in batch_embed(
   querydoc, 'embedding', EmberV1Embedder().embed_nl_key, batch_size=1
):
   embed(doc.text)

# Query index
matches, scores = doc_index.find(querydoc[0], 'embedding', limit=10)

# Print results
for i, result in enumerate(matches):
   print(f'{i}: {result.text}')
   print(f'   Score: {scores[i]}')
   print()
