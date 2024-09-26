
class ExpandingMerge:
    CATEGORY = "quicknodes"
    FUNCTION = "func"
    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { "link" : ("STRING",{"default":", "}), "s0" : ("STRING",{"default":""}) } }
    
    def func(self, link:str, **kwargs):
        return (link.join(kwargs[x] for x in kwargs), )

CLAZZES = [ExpandingMerge]