import requests, json
from resources.prompt_formats import format_prompt, clean_reply, get_payload, formats


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
                        "dataset": ("STRING",{"default":"ChrisGoringe/flux_prompts"}),
                    }}

        CATEGORY = "quicknodes"
        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("prompt",)
        FUNCTION = "func"
        
        def func(self, opener, server, settings, seed, dataset):
            creator = Creator.get_creator(server, dataset)
            settings_list = [s.strip() for s in settings.split(',') if s.strip() and '=' in s]
            prompt  = creator.get_new_prompt(opener, seed, settings_list)
            return (prompt,)

    CLAZZES.append(LLMRandom)

except Exception as e:
    print(e)
    
