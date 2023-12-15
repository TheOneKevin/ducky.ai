import os
import re

def split(doc_root, doc):
   PATTERN_HEADER = re.compile(r'^(=+)\s(.+)$')
   PATTERN_SECTION = re.compile(r'^\[.*\]$')
   
   with open(doc, 'r') as f:
      lines = f.readlines()

   # Pass: Substitute includes
   for i in range(len(lines)):
      line = lines[i].strip()
      if line.startswith('include::'):
         include_path = os.path.join(doc_root, line[9:-2])
         if not os.path.exists(include_path):
            continue
         with open(include_path, 'r') as f:
            include_lines = f.readlines()
         lines[i] = '\n'.join(include_lines)

   # Pass: Re-split lines by '\n' as we have newlines in the middle of lines
   lines = [line + '\n' for line in ''.join(lines).split('\n')]

   # Pass: Split into sections and extract tables
   sections: list[dict] = []
   state = 'default'
   i = 0
   while i < len(lines):
      line = lines[i]
      if line.startswith('//') or line == '<<<\n' or line.startswith('((('):
         i += 1
         continue
      if state == 'default':
         header_match = PATTERN_HEADER.match(line.strip())
         if header_match:
            # How many = characters are there?
            level = len(header_match.group(1))
            # What is the title?
            title = header_match.group(2)
            sections.append({
                'level': level,
                'title': title,
                'sections': [{
                    'type': 'text',
                    'text': ''
                }]
            })
         elif PATTERN_SECTION.match(line.strip()):
            # Keep matching blank lines
            old_i = i
            i += 1
            while lines[i] == '\n':
               i += 1
            if lines[i].startswith('===='):
               state = 'in-section'
               sections[-1]['sections'].append({
                   'type': line.strip(),
                   'text': ''
               })
            elif lines[i].startswith('....') or lines[i].startswith('----'):
               state = 'in-code'
               sections[-1]['sections'].append({
                   'type': 'code',
                   'language': line.strip()[1:-1],
                   'text': ''
               })
            else:
               i = old_i
               pass  # Ignore all other [.*] syntax
         elif line.startswith('|==='):
            state = 'in-table'
            sections[-1]['sections'].append({
                'type': 'table',
                'text': ''
            })
         else:
            if len(sections) > 0:
               sections[-1]['sections'][-1]['text'] += line
      elif state == 'in-section':
         if line.startswith('===='):
            state = 'default'
            sections[-1]['sections'].append({
                'type': 'text',
                'text': ''
            })
         else:
            if len(sections) > 0:
               sections[-1]['sections'][-1]['text'] += line
      elif state == 'in-table':
         if line.startswith('|==='):
            state = 'default'
            sections[-1]['sections'].append({
                'type': 'text',
                'text': ''
            })
         else:
            if len(sections) > 0:
               sections[-1]['sections'][-1]['text'] += line
      elif state == 'in-code':
         if line.startswith('....') or line.startswith('----'):
            state = 'default'
            sections[-1]['sections'].append({
                'type': 'text',
                'text': ''
            })
         else:
            if len(sections) > 0:
               sections[-1]['sections'][-1]['text'] += line
      i += 1

   # Pass: Split sections into paragraphs that are not code or tables
   for section in sections:
      for subsection in section['sections']:
         if subsection['type'] != 'table' and subsection['type'] != 'code':
            subsection['text'] = subsection['text'].split('\n\n')
            # Strip, remove empty paragraphs and replace newlines with spaces
            subsection['text'] = [
               # Regex to preserve lists
               re.sub(r'\n(?!\*)', ' ', p).strip()
               # This is for code blocks, which we want to keep as-is
               if '....' not in p
               else p
               for p in subsection['text']
            ]
         else:
            subsection['text'] = [subsection['text'].strip()]

   # Pass: Replace any remaining .... with ```
   for section in sections:
      for subsection in section['sections']:
         if subsection['type'] != 'table' and subsection['type'] != 'code':
            subsection['text'] = [
               p.replace('....', '```').replace('----', '```')
               for p in subsection['text']
            ]

   # Pass: Remove _ and replace multiple spaces with one
   for section in sections:
      for subsection in section['sections']:
         if subsection['type'] != 'table' and subsection['type'] != 'code':
            subsection['text'] = [
               re.sub(r' +', ' ', p.replace('_', ''))
               for p in subsection['text']
            ]

   # Pass: Remove \n and then replace multiple spaces with one but only for
   #       code blocks with language containing "wavedrom"
   for section in sections:
      for subsection in section['sections']:
         if subsection['type'] == 'code' \
            and 'wavedrom' in subsection['language']:
            subsection['text'] = [
               re.sub(r' +', ' ', p.replace('\n', ''))
               for p in subsection['text']
            ]

   # Pass: Filter out non-ASCII characters
   for section in sections:
      section['title'] = ''.join([c for c in section['title'] if ord(c) < 128])
      for subsection in section['sections']:
         subsection['text'] = [
            ''.join([c for c in p if ord(c) < 128])
            for p in subsection['text']
         ]

   # Pass: Delete subsection['text'] strings that are empty
   for section in sections:
      for subsection in section['sections']:
         if subsection['type'] != 'table' and subsection['type'] != 'code':
            subsection['text'] = [
               p for p in subsection['text'] if p.strip()
            ]

   # Pass: Replace latexmath:[...] with ... using regex
   for section in sections:
      for subsection in section['sections']:
         if subsection['type'] != 'code':
            subsection['text'] = [
               re.sub(r'latexmath:\[(.+?)\]', r'\1', p)
               for p in subsection['text']
            ]

   # Pass: Remove subsections with empty text
   for section in sections:
      section['sections'] = [
         subsection
         for subsection in section['sections']
         if len(subsection['text']) > 0
      ]

   return sections
