
class ExpandingMerge:
    CATEGORY = "quicknodes"
    FUNCTION = "func"
    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { "link" : ("STRING",{"default":", "}), }, "optional": { "s0" : ("STRING",{"default":"", "force_input":True}) } }
    
    def func(self, link:str, **kwargs):
        return (link.join(kwargs[x] for x in sorted(kwargs)), )

CLAZZES = [ExpandingMerge]