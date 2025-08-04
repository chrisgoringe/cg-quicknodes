import comfy.model_management as model_management


class ClearAll:
    CATEGORY = "quicknodes"

    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "latent": ("LATENT", {}), } }

    RETURN_TYPES = ("LATENT", )
    FUNCTION = "func"

    def func(self, latent):
        model_management.unload_all_models()
        model_management.soft_empty_cache(True)
        return (latent,)


CLAZZES = [ClearAll,]
