import datasets, random, requests
from .prompt_formats import magic_cast

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
    def __init__(self, server, dataset_id):
        self.server = server
        self.dataset_id = dataset_id
        self.ds = datasets.load_dataset(dataset_id)['train']

    @classmethod
    def get_creator(cls, server, dataset_id):
        if (not cls.instance or cls.instance.server!=server or cls.instance.dataset_id!=dataset_id):
            cls.instance = cls(server, dataset_id)
        return cls.instance

    def get_some_prompts(self, n, seed):
        seed = seed or random.randint(1,1e8)
        self.ds = self.ds.shuffle(seed)
        return self.ds['prompt'][:n]

    def get_new_prompt(self, opener:str, seed:int, settings_list:list[str]):
        ps = self.get_some_prompts(50, seed)
        old = START + (END+START).join(ps) + END + START + opener
        payload = DEFAULTS | {"prompt":old} | { s.split('=')[0].strip():magic_cast(s.split('=')[1].strip()) for s in settings_list }
        res = requests.post(self.server, json=payload, verify=False)
        return (" ".join((opener, res.json()['results'][0]['text'].strip()))).strip()
    
    def changed(self, server, dataset_id):
        return (server!=self.server or dataset_id!=self.dataset_id)
