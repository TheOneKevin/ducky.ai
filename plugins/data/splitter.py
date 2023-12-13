import json
import os
from asciidocparser import split

# Document list grabbed from riscv-unprivileged.adoc, in order
docs = [
   'intro.adoc',
   'rv32.adoc',
   'zifencei.adoc',
   'zihintntl.adoc',
   'zihintpause.adoc',
   'rv32e.adoc',
   'rv64.adoc',
   'rv128.adoc',
   'm-st-ext.adoc',
   'a-st-ext.adoc',
   'zicsr.adoc',
   'counters.adoc',
   'f-st-ext.adoc',
   'd-st-ext.adoc',
   'q-st-ext.adoc',
   'zfh.adoc',
   'rvwmo.adoc',
   'c-st-ext.adoc',
   'zimop.adoc',
   'b-st-ext.adoc',
   'j-st-ext.adoc',
   'p-st-ext.adoc',
   'v-st-ext.adoc',
   'zam-st-ext.adoc',
   'zfinx.adoc',
   'zfa.adoc',
   'ztso-st-ext.adoc',
   'rv-32-64g.adoc',
   'extending.adoc',
   'naming.adoc',
   'history.adoc',
   'mm-eplan.adoc',
   'mm-formal.adoc'
]

doc_root = os.path.join(os.path.dirname(__file__), 'riscv-isa-manual', 'src')
result = []
for doc in docs:
   print(f'Parsing {doc}')
   doc = os.path.join(doc_root, doc)
   result.extend(split(doc_root, doc))

print('Loading tokenizer')
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("llmrails/ember-v1")
print('Calculating token counts')
for section in result:
   for subsection in section['sections']:
      subsection['tokens'] = [
         len(x)
         for x in tokenizer(subsection['text'])['input_ids']  # type: ignore
      ]

print('Dumping output')
with open('output_tokens.json', 'w') as f:
   json.dump(result, f, indent=1)
