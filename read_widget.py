class ReadWidget:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "node": ("INT", {"default":0}), "widget": ("STRING", {"default":""}), },
                "hidden" : { "prompt":"PROMPT" } }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)
    FUNCTION = "func"
    def func(self, node, widget, prompt):
        try:
            w = prompt[str(node)]['inputs'][widget]
            w = f"{w}" if not isinstance(w,list) else f"{widget} in an input on #{node}"
        except:
            w = f"{widget} not found on node #{node}"
        return (w,)
    
    @classmethod
    def IS_CHANGED(self, node, widget, prompt):
        return self.func(node, widget, prompt)[0]
    
CLAZZES = [ReadWidget]