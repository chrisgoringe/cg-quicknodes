END = "<|im_end|>"
START = "<|im_start|>"

DEFAULTS:dict[str,str|float|int|bool|list[str]] = {     
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
    "dry_multiplier":0.8, 
    "dry_allowed_length":2, 
    "dry_base":1.75
}

def magic_cast(x:str) -> bool|int|float|str:
    if x.lower()=='true': return True
    if x.lower()=='false': return False
    try: return int(x)
    except: pass
    try: return float(x)
    except: return x

def parse_settings_list(settings_list:list[str]) -> dict[str,int|float|str|bool]:
    return { s.split('=')[0].strip():magic_cast(s.split('=')[1].strip()) for s in settings_list }

def wrap(role, text):
    return f"{START}{role}\n{text}\n{END}\n" if text else f"{START}{role}\n"

def get_base_payload(settings:str) -> dict[str,str|float|int|bool|list[str]]:
    settings_list = [s.strip() for s in settings.split(',') if s.strip() and '=' in s]
    settings_dict = parse_settings_list(settings_list)
    base_payload = DEFAULTS.copy()
    for k in settings_dict: base_payload[k] = settings_dict[k]
    return base_payload