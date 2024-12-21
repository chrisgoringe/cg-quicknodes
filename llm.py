import requests, json
from resources.prompt_formats import format_prompt, clean_reply, get_payload, formats

class ServerException(Exception): pass

class LLM:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "topic": ("STRING",{"default":"", "multiline":True}),
            "style": ("STRING",{"default":"", "multiline":True}),
            "server": ("STRING", {"default":".../api/v1/generate"}),
            "settings": ("STRING",{"default":"max_length=150, temperature=0.7", "multiline":True, "tooltip":"Comma separated key=value pairs"}),
            "seed": ("INT", {"default":0, "min":0, "max":999999}),
            "prompt_format": ([k for k in formats], {}),
            "active": ("BOOLEAN", {"default":True}),
        }}

    CATEGORY = "quicknodes"
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("expanded", "topic", )
    FUNCTION = "func"
    
    def func(self, topic, style, server, settings, seed, prompt_format,active):
        if not active: return (topic,topic,)
        message = format_prompt(prompt_format, topic, style)
        r = get_payload(message, sampler_seed=seed, settings=settings.split(","))
        res = requests.post(server, json=r, verify=False)
        if res.status_code==200:
            reply = clean_reply(prompt_format, res.json()['results'][0]['text'])
        else:
            raise ServerException(f"{res.url} returned {res.status_code} : {res.reason}")
        return (reply,topic,)
    
class Stash:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": { "text":("STRING",{"default":""}), "file":("STRING",{"default":"stash.jsonl"}) }}
    CATEGORY = "quicknodes"
    RETURN_TYPES = ()
    OUTPUT_NODE = True
    FUNCTION = "func"    

    def func(self, text, file):
        with open(file, 'a+') as f:
            print(json.dumps({"prompt":text}), file=f)
        return ()
    
class Unstash:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":{"file":("STRING",{"default":"stash.jsonl"}) }}
    CATEGORY = "quicknodes"
    RETURN_TYPES = ("STRING",)
    FUNCTION = "func"   

    def __init__(self):
        self.index = -1
        self.list = None

    def func(self, file):
        if not self.list:
            self.list = []
            with open(file, 'r') as f:
                for line in f.readlines():
                    self.list += [json.loads(line)['prompt'],]
        self.index += 1
        return (self.list[self.index],)

CLAZZES = [LLM, Stash, Unstash]