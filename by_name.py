from nodes import LoraLoaderModelOnly

class LoraLoaderFromString(LoraLoaderModelOnly):
    @classmethod
    def INPUT_TYPES(s):
        return {"required": { "model": ("MODEL",),
                              "lora_name": ("STRING", {}),
                              "strength_model": ("FLOAT", {"default": 1.0, "min": -100.0, "max": 100.0, "step": 0.01}),
                              }}    

CLAZZES = [LoraLoaderFromString]