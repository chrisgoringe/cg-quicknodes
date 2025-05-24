import datasets, random, requests, time
from .prompt_formats import magic_cast
from math import pow
from typing import Optional

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
    instance = None
    last_created = None
    stale_time = 300
    def __init__(self, server, dataset_id):
        self.server = server
        self.dataset_id = dataset_id
        try:
            self.ds = datasets.load_dataset(dataset_id)['train']
        except:
            self.ds = datasets.load_from_disk(dataset_id)
        prompts = self.ds['prompt']
        self.count = len(prompts)
        self.data  = {
            'prompt':prompts,  
            'idx'   :self.ds['idx'] if 'idx' in self.ds.column_names else [0]*self.count, 
            'score' :self.ds['score'] if 'score' in self.ds.column_names else [0]*self.count
        }


    @classmethod
    def get_creator(cls, server, dataset_id):
        if (
            not cls.instance or 
            cls.instance.server!=server or 
            cls.instance.dataset_id!=dataset_id or 
            (time.monotonic()-cls.last_created)>cls.stale_time
        ):
            cls.instance = cls(server, dataset_id) 
            cls.last_created = time.monotonic()
        return cls.instance
 
    def get_some_prompts(self, n, seed, weighted:Optional[float]=None) -> tuple[list[str], list[int]]:
        seed = seed or random.randint(1,1e8)
        random.seed(seed)
        weights = [ pow(weighted, x) for x in self.data['score'] ] if weighted else None
        chosen = random.choices(population = list(range(0,self.count)), weights=weights, k=n)

        return (list(self.data['prompt'][x] for x in chosen), 
                list(self.data['idx'][x] for x in chosen))

    def get_new_prompt(self, opener:str, seed:int, settings_list:list[str], use_n=10, weighted=1.0):
        ps, idxes = self.get_some_prompts(use_n, seed, weighted)
        old = START + (END+START).join(ps) + END + START + opener
        payload = DEFAULTS | {"prompt":old} | { s.split('=')[0].strip():magic_cast(s.split('=')[1].strip()) for s in settings_list }
        res = requests.post(self.server, json=payload, verify=False)
        return (" ".join((opener, res.json()['results'][0]['text'].strip()))).strip() , ",".join([str(idx) for idx in idxes])
    
    def changed(self, server, dataset_id):
        return (server!=self.server or dataset_id!=self.dataset_id)
