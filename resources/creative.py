import datasets, requests, time, os, random
from .prompt_formats import parse_settings_list
from math import pow
from typing import Optional
import numpy as np

END = "<|im_end|>"
START = "<|im_start|>"

DEFAULTS = {     
    "max_context_length": 20000,
    "max_length": 2000,
    "quiet": False,
    "rep_pen": 1.1,
    "rep_pen_range": 256,
    "rep_pen_slope": 1,
    "temperature": 1.1,
    "tfs": 1,
    "top_a": 0,
    "top_k": 100,
    "top_p": 0.9,
    "typical": 1,
    "stop_sequence": [END,],
    "trim_stop": True,
    "dry_multiplier":0.8, "dry_allowed_length":2, "dry_base":1.75
}

class Creator:
    _instance = None

    def __init__(self, server, dataset_id:str, is_context=False):
        self.dataset_id = dataset_id             if not is_context else None
        self.provided   = dataset_id.split("|")  if is_context     else None
        self.server     = server
        self.is_context = is_context
        if not is_context:
            ds = datasets.load_from_disk(dataset_id) if os.path.exists(dataset_id) else datasets.load_dataset(dataset_id)['train']
            
            self.count = len(ds)
            self.data  = {
                'prompt':ds['prompt'],  
                'idx'   :ds['idx']   if 'idx'   in ds.column_names else [0]*self.count, 
                'score' :ds['score'] if 'score' in ds.column_names else [0]*self.count
            }
        self.created = time.monotonic()

    @property
    def age(self): return time.monotonic() - self.created

    @classmethod
    def instance(cls, server:str, dataset_id:str, reload_after:int=300):
        if (
            not cls._instance                       or 
            cls._instance.server     != server      or 
            cls._instance.dataset_id != dataset_id  or 
            cls._instance.is_context                or
            cls._instance.age > reload_after
        ):
            cls._instance = cls(server, dataset_id) 
        return cls._instance
    
    @classmethod
    def context_instance(cls, server:str, context):
        cls._instance = cls(server, context, True)
        return cls._instance
 
    def get_some_prompts(self, n, seed, weighted:Optional[float]=None) -> tuple[list[str], list[int]]:
        if self.provided: 
            random.shuffle(self.provided)
            return (self.provided, [])
        assert n <= self.count, f"Requested {n} prompts but only {self.count} available"
        rng = np.random.default_rng(seed)
        p = [ pow(weighted, x) for x in self.data['score'] ] if weighted else [1.0] * self.count
        p = p / np.sum(p, dtype=float)
        chosen = rng.choice(self.count, size=n, replace=False, p=p)
        chosen = list(chosen[-x] for x in range(n))  # reverse order so first chosen is last in prompt (most recent in context)

        return (list(self.data['prompt'][x] for x in chosen), 
                list(self.data['idx'][x]    for x in chosen))

    def get_new_prompt(self, opener:str, seed:int, settings_list:list[str], use_n=10, weighted=1.0):
        opener  = opener.strip()
        if self.is_context:
            ps, ns = self.provided, []
        else:
            ps, ns  = self.get_some_prompts(use_n, seed, weighted)
        prompt  = START + (END+START).join(ps) + END + START + opener
        idx_str = ",".join([str(idx) for idx in ns])

        payload = DEFAULTS | {"prompt":prompt} | parse_settings_list(settings_list)
        response = requests.post(self.server, json=payload, verify=False)
        if response.status_code != 200: raise Exception(f"Server {self.server} returned {response.status_code}: {response.reason}")

        new_prompt:str = opener + " " + response.json()['results'][0]['text'].strip()
        return (new_prompt, idx_str)
