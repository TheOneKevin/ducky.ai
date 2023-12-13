import json
import re
from PyPDF2 import PdfReader
from pprint import pprint

reader = PdfReader(open("unpriv-isa-asciidoc.pdf", 'rb'))


def bookmark_dict(bookmark_list):
   result = []
   for item in bookmark_list:
      if isinstance(item, list):
         # recursive call
         result.extend(bookmark_dict(item))
      else:
         try:
            result.append(
               (reader.get_destination_page_number(item) + 1, item.title))
         except:
            pass
   return result


bookmarks = bookmark_dict(reader.outline)

# Filter out any non-ASCII characters
bookmarks = [
   (page, title.encode('ascii', 'ignore').decode('ascii'))
   for page, title in bookmarks
]

# Replace `` and '' with " in bookmarks
bookmarks = [
   (page, title.replace('``', '"').replace("''", '"'))
   for page, title in bookmarks
]

# Remove ", Version x.x" using regex
bookmarks = [
   (page, re.sub(r', Version \d\.\d', '', title))
   for page, title in bookmarks
]

# Print bookmarks list
for page, title in bookmarks:
   print(f'{page} {title}')

with open('output_tokens.json', 'r') as f:
   doc = json.load(f)

for section in doc:
   # Normalize title
   section['title'] = section['title'].strip()

   # Remove ", Version x.x" using regex
   section['title'] = re.sub(r', Version \d\.\d', '', section['title'])

   # Find section['title'] in bookmarks
   found = '❌'
   for bookmark in bookmarks:
      if bookmark[1].endswith(section['title']):
         section['page'] = bookmark[0]
         found = '✅'
         break
   print(f'{found} {section["title"]}')

# Now we can re-save the JSON file with the page numbers
with open('output_tokens.json', 'w') as f:
   json.dump(doc, f, indent=1)
