import requests


def llm(topic, style, server, settings:str, prompting_format=0, sampler_seed=None) -> str:
    message = [[
        "<<SYS>",
        "You are an AI assistant specialized in creating detailed prompts for image generation based on given topics and styles. ",
        "Your task is to analyze the input and create a comprehensive, creative, and coherent prompt that can guide an image generation AI to produce a vivid and accurate representation of the described scene or concept.",
        "Your reply should just be the prompt",
        "<</SYS>>",
        "[INST]"
        "Create a detailed image generation prompt based on the following information:",
        f"Topic: {topic}",
        f"Style: {style}",
        "Your prompt should include the following elements :",
        "1. Main subject or character description",
        "2. Background and setting details",
        "3. Lighting, color scheme, and atmosphere",
        "4. Any specific actions or poses for characters",
        "5. Important objects or elements to include",
        "6. Overall mood or emotion to convey",
        "[/INST]"
    ]][prompting_format]

    r = {
        "max_context_length": 2048,
        "max_length": 1000,
        "quiet": False,
        "rep_pen": 1.1,
        "rep_pen_range": 256,
        "rep_pen_slope": 1,
        "temperature": 0.5,
        "tfs": 1,
        "top_a": 0,
        "top_k": 100,
        "top_p": 0.9,
        "typical": 1,
        "prompt": "\n".join(message)
    }

    if sampler_seed: r['sampler_seed'] = sampler_seed % 1000000

    def magic_cast(x:str):
        if x.lower()=='true': return True
        if x.lower()=='false': return False
        try: return int(x)
        except: pass
        try: return float(x)
        except: return x

    for s in settings.split(","):
        try:
            k,v = (x.strip() for x in s.split('='))
            r[k] = magic_cast(v)
        except ValueError: pass

    def cleaned(s:str):
        t = None
        while t is None or len(t)!=len(s):
            t = s
            s = t.replace('<SYS>','').replace('</SYS>','').strip().strip('"').replace('<','').replace('>','')
        return s

    res = requests.post(server, json=r, verify=False)
    return cleaned(res.json()['results'][0]['text'])

class LLM:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "topic": ("STRING",{"default":"", "multiline":True}),
            "style": ("STRING",{"default":"", "multiline":True}),
            "server": ("STRING", {"default":".../api/v1/generate"}),
            "settings": ("STRING",{"default":"", "multiline":True}),
            "seed": ("INT", {"default":0, "min":0, "max":999999}),
        }}

    CATEGORY = "quicknodes"
    RETURN_TYPES = ("STRING","STRING",)
    RETURN_NAMES = ("expanded", "topic", )
    FUNCTION = "func"
    
    def func(self, topic, style, server, settings, seed=None, **kwargs):
        return (llm(topic, style, server, settings, sampler_seed=seed), topic, )

CLAZZES = [LLM]