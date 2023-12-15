"""
Internal module for resolving flows and providers.
"""

import os, sys, inspect, importlib
from typing import Literal
from .session import FlowDescriptor, IChatProvider

ProvidersT = Literal['openai', 'dummy', 'no-op']
__cached_providers: dict[ProvidersT, IChatProvider] = {}

def resolve_flows(flow_dir: str | None = None) -> list[FlowDescriptor]:
   """
   Loops through the directory and gathers all the prompt flows.
   """
   # If no flow directory is specified, then we use the default one
   if flow_dir is None:
      flow_dir = os.path.join(
         os.path.dirname(os.path.realpath(__file__)),
         '..',
         '..',
         'plugins'
      )
   
   # And if the directory doesn't exist, then we return an empty list
   if not os.path.isdir(flow_dir):
      return []
   result = []

   # Get all the python files in the directory (recursively)
   files = [
      os.path.realpath(os.path.join(dp, f))
      for dp, dn, filenames in os.walk(flow_dir)
      for f in filenames if os.path.splitext(f)[1] == '.py'
   ]

   # For each python file, check if it has the required attributes
   for file in files:
      old_path = sys.path.copy()
      sys.path.append(os.path.dirname(file))
      filename = os.path.basename(file)
      modname = filename[:-3]
      if modname == '__init__':
         continue
      # We import the module and reload it to ensure we get the latest version
      try:
         mod = importlib.import_module(modname)
         mod = importlib.reload(mod)
      except Exception as e:
         continue
      # Check if the module has the required attributes
      members_dict = dict(inspect.getmembers(mod))
      entry = members_dict.get('__FLOWENTRY__')
      name = members_dict.get('__FLOWNAME__')
      desc = members_dict.get('__FLOWDESC__')
      # If not, then it's probably some random python file
      if entry == None or name == None or desc == None:
         continue
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

def resolve_provider(provider: ProvidersT) -> IChatProvider:
   """
   Resolves a provider from the given string.
   """
   from .chat import (
      OpenAIChatProvider, DummyChatProvider, NoOpChatProvider
   )
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

__all__ = ['resolve_flows', 'resolve_provider']
