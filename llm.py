import requests, random, os, json, datasets, codecs
from resources.prompt_formats import format_prompt, clean_reply, get_payload, formats
from resources.creative import PromptCreator, ContextList, Context, rewrite_prompt
from comfy.model_management import InterruptProcessingException
from typing import Optional, Any

def obfus(s, obf) -> str:
    if not isinstance(obf, int): obf = 1 if obf else 0
    if obf==0: return s
    if obf==1: return codecs.encode(s,'rot13')
    raise NotImplementedError("")

def defus(s, obf) -> str:
    if not isinstance(obf, int): obf = 1 if obf else 0
    if obf==0: return s
    if obf==1: return codecs.decode(s,'rot13')
    raise NotImplementedError("")

class Verifier:
    _certificates:list[str] = []
    _certificate:Optional[str|bool] = None
    directory = os.path.join(os.path.split(__file__)[0], 'client_certificates')
    
    @classmethod
    def certificates(cls) -> list[str]:
        if not cls._certificates:
            cls._certificates = [ os.path.join(cls.directory, f) for f in os.listdir(cls.directory) if f.endswith(".pem") ]
        return cls._certificates

    @classmethod
    def _post(cls, *args, **kwargs):
        return requests.post(*args, verify=cls._certificate, **kwargs)
    
    @classmethod
    def post(cls, *args, **kwargs):
        if cls._certificate:
            try:    return cls._post(*args, **kwargs)
            except: cls._certificate = None
        for c in cls.certificates():
            cls._certificate = c
            try:    return cls._post(*args, **kwargs)
            except: cls._certificate = None
        cls._certificate = False
        return cls._post(*args, **kwargs)

class ServerException(Exception): pass

class LLM:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": 
                {
                    "topic": ("STRING",{"default":"", "multiline":True}),
                    "style": ("STRING",{"default":"", "multiline":True}),
                    "server": ("STRING", {"default":".../api/v1/generate"}),
                    "settings": ("STRING",{"default":"max_length=150, temperature=0.7", "multiline":True, "tooltip":"Comma separated key=value pairs"}),
                    "seed": ("INT", {"default":0, "min":0, "max":999999}),
                    "prompt_format": ([k for k in formats], {}),
                    "active": ("BOOLEAN", {"default":True}),
                },
                "optional": {
                    "context": ("STRING", {"default":"", "multiline":True}),
                    "starter": ("STRING", {"default":"", "multiline":True}),
                }}

    CATEGORY = "quicknodes/llm"
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("expanded", "topic", )
    FUNCTION = "func"
    
    def func(self, topic, style, server, settings, seed, prompt_format,active, context=None, starter=None):
        if not active: return (topic,topic,)
        message = format_prompt(prompt_format, topic, style, context, starter)
        r = get_payload(message, sampler_seed=seed, settings=settings.split(","))
        res = Verifier.post(server, json=r)
        if res.status_code==200:
            reply = clean_reply(prompt_format, res.json()['results'][0]['text'])
        else:
            raise ServerException(f"{res.url} returned {res.status_code} : {res.reason}")
        return ((f"{starter} " if starter else "")+reply,topic,)

class LLMRewriter:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": 
                {
                    "prompt": ("STRING",{"default":"", "multiline":True}),
                    "server": ("STRING", {"default":".../api/v1/generate"}),
                    "settings": ("STRING",{"default":"max_length=150, temperature=0.7", "multiline":True, "tooltip":"Comma separated key=value pairs"}),
                },
                    "optional":
                    {
                        "extra_instructions": ("STRING", {"default":"Assistant rewrites the prompt to make it more coherent and gramatically correct.", "multiline":True})
                    }}

    CATEGORY = "quicknodes/llm"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "func"
    
    def func(self, prompt, server, settings, extra_instructions):
        return (rewrite_prompt(server, prompt, settings, extra_instructions),)

class LLLFromSummary:
    @classmethod
    def INPUT_TYPES(cls):
        return  {
            "required": {
                "server": ("STRING", {"default":".../api/v1/generate"}),
                "settings": ("STRING",{"default":"", "multiline":True, "tooltip":"Comma separated key=value pairs"}),
                "seed": ("INT", {"default":0, "min":0, "max":999999}),
            },
            "optional": { 
                "contexts":("CONTEXTS", {}),
                "summary": ("STRING", {"default":""}),
                "opener":("STRING", {"default":""})
            }
        }
    
    CATEGORY = "quicknodes/llm"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)
    FUNCTION = "func"

    def func(self, server:str, settings:str, seed:int, contexts:Optional[ContextList]=None, summary:Optional[str]=None, opener:Optional[str]=None) -> tuple[str]:
        creator = PromptCreator(server, settings)
        return (creator.get_new_prompt(summary, contexts, opener, seed), )

