import inspect
import os
import sys
from typing import Literal
from .session import FlowDescriptor
import importlib
from typing import Literal
from .private import OpenAIChatProvider, DummyChatProvider, NoOpChatProvider

ProvidersT = Literal['openai', 'dummy', 'no-op']
__cached_providers = {}


def resolve_flows(flow_dir: str | None = None) -> list[FlowDescriptor]:
   """
   Loops through the directory and gathers all the prompt flows.
   """
   if flow_dir is None:
      flow_dir = os.path.join(os.path.dirname(__file__), '../plugins/flows')
   if not os.path.isdir(flow_dir):
      return []
   old_path = sys.path.copy()
   sys.path.append(flow_dir)
   result = []
   for filename in os.listdir(flow_dir):
      if filename.endswith('.py'):
         modname = filename[:-3]
         if modname == '__init__':
            continue
         mod = importlib.import_module(modname)
         mod = importlib.reload(mod)
         members_dict = dict(inspect.getmembers(mod))
         entry = members_dict.get('__FLOWENTRY__')
         name = members_dict.get('__FLOWNAME__')
         desc = members_dict.get('__FLOWDESC__')
         if entry is not None and name is not None and desc is not None:
            # TODO: Use a better ID & should be invariant to the file too.
            id = filename[:-3]
            # Try to set the flow ID as session.start_flow_stream expects it
            setattr(entry, 'flow_id', id)
            result.append(FlowDescriptor(
               id=id,
               name=name,
               description=desc,
               entry=entry
            ))
   sys.path = old_path
   return result


def resolve_provider(provider: ProvidersT):
   """
   Resolves a provider from the given string.
   """
   if provider in __cached_providers:
      return __cached_providers[provider]
   if provider == 'openai':
      __cached_providers[provider] = OpenAIChatProvider()
   elif provider == 'dummy':
      __cached_providers[provider] = DummyChatProvider()
   elif provider == 'no-op':
      __cached_providers[provider] = NoOpChatProvider()
   else:
      raise ValueError(f'Unknown provider: {provider}')
   return __cached_providers[provider]
