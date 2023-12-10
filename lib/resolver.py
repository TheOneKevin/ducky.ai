import inspect, os, sys
from typing import Callable, Literal
from .session import PromptFlowT
from importlib import import_module
from dataclasses import dataclass
from uuid import uuid4
from typing import Literal
from .openai import OpenAIChatProvider
from .babbler import DummyChatProvider

ProvidersT = Literal['openai', 'dummy']
__cached_providers = {}

@dataclass
class FlowDescriptor:
   id: str
   name: str
   description: str
   entry: Callable[[], PromptFlowT]

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
         mod = import_module(modname)
         members_dict = dict(inspect.getmembers(mod))
         entry = members_dict.get('__FLOWENTRY__')
         name = members_dict.get('__FLOWNAME__')
         desc = members_dict.get('__FLOWDESC__')
         if entry is not None and name is not None and desc is not None:
            result.append(FlowDescriptor(
               id=uuid4().hex,
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
   else:
      raise ValueError(f'Unknown provider: {provider}')
   return __cached_providers[provider]
