import json

if __name__ != '__main__':
   raise ImportError('This module cannot be imported')

# Let's read in output_tokens.json
with open('output_tokens.json', 'r') as f:
   document = json.load(f)

# Now combine the subsections such that the sum of the tokens is less than 400
# for each subsection that we combined.
for section in document:
   for subsection in section['sections']:
      if subsection['type'] in { 'code', 'table' }:
         continue
      tokens: list[int] = subsection['tokens']
      texts: list[str] = subsection['text']
      new_tokens: list[int] = []
      new_texts: list[str] = []
      i = 0
      cur_tokens = 0
      cur_text = ''
      while i < len(tokens):
         if cur_tokens + tokens[i] < 400:
            cur_tokens += tokens[i]
            cur_text += texts[i]
         else:
            new_tokens.append(cur_tokens)
            new_texts.append(cur_text)
            cur_tokens = tokens[i]
            cur_text = texts[i]
         i += 1
      if cur_tokens != 0:
         new_tokens.append(cur_tokens)
         new_texts.append(cur_text)
      subsection['tokens'] = new_tokens
      subsection['text'] = new_texts

# Now write the new document to output_tokens_combined.json
with open('output_tokens_combined.json', 'w') as f:
   json.dump(document, f, indent=1)
