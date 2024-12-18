class Simple:
    CATEGORY = "quicknodes/simples"
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { s.RETURN_TYPES[0].lower(): (s.RETURN_TYPES[0],s.extras()), } }
    RETURN_TYPES:tuple[str] = None
    FUNCTION = "func"
    def func(self, **kwargs): return ( kwargs[self.RETURN_TYPES[0].lower()], )

class SimpleInt(Simple):
    RETURN_TYPES = ("INT",)
    @classmethod
    def extras(s): return {"default":0}    

class SimpleFloat(Simple):
    RETURN_TYPES = ("FLOAT",)
    @classmethod
    def extras(s): return {"default":0.0, "min":-10000, "max":10000}        

class SimpleString(Simple):
    RETURN_TYPES = ("STRING",)
    @classmethod
    def extras(s): return {"default":""}

class SimpleMultilineString(Simple):
    RETURN_TYPES = ("STRING",)
    @classmethod
    def extras(s): return {"default":"", "multiline":True}

class SimpleLatent(Simple):
    RETURN_TYPES = ("LATENT",)
    @classmethod
    def extras(s): return {}    

CLAZZES = [SimpleInt,SimpleFloat,SimpleString,SimpleMultilineString, SimpleLatent]