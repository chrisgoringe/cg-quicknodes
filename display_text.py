from server import PromptServer

class DisplayText:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : {},
                "optional" : { "text": ("*", {"default":"", "forceInput":True}), },
                "hidden": { "id": "UNIQUE_ID" } }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "func"
    OUTPUT_NODE = True

    def func(self, id, text=""):
        text = f"{text}"
        PromptServer.instance.send_sync("cg.quicknodes.textmessage", {"id": id, "message":text})
        print(f"{id}:{text}")
        return ()
    
class DisplayLength:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return {"required" : {},
                "optional" : { "anything": ("*", {"default":"", "forceInput":True}), },
                "hidden": { "id": "UNIQUE_ID" } }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "func"
    OUTPUT_NODE = True

    def func(self, id, anything=""):
        try:
            text = f"{len(anything)}"
        except:
            text = "doesn't support __len__"
        PromptServer.instance.send_sync("cg.quicknodes.textmessage", {"id": id, "message":text})
        print(f"{id}:{text}")
        return ()
    
CLAZZES = [DisplayText, DisplayLength]