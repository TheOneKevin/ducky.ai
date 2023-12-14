import os
import json
from docarray import BaseDoc, DocList
from lib import *
from lib.embedders import EmberV1Embedder
from docarray.index.backends.hnswlib import HnswDocumentIndex

input_file = os.path.join(
   os.path.dirname(__file__),
   'plugins',
   'data',
   'output_tokens_combined.json'
)
with open(input_file, 'r') as f:
   document = json.load(f)

@EmbeddedDoc({'embedding': EmberV1Embedder()})
class RiscVDoc(BaseDoc):
   text: str

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

# doc_index = HnswDocumentIndex[RiscVDoc](work_dir='./tmp_0')
# doc_index.index(docs)

abs_path = os.path.join(os.path.dirname(__file__), 'simple_dl')
docs.push(f'file://{abs_path}')
