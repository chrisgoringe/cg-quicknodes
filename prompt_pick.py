import json, os

class PromptPick:
    path = os.path.join(os.path.dirname(__file__), "resources", "prompt_pick.json")
    
    options = {}
    if not os.path.exists(path):
        print(f"{path} not found")
    else:
        with open(path, "r") as f: options = json.load(f)

    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "pick": (list(k for k in PromptPick.options),{} ) } }
    RETURN_TYPES = ("STRING","STRING")
    RETURN_NAMES = ("short","long")
    FUNCTION = "func"
    def func(self,pick):
        with open(PromptPick.path, "r") as f: options = json.load(f)
        p0 = options[pick][0]
        p1 = " ".join(options[pick])
        return (p0,p1,)
    
    @classmethod
    def IS_CHANGED(self,pick):
        with open(PromptPick.path, "r") as f: options = json.load(f)
        return (" ".join(options[pick]),)
    
CLAZZES = [PromptPick]