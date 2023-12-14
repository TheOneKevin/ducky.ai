from docarray import BaseDoc, DocList
from lib import *
from lib.embedders import BgeLLMEmbedder, BgeInstructionType
from docarray import BaseDoc, DocList
from docarray.index import InMemoryExactNNIndex
from docarray.typing import NdArray
import numpy as np


@EmbeddedDoc({'embedding': BgeLLMEmbedder()})
class MyDoc(BaseDoc):
   x: str

docs = DocList([
   MyDoc(x='a'),
   MyDoc(x='b'),
   MyDoc(x='c'),
])

for doc, embed in batch_embed(docs, 'embedding',
                              BgeLLMEmbedder().embed_nl_query):
   embed((BgeInstructionType.chat, doc.x))

for doc in docs:
   print(doc.embedding)

print(batch_embed_raw([
   (BgeInstructionType.chat, 'b'),
   (BgeInstructionType.chat, 'c'),
   (BgeInstructionType.chat, 'd')
], BgeLLMEmbedder().embed_nl_query, batch_size=1))

import os
abs_path = os.path.join(os.path.dirname(__file__), 'simple_dl')
docs.push(f'file://{abs_path}')
