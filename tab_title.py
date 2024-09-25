from server import PromptServer
class TabTitle:
    CATEGORY = "quicknodes"
    FUNCTION = "func"
    RETURN_TYPES = ("STRING",)
    OUTPUT_NODE = True
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { "title" : ("STRING",{"default":""}) } }
    
    def func(self, title):
        PromptServer.instance.send_sync("cg.quicknodes.tabtitle", {"message":title})
        return (title,)


CLAZZES = [TabTitle]