class HtmlNode:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":{} }
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "func"
    def func(self):
        return ()
    
CLAZZES = [HtmlNode]