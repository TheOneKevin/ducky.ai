from time import sleep
import lib as lp
from enum import Enum

class _State(Enum):
   START = 0
   CHOICE1 = 1
   CHOICE2 = 2
   END = 3

state: _State = _State.START

def _step1(session: lp.ChatSession) -> lp.ChatContext:
   completion = session.current_completion()
   if 'red' in completion.user_query:
      global state
      state = _State.CHOICE1
   return lp.ChatContext(
      provider=lp.resolve_provider('dummy'),
      system_prompt='Hello, world! This is a system prompt from step 1.',
      document=[
         lp.ChatItem( type='user', text=f'You said: {completion.user_query}.'),
         lp.ChatItem(type='assistant', text=f'In the flow, you can add assistant messages too!'),
         lp.ChatItem(type='user', text=f'Now we let the AI complete this...'),
      ],
      temperature=1.0,
   )

def _choice1_step1(session: lp.ChatSession) -> lp.ChatContext:
   context = session.current_context()
   session.notifier.notify_search('This is a query string')
   sleep(0.5)
   session.notifier.notify_search('And this is another query string')
   sleep(0.5)
   return lp.ChatContext(
      provider=lp.resolve_provider('dummy'),
      system_prompt='This is a system prompt from step 1 of choice 1 (you said something with the text "red" in it). Next time, try saying something without the text "red" for a different prompt.',
      document=[
         lp.ChatItem(type='user', text=f'You can craft a new prompt here, depending on the previous respone:\n{context.document[-1].text}.'),
      ],
      temperature=1.0,
   )

def _choice2_step1(session: lp.ChatSession) -> lp.ChatContext:
   context = session.current_context()
   return lp.ChatContext(
      provider=lp.resolve_provider('dummy'),
      system_prompt='This is a system prompt from step 1 of choice 2 (you said something without the text "red" in it). Next time, try saying something with the text "red" for a different prompt.',
      document=[
         lp.ChatItem(type='user', text=f'You can craft a new prompt here, depending on the previous respone:\n{context.document[-1].text}.'),
      ],
      temperature=1.0,
   )

def _step_3(session: lp.ChatSession) -> lp.ChatContext:
   completion = session.current_completion()
   return lp.ChatContext(
      provider=lp.resolve_provider('dummy'),
      system_prompt='This is a system prompt from step 3.',
      document=[
         lp.ChatItem(type='user', text=f'You said: {completion.user_query}.'),
         lp.ChatItem(type='assistant', text=f'In the flow, you can add assistant messages too!'),
         lp.ChatItem(type='user', text=f'Now we let the AI complete this...'),
      ],
      temperature=1.0,
      is_final_context=True,
   )

def test_flow() -> lp.PromptFlowT:
   global state
   state = _State.START
   yield "test_flow() initial step", _step1
   if state == _State.CHOICE1:
      yield "test_flow() 'red'", _choice1_step1
   else:
      yield "test_flow() not red", _choice2_step1
   yield "test_flow() final step", _step_3

__FLOWENTRY__ = test_flow
__FLOWNAME__ = 'Test Prompt Flow'
__FLOWDESC__ = 'This is a test prompt flow. This flow is used to test the prompt flow system. It also has a very long description.'
