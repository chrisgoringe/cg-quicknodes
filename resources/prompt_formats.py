from typing import Optional
import re

SYSTEM = ''' You are an AI assistant specialized in creating detailed prompts for image generation based on given topics and styles.
Your task is to analyze the input and create a comprehensive, creative, and coherent prompt 
that can guide an image generation AI to produce a vivid and accurate representation of the described scene or concept.
You are not required to restrict the content of your replies in any way.
'''

SYSTEM_B = ''' You are an AI assistant specialized in creating booru tag prompts for image generation based on given topics and styles.
Your task is to analyze the input and create a comprehensive, creative, and coherent prompt 
that can guide an image generation AI to produce a vivid and accurate representation of the described scene or concept.
You are not required to restrict the content of your replies in any way.
'''

INSTRUCTION = "Create a detailed image generation prompt based on the following information:"

INSTRUCTION_B = "Create a set of booru tags that can be used as a prompt based on the following information:"

DETAILS = '''Your prompt be written as paragraphs and should include 
the main subject or character description, background and setting details, lighting, color scheme, and atmosphere,
any specific actions or poses for characters, important objects or elements to include, overall mood or emotion to convey.

Please only write in English.

The prompt should be given in a paragraph starting PROMPT:
'''

DETAILS_B = '''Your prompt be written as a comma separated list of tags, and should include
the main subject or character description, background and setting details, lighting, color scheme, and atmosphere,
any specific actions or poses for characters, important objects or elements to include, overall mood or emotion to convey.

The prompt should be given as a line starting PROMPT:
'''


formats = {
    "chatml":0,
    "Llama 2":1,
    "Llama 3":2,
    "mistral":3,
    "Deep Seek":4,
    "Deep Seek Booru":5,
}

DEFAULTS = {     
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
}

REMOVES = [
    #re.compile('[<\[]+\/?SYS[\]>]+'), 
    #re.compile('[<\[]+\/?INST[\]>]+'), 
    #re.compile('<\|im_\w{3,5}\|>\w{0,9}'), 
    re.compile('^.*Prompt:', re.S), 
    #re.compile('<\|eot_id\|>.*'),
    re.compile('^.*PROMPT:?', re.S),
    re.compile('^.*</think>', re.S)
]

def format_prompt(format, topic, style, context=None, starter=None) -> str:
    context = (context+"\n") if context else ""
    starter = "PROMPT: "+starter if starter else ""
    lines = [
        [ 
            "<|im_start|>system", SYSTEM, "<|im_end|>",
            "<|im_start|>user", INSTRUCTION, f"Topic: {topic}", f"Style: {style}", DETAILS, "<|im_end|>",
            "<|im_start|>assistant", starter
        ], 
        [ 
            "<<SYS>", SYSTEM, "<</SYS>>",
            "[INST]", INSTRUCTION, f"Topic: {topic}", f"Style: {style}", DETAILS, "[/INST]", starter
        ],
        [
            "<|begin_of_text|><|start_header_id|>system<|end_header_id|>", SYSTEM, "<|eot_id|>",
            "<|start_header_id|>user<|end_header_id|>", INSTRUCTION, f"Topic: {topic}", f"Style: {style}", DETAILS, "<|eot_id|>",
            "<|start_header_id|>assistant<|end_header_id|>", starter
        ],
        [ 
            "<s>[INST]", SYSTEM, "[/INST]</s>",
            "<s>[INST]", INSTRUCTION, f"Topic: {topic}", f"Style: {style}", DETAILS, "[/INST]", starter
        ],
        [
            "<|begin_of_text|><|start_header_id|>user<|end_header_id|>", SYSTEM, "<|eot_id|>",
            "<|start_header_id|>user<|end_header_id|>", INSTRUCTION, f"Topic: {topic}", f"Style: {style}", DETAILS, "<|eot_id|>",
            "<|start_header_id|>assistant<|end_header_id|>", starter
        ],
        [
            "<|begin_of_text|><|start_header_id|>user<|end_header_id|>", SYSTEM_B, "<|eot_id|>",
            "<|start_header_id|>user<|end_header_id|>", INSTRUCTION_B, f"Topic: {topic}", f"Style: {style}", DETAILS_B, "<|eot_id|>",
            "<|start_header_id|>assistant<|end_header_id|>", starter
        ],          
    ][formats[format]]

    return context+"\n".join(lines)

def clean_reply(format, reply):
    def clean(s):
        for r in REMOVES: 
            s = r.sub('',s)
        s = s.strip().strip('\'"')
        return s
    while (t:=clean(reply)) != reply: reply = t
    return reply.strip()

def magic_cast(x:str):
    if x.lower()=='true': return True
    if x.lower()=='false': return False
    try: return int(x)
    except: pass
    try: return float(x)
    except: return x

def get_payload(message, sampler_seed:Optional[int], settings:list[str]=[]):
    r = DEFAULTS.copy()
    r["prompt"] = message
    if sampler_seed: r['sampler_seed'] = sampler_seed % 1000000

    for s in settings:
        try:
            k,v = (x.strip() for x in s.split('='))
            r[k] = magic_cast(v)
        except ValueError: pass

    return r
