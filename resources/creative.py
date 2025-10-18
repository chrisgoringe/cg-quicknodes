import requests
from .contexts import Context, ContextList
from typing import Optional
from .formats import get_base_payload, wrap

def rewrite_prompt(server, prompt:str, settings:str, extra_instructions:str):
    payload = get_base_payload(settings)
    payload['prompt'] = wrap("system",extra_instructions) + wrap("user",prompt) + wrap("assistant",None)
    response = requests.post(server, json=payload, verify=False)  
    jsn = response.json()
    return jsn['results'][0]['text'].strip()

class PromptCreator:
    def __init__(self, server:str, settings:str):
        self.server = server
        self.settings = settings

    def get_new_prompt(self, summary:Optional[str]=None, contexts:Optional[ContextList]=None, opener:Optional[str]=None, seed:Optional[int]=None) -> str:
        context = "".join( [c.wrapped() for c in contexts.contexts] ) if contexts else ""
        summary = wrap("user",summary) if summary else ""
        opener  = (opener + " ") if opener else ""

        payload = get_base_payload(self.settings)

        payload['prompt'] = context + summary + wrap("assistant",None) + opener
        if seed: payload['sampler_seed'] = (seed % 1000000)

        response = requests.post(self.server, json=payload, verify=False)
        if response.status_code != 200: raise Exception(f"Server {self.server} returned {response.status_code}: {response.reason}")

        new_prompt:str = opener + response.json()['results'][0]['text'].strip()
        return new_prompt
