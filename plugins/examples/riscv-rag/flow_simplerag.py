import lib as lp
from data.schema import load_embeddings, query_db, RiscVDoc
from docarray import DocList
from docarray.index.backends.hnswlib import HnswDocumentIndex

cached_db: HnswDocumentIndex[RiscVDoc] | None = None

def flowentry(session: lp.ChatSession) -> lp.PromptFlowT:
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
   # 2. Take the query and search the database
   completion = session.current_completion()
   user_query = completion.user_query
   queries = DocList([RiscVDoc(text=user_query)])
   assert cached_db is not None
   session.notifier.notify_search(user_query)
   doclistlist, scores = query_db(cached_db, queries, limit=10)
   results: list[str] = []
   for i, doc in enumerate(doclistlist[0]):
      results.append(
         f'Score: {scores[0][i]}<br />Result {i}:<br />{doc.text}')
      completion.references.append(
         lp.ReferenceItem(
            type='text',
            data=doc.text,
            url='???'
         )
      )
   yield "Retrieving data", lp.ChatContext(
      provider=lp.resolve_provider('no-op'),
      system_prompt='',
      document=[lp.ChatItem(
         type='assistant',
         text='<br /><hr />'.join(results)
      )],
      is_final_context=True,
   )

__FLOWENTRY__ = flowentry
__FLOWNAME__ = 'RISC-V: Simple search (no LLM)'
__FLOWDESC__ = 'Searches the vector database raw, as-is.'
