import json

if __name__ != '__main__':
   raise ImportError('This module cannot be imported')

with open('output_tokens.json', 'r') as f:
   tokens = json.load(f)
for section in tokens:
   for subsection in section['sections']:
      # Check if there is a number > 512 in the subsection['tokens']
      num_tokens = max(subsection['tokens'])
      if num_tokens > 512:
         print(
            f'Tokens {num_tokens} in subsection: ',
            json.dumps(subsection)[:60],
            'in section:',
            section['title']
         )
