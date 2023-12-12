import lib as lp


def _step1(session: lp.ChatSession) -> lp.ChatContext:
   # Since this is the first step, the user query is in the current completion
   user_text = session.current_completion().user_query

   # Now let's craft an artificial response
   document = [lp.ChatItem(
      type='assistant',
      text=f'This is using the no-op chat provider. You said:'
      f'   \n  \n{user_text}  \n  \n'
      f'Here is some text appended to the end of the conversation. Try inspecting the details of this chat. You should only see 1 entry in the history corresponding to this message only.'
   )]

   # Return the chat context through no-op, this will NOT modify the document
   # and what the user sees is what we put in "document"
   return lp.ChatContext(
      provider=lp.resolve_provider('no-op'),
      system_prompt='',
      document=document,
      is_final_context=True,
   )


def echo() -> lp.PromptFlowT:
   yield "Echo", _step1


__FLOWENTRY__ = echo
__FLOWNAME__ = 'Echo Prompter'
__FLOWDESC__ = 'Echoes everything you say back to you.'
