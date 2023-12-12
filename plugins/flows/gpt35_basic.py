import lib as lp

my_system_prompt = "You are a helpful assistant named Ducky. Format your reponses in Markdown. However, enclose inline math expressions with dollar signs like this $\\latex 1 + 2 + 3$ and multi-line math expressions with double dollar signs like this $$\\frac{1}{2}x+y$$. Be nice to the user."


def _step1(session: lp.ChatSession) -> lp.ChatContext:
   # Re-construct the chat history
   history = []
   for completion in session.history:
      # Append the previous user query
      history.append(lp.ChatItem(type='user', text=completion.user_query))
      # Check if the item has a response
      if completion.response:
         history.append(lp.ChatItem(
            type='assistant', text=completion.response))
   # Return the constructed chat context
   return lp.ChatContext(
      model='gpt-3.5-turbo-1106',
      provider=lp.resolve_provider('openai'),
      system_prompt=my_system_prompt,
      document=history,
      temperature=1.0,
      # max_tokens=256,
      is_final_context=True,
   )


def gpt_35(session: lp.ChatSession) -> lp.PromptFlowT:
   yield "GPT 3.5-Turbo", _step1


__FLOWENTRY__ = gpt_35
__FLOWNAME__ = 'GPT 3.5-Turbo'
__FLOWDESC__ = 'Vanilla GPT-3.5 Turbo chatbot.'
