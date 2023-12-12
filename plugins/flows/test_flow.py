import lib as lp


def _step1(session: lp.ChatSession) -> lp.ChatContext:
   # When was the last time the user mentioned the word 'red'?
   user_query = session.current_completion().user_query
   last_red_message = -1
   if 'red' in user_query:
      last_red_message = 0
   else:
      total_messages = len(session.history)
      for idx, item in enumerate(session.history):
         if 'red' in item.user_query:
            last_red_message = total_messages - idx - 1
   # Return a no-op context with the last red message as state
   return lp.ChatContext(
      provider=lp.resolve_provider('dummy'),
      system_prompt='Randomly put some text in the document here.',
      document=[lp.ChatItem(type='user', text=user_query)],
      user_data={'last_red_message': last_red_message}
   )


def _found_red_now(session: lp.ChatSession) -> lp.ChatContext:
   # This is reached when the user mentions the word 'red' in the cur msg
   return lp.ChatContext(
      provider=lp.resolve_provider('no-op'),
      document=[lp.ChatItem(
         type='assistant',
          text='You mentioned red in this message.  \n\n')],
      is_final_context=True
   )


def _found_red_before(session: lp.ChatSession) -> lp.ChatContext:
   # This is reached when the user mentioned the word 'red' before
   return lp.ChatContext(
      provider=lp.resolve_provider('no-op'),
      document=[lp.ChatItem(
          type='assistant',
          text=f'You mentioned red {session.current_context().user_data["last_red_message"]} message(s) ago.  \n\n'
      )],
      is_final_context=True
   )


def _not_found_red(session: lp.ChatSession) -> lp.ChatContext:
   # This is reached when the user never mentioned the word 'red'
   return lp.ChatContext(
      provider=lp.resolve_provider('dummy'),
      document=[lp.ChatItem(
         type='assistant',
         text='You never mentioned red. Try mentioning the word "red".  \n\n'
      )],
      is_final_context=True
   )


def test_flow(session: lp.ChatSession) -> lp.PromptFlowT:
   yield 'Detecting when the user mentioned "red"', _step1
   if session.current_context().user_data['last_red_message'] == 0:
      yield 'You mentioned red in your last message.', _found_red_now
   elif session.current_context().user_data['last_red_message'] > 0:
      yield 'You mentioned red in your second last message.', _found_red_before
   else:
      yield 'You never mentioned red.', _not_found_red


__FLOWENTRY__ = test_flow
__FLOWNAME__ = 'Test Prompt Flow'
__FLOWDESC__ = 'This is a test stateful prompt flow. This flow also has a very long description.'
