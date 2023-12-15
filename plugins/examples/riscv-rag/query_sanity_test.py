import os, sys
from docarray import DocList

# Add the root of the repo to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def main():
   from data.schema import load_embeddings, query_db, RiscVDoc
   # Load embeddings
   print('Loading embedding database and index')
   doc_index = load_embeddings()
   print('Done!')
   # Get input from user?
   queries = DocList([
      RiscVDoc(text='What is the purpose of the CSR instruction?')
   ])
   # Query database
   print('Querying database')
   doclistlist, scores = query_db(doc_index, queries)
   # Print results
   for i, doclist in enumerate(doclistlist):
      for j, doc in enumerate(doclist):
         print(f'Result {i},{j}:\n{doc.text}')
         print(f'   Score: {scores[i][j]}')
         print()

if __name__ == '__main__':
   main()
