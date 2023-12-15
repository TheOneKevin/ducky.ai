import re
import lib as lp
from data.schema import load_embeddings, query_db, RiscVDoc
from docarray import DocList
from docarray.index.backends.hnswlib import HnswDocumentIndex

from lib.embedders.emberv1 import EmberV1Embedder

cached_db: HnswDocumentIndex[RiscVDoc] | None = None
PATTERN = re.compile(r'"([^"]+)"')

def flowentry(session: lp.ChatSession) -> lp.PromptFlowT:
   user_query = session.current_completion().user_query

   # 1. Load the database if it's not already loaded
   global cached_db
   if cached_db is None:
      cached_db = load_embeddings()
      yield "Loading database", lp.ChatContext(
         provider=lp.resolve_provider('no-op'),
         system_prompt='',
         document=[lp.ChatItem(
            type='assistant',
            text='Loading database'
         )],
         is_final_context=False,
      )
   assert cached_db is not None

   # 2. Construct the prompt for generating queries
   yield "Generating queries", lp.ChatContext(
      provider=lp.resolve_provider('openai'),
      model='gpt-3.5-turbo-1106',
      system_prompt="You are an assistant that will help with querying an embedding vector database. The database contains embeddings of text chunks from the RISC-V database. Come up with 1-3 query phrases for the embedding database that will be the most effective in answering the user's question. Use compiler terminology. Do not start queries with a verb. Instead, just type out related topics. Surround each query in double quotes \"like this\".",
      document=[lp.ChatItem(
         type='user',
         text=f'Can you come up with search queries for the question:\n{user_query}'
      )],
      temperature=0.2,
      frequency_penalty=1.0,
      presence_penalty=0.25,
      is_final_context=False,
   )

   # 3. Extract the queries from the response
   queries = DocList()
   phrases = PATTERN.findall(session.current_context().document[-1].text)
   for phrase in phrases:
      session.notifier.notify_search(phrase)
      queries.append(RiscVDoc(text=phrase))

   # 4. Take the queries and search the database
   doclistlist, scores = query_db(cached_db, queries, limit=3, batch_size=64)
   results: set[str] = set()
   for doclist in doclistlist:
      for doc in doclist:
         results.add(doc.text)
         session.current_completion().references.append(
            lp.ReferenceItem(
               type='text',
               data=doc.text,
               url='???'
            )
         )

   # 5. Construct the query from the results
   query_list = list(results)
   for i in range(len(query_list)):
      query_list[i] = f'Source {i+1}: """{query_list[i]}"""'
   data_list = '\n'.join(query_list)
   
   yield "Retrieving data", lp.ChatContext(
      provider=lp.resolve_provider('openai'),
      model='gpt-3.5-turbo-1106',
      system_prompt="You are an assistant that will help the user with searching and synthesizing answers from the RISC-V Unprivileged ISA specifications. Be specific in your answer and use the supplied information. If there are multiple possible answers, list 2 of them even if the user specified 1. If the question can be answered directly without the supplied information, answer it as well. If you do not know the answer, say so. State to the user if you are giving incomplete information. The passages will be given as a list in the format:\n\nSource 1: \"\"\"Passage 1\"\"\"\n...\nSource N: \"\"\"Passage 3\"\"\"\n\nPlease have in-text citation in your response, for example, if you used Source 1 in your response, put [1] where you used it. Please do well, my career depends on it!",
      document=[lp.ChatItem(
         type='user',
         text=f'Relative passages retrieved from the RISC-V specification:\n\n{data_list}\n\nUser question: {user_query}'
      )],
      is_final_context=True,
   )

__FLOWENTRY__ = flowentry
__FLOWNAME__ = 'RISC-V: LLM powered RAG'
__FLOWDESC__ = 'A generic run at the mill retrieval augmented generation flow.'