DS_FEATURES:dict[str,tuple[datasets.Value,Any]] = {
    'summary'        : (datasets.Value(dtype='string' ), ""), 
    'prompt'         : (datasets.Value(dtype='string' ), ""), 
    'idx'            : (datasets.Value(dtype='int64'  ), None),
    'score'          : (datasets.Value(dtype='float32'), 0.0),
}

def recast_ds(ds:datasets.Dataset) -> datasets.Dataset:
    for k in DS_FEATURES:
        if not k in ds.column_names:
            t, v = DS_FEATURES[k]
            ds = ds.add_column(name=k, feature=t, column=[v for _ in range(len(ds))], new_fingerprint=f"{random.random()}")
        else:
            ds = ds.cast_column(k, DS_FEATURES[k][0])
    return ds

class PickOldPrompt:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": 
                {
                    "seed": ("INT", {"default":0, "min":0, "max":999999}),
                    "dataset": ("STRING",{"default":"ChrisGoringe/generic", "tooltip":"Dataset or json file holding list[str|list[str,...]]"}),
                    "weighting": ("FLOAT", {"default":1.01, "min":0.1, "max":10.0, "step":0.01, "tooltip":"Values greater than 1.0 will prefer previously successful prompt contexts (dataset only)"}),
                    "remove": ("BOOLEAN", {"default":False, "tooltip":"Remove the chosen prompt (json only)"}),
                }}

    CATEGORY = "quicknodes/llm"
    RETURN_TYPES = ("STRING","INT",)
    RETURN_NAMES = ("prompt","idx",)
    FUNCTION = "func"    

    def func(self, seed:int, dataset:str, weighting:float, remove:bool) -> tuple[str, int]:
        for _ in range(3):
            try:
                return self._func(seed, dataset, weighting, remove)
            except Exception as e:
                print(f"PickOldPrompt: Caught exception {e}, retrying")
        return ("", 0)

    def _func(self, seed:int, dataset:str, weighting:float, remove:bool) -> tuple[str, int]:
        if dataset.endswith('.json'):
            if seed: random.seed(seed)
            with (open(dataset, 'r', encoding="utf8") as fh): data:list[str|list] = json.load(fh)
            print(f"PickOldPrompt: Loaded {len(data)} prompts from {dataset}")
            n = random.randint(0, len(data)-1)
            prompt = data.pop(n)
            if not isinstance(prompt, str): prompt = str(prompt[0])
            if remove: 
                with (open(dataset, 'w', encoding="utf8") as fh): json.dump(data, fh, indent=2)
                print(f"PickOldPrompt: Saved  {len(data)} prompts to {dataset}")
            return (prompt, 0)

        if os.path.exists(dataset) and os.path.isdir(dataset):
            ds = datasets.load_from_disk(dataset)
            assert isinstance(ds, datasets.Dataset)
            ds = recast_ds(ds)
            contexts:ContextList = ContextList.from_dataset(ds, n=1, seed=seed, weighting=weighting)
            return (contexts.contexts[0].prompt, contexts.infos[0])
        else:
            ds = datasets.load_dataset(dataset, split='train')
            ps = [str(x) for x in ds['prompt']]
            return(random.choice(ps),0)

    
class PickContexts:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": 
                {
                    "seed": ("INT", {"default":0, "min":0, "max":999999}),
                    "dataset": ("STRING",{"default":"ChrisGoringe/flux_prompts", "tooltip":"Dataset or json file holding list[str|list[str,...]]"}),
                    "weighting": ("FLOAT", {"default":1.0, "min":0.1, "max":10.0, "step":0.01, "tooltip":"Values greater than 1.0 will prefer previously successful prompt contexts"}),
                    "count": ("INT", {"default":10, "min":0, "max":100, "tooltip":"Number of old prompts to use to create the context"}),
                }}

    CATEGORY = "quicknodes/llm"
    RETURN_TYPES = ("CONTEXTS","STRING")
    RETURN_NAMES = ("contexts", "info")
    FUNCTION = "func"
    
    def func(self, seed:int, dataset:str, weighting:float, count:int, **kwargs) -> tuple[ContextList, str]:
        dataset = dataset.strip()
        if count and dataset:
            if dataset.endswith('.json'):
                if seed: random.seed(seed)
                with (open(dataset, 'r', encoding="utf8") as fh): data:list[str|list] = json.load(fh)
                if len(data)<count: raise ValueError(f"{dataset} has only {len(data)} entries, cannot pick {count}")
                random.shuffle(data)
                contexts = ContextList(contexts = [Context("", d if isinstance(d,str) else d[0]) for d in data[:count]], infos = [0 for _ in range(count)] )
            else:
                ds = datasets.load_from_disk(dataset)
                if not isinstance(ds, datasets.Dataset): raise NotImplementedError(f"Dataset {dataset} is not a single dataset")
                ds = recast_ds(ds)
                contexts = ContextList.from_dataset(ds, n=count, seed=seed, weighting=weighting)
            return ( contexts, contexts.info, )
        else:
            return ( ContextList([]), "", )
    
class JumbleContexts:
    @classmethod
    def INPUT_TYPES(cls):
        return { "required": {
                    "c1": ("CONTEXTS", {}),
                }, "optional": {
                    "c2": ("CONTEXTS", {}),
                    "c3": ("CONTEXTS", {}),
                    "c4": ("CONTEXTS", {}),
                    "seed": ("INT", {"default":-1, "min":0, "max":999999}),
                }}
    
    RETURN_TYPES = ("CONTEXTS","STRING",)
    RETURN_NAMES = ("contexts", "info")
    CATEGORY = "quicknodes/llm"
    FUNCTION = "func"

    def func(self, c1:ContextList, c2:Optional[ContextList]=None, c3:Optional[ContextList]=None, c4:Optional[ContextList]=None, seed:int=0) -> tuple[ContextList, str]:
        c = c1.copy().add_from(c2).add_from(c3).add_from(c4).shuffle(seed)
        return ( c, c.info, )

class PromptDump:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING",{"default":""}),
                "folder": ("STRING",{"default":"promptdump"}),
                "obf": (["0", "1"], {"default":"1", "tooltip":"Obfuscation level (0=none, 1=rot13)"}),
            },
            "optional": {
                "info": ("STRING", {"default":""}),
            }
        }

    CATEGORY = "quicknodes/llm"
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "func"
    
    def func(self, prompt, folder, obf:int, info=None):
        if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)

        filename = os.path.join(folder, f"{random.randint(100000,999999)}.json")
        payload = {"prompt":obfus(prompt, obf), "obfus":obf}
        if info: 
            infos = info.split('|')
            if len(infos)==2: infos[1] = obfus(infos[1], obf)
            payload['info'] = '|'.join(infos)
        with open(filename, 'w') as fh: json.dump(payload, fh)
        return ()

class PromptUndump:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": 
                    {
                        "folder": ("STRING",{"default":"promptdump"}),
                        "mode": (["random-and-delete", "random-and-keep", "deterministic-and-delete", "deterministic-and-keep"], {}),
                        "seed": ("INT", {"default":0, "min":0, "max":999999, "tooltip":"Seed for random selection"}),
                    }
                }

    CATEGORY = "quicknodes/llm"
    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("prompt","info")
    FUNCTION = "func"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        return float("NaN")
    
    def func(self, folder, mode, seed):
        filenames = [os.path.join(folder,f) for f in os.listdir(folder) if os.path.splitext(f)[1]==".json"]
        if "random" in mode:
            if seed: random.seed(seed)
        else:
            filenames.sort()
        if not filenames: raise InterruptProcessingException()
        filename = random.choice(filenames) if "random" in mode else filenames[0]
        with open(filename, 'r') as fh: data = json.load(fh)
        if "delete" in mode: os.remove(filename)

        if (obf:=data.get('obfus',0)): 
            data['prompt'] = defus(data['prompt'], obf)
            infos = data['info'].split('|') if 'info' in data else []
            if len(infos)==2: infos[1] = defus(infos[1], obf)
            data['info'] = '|'.join(infos)
        return ( data['prompt'], data['info'] )          
    
CLAZZES:list[Any] = [LLM, LLLFromSummary, PickContexts, JumbleContexts, LLMRewriter, PickOldPrompt] 

