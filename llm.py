import requests, random, os, json, time
from resources.prompt_formats import format_prompt, clean_reply, get_payload, formats
from comfy.model_management import InterruptProcessingException
from ui_decorator import ui_signal

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

    CATEGORY = "quicknodes"
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("expanded", "topic", )
    FUNCTION = "func"
    
    def func(self, topic, style, server, settings, seed, prompt_format,active, context=None, starter=None):
        if not active: return (topic,topic,)
        message = format_prompt(prompt_format, topic, style, context, starter)
        r = get_payload(message, sampler_seed=seed, settings=settings.split(","))
        res = requests.post(server, json=r, verify=False)
        if res.status_code==200:
            reply = clean_reply(prompt_format, res.json()['results'][0]['text'])
        else:
            raise ServerException(f"{res.url} returned {res.status_code} : {res.reason}")
        return ((f"{starter} " if starter else "")+reply,topic,)
    
CLAZZES = [LLM,]

import codecs

def obfus(s, obf) -> str:
    if not isinstance(obf, int): obf = 1 if obf else 0
    if obf==1: return codecs.encode(s,'rot13')
    raise NotImplementedError("")

def defus(s, obf) -> str:
    if not isinstance(obf, int): obf = 1 if obf else 0
    if obf==1: return codecs.decode(s,'rot13')
    raise NotImplementedError("")
   
try:
    from resources.creative import Creator
    class LLMRandom:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": 
                    {
                        "opener": ("STRING",{"default":"", "multiline":True}),
                        "server": ("STRING", {"default":".../api/v1/generate"}),
                        "settings": ("STRING",{"default":"", "multiline":True, "tooltip":"Comma separated key=value pairs"}),
                        "seed": ("INT", {"default":0, "min":0, "max":999999}),
                    },
                    "optional": {"context":("STRING", {"default":"", "tooltip":"List of context prompts joined on '|'"})}
                    }

        CATEGORY = "quicknodes"
        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("prompt",)
        FUNCTION = "func"
        
        def func(self, opener:str, server:str, settings:str, seed:int, context:str="", **kwargs):
            creator = Creator.context_instance(server, context)
            settings_list = [s.strip() for s in settings.split(',') if s.strip() and '=' in s]
            prompt, _  = creator.get_new_prompt(opener=opener, seed=seed, settings_list=settings_list)
            return (prompt,)
        
    def count(folder, ext=None):
        return len([f for f in os.listdir(folder) if (ext is None or os.path.splitext(f)[1]==ext)])
    
    @ui_signal(['display_text'])
    class PromptDump:
        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "prompt": ("STRING",{"default":""}),
                    "folder": ("STRING",{"default":"promptdump"}),
                    "maximum": ("INT",{"default":5, "tooltip":"Skip if there are already this many or more in the folder"}),
                    "sleeponskip": ("INT",{"default":1, "tooltip":"If skipping, sleep for this number of seconds"}),
                },
                "optional": {
                    "info": ("STRING", {"default":""}),
                }
            }

        CATEGORY = "quicknodes/utils"
        RETURN_TYPES = ("INT",)
        RETURN_NAMES = ("count",)
        OUTPUT_NODE = True
        FUNCTION = "func"
        

        def func(self, prompt, folder, info=None, maximum=5, sleeponskip=1):
            obf = 1
            if count(folder, ".json")<maximum:
                filename = os.path.join(folder, f"{random.randint(100000,999999)}.json")
                payload = {"prompt":obfus(prompt, obf), "obfus":obf}
                if info: 
                    infos = info.split('|')
                    if len(infos)==2: infos[1] = obfus(infos[1], obf)
                    payload['info'] = '|'.join(infos)
                with open(filename, 'w') as fh: json.dump(payload, fh)
            else:
                time.sleep(sleeponskip)
            n = count(folder, ".json")
            return (n, f"{n} in folder")
    
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

        CATEGORY = "quicknodes/utils"
        RETURN_TYPES = ("STRING","STRING","INT")
        RETURN_NAMES = ("prompt","info","left")
        FUNCTION = "func"

        @classmethod
        def IS_CHANGED(s, **kwargs):
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
            n = count(folder, ".json")
            if (obf:=data.get('obfus',0)): 
                data['prompt'] = defus(data['prompt'], obf)
                infos = data['info'].split('|')
                if len(infos)==2: infos[1] = defus(infos[1], obf)
                data['info'] = '|'.join(infos)
            return ( data['prompt'], data['info'], n )        

    class PickFromDataset:
        @classmethod
        def INPUT_TYPES(cls):
            return {"required": 
                    {
                        "seed": ("INT", {"default":0, "min":0, "max":999999}),
                        "dataset": ("STRING",{"default":"ChrisGoringe/flux_prompts"}),
                        "weighting": ("FLOAT", {"default":1.0, "min":0.1, "max":10.0, "step":0.01, "tooltip":"Values greater than 1.0 will prefer previously successful prompt contexts"}),
                        "count": ("INT", {"default":10, "min":1, "max":100, "tooltip":"Number of old prompts to use to create the context"}),
                    }}

        CATEGORY = "quicknodes/datasets"
        RETURN_TYPES = ("STRING","STRING","INT","STRING")
        RETURN_NAMES = ("prompts","context","infos","info")
        OUTPUT_IS_LIST = (True,False,True,False)
        FUNCTION = "func"
        
        def func(self, seed:int, dataset:str, weighting:float, count:int, **kwargs):
            creator = Creator.instance(None, dataset.strip())
            prompts, infos  = creator.get_some_prompts(n=count, seed=seed, weighted=weighting)
            return (prompts,"|".join(prompts),infos,",".join([str(idx) for idx in infos]))  

    class Jumble:
        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required":  {
                    "stringlist1": ("STRING", {"default":""}),
                },
                "optional": {
                    "stringlist2": ("STRING", {"default":""}),
                    "stringlist3": ("STRING", {"default":""}),
                    "stringlist4": ("STRING", {"default":""}),
                    "seed": ("INT", {"default":0, "min":0, "max":999999}),
                    "joiner": ("STRING", {"default":"|"}),
                }
            }

        CATEGORY = "quicknodes/datasets"
        RETURN_TYPES = ("STRING","STRING",)
        RETURN_NAMES = ("prompts","context",)
        INPUT_IS_LIST = True
        OUTPUT_IS_LIST = (True,False)
        FUNCTION = "func"
        
        def func(self, stringlist1:list[str], stringlist2:list[str]=[], stringlist3:list[str]=[], stringlist4:list[str]=[], 
                 seed:list[int]=[0,], joiner:list[str]=["|",] ):
            outlist = stringlist1 + stringlist2 + stringlist3 + stringlist4
            outlist = [o.strip() for o in outlist if o.strip()]
            random.seed(seed[0])
            random.shuffle(outlist)

            return ( outlist, joiner[0].join(outlist), )               
        
    CLAZZES.extend([LLMRandom, Jumble, PickFromDataset, PromptDump, PromptUndump])

except Exception as e:
    print(e)
    
