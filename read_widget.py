class ReadWidget:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
                    "node": ("INT", {"default":0}),
                    "widget": ("STRING", {"default":""}), 
                    "if_absent":("STRING",{"default":"not found"})
                },
                "hidden" : { 
                    "prompt":"PROMPT" 
                } }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "func"
    def func(self, node, widget, if_absent, prompt):
        try:
            w = prompt[str(node)]['inputs'][widget]
            w = f"{w}" if not isinstance(w,list) else f"{widget} in an input on #{node}"
        except:
            w = if_absent
        return (w,)
    
    @classmethod
    def IS_CHANGED(self, node, widget, if_absent, prompt):
        return self.func(node, widget, if_absent, prompt)[0]
    
CLAZZES = [ReadWidget]