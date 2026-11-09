import json, os
from pathlib import Path

path = Path(__file__).parent / 'resources' / 'prompt_pick.json'

if path.exists():
    class PromptPick:
        with open(path, "r") as f: options = json.load(f)

        CATEGORY = "quicknodes"
        @classmethod    
        def INPUT_TYPES(cls):
            return { "required":  { "pick": (list(k for k in PromptPick.options),{} ) } }
        RETURN_TYPES = ("STRING","STRING")
        RETURN_NAMES = ("short","long")
        FUNCTION = "func"
        def func(self,pick):
            with open(path, "r") as f: options = json.load(f)
            p0 = options[pick][0]
            p1 = " ".join(options[pick])
            return (p0,p1,)
        
        @classmethod
        def IS_CHANGED(cls,pick):
            with open(path, "r") as f: options = json.load(f)
            return (" ".join(options[pick]),)
        
    CLAZZES = [PromptPick]
else:
    print(f"{path} not found; PromptPick not loaded")