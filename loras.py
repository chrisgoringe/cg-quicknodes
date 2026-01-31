from nodes import LoraLoader, LoraLoaderModelOnly
import os

class LoadLoraByName(LoraLoader):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The diffusion model the LoRA will be applied to."}),
                "clip": ("CLIP", {"tooltip": "The CLIP model the LoRA will be applied to."}),
                "lora_name": ("STRING", {"tooltip": "The name of the LoRA; optionally :x for strength (else strength = 1.0)"}),
            },
            "optional": {
                "directory": ("STRING", {"tooltip": "The subdirectory the LoRA is in"})
            }
        }
    CATEGORY = "quicknodes"
    FUNCTION = "func"

    def func(self, model, clip, lora_name, directory=""):
        if not lora_name: return(model, clip)
        strength_model = 1.0
        if ':' in lora_name:
            try:
                lora_name, strength_model = lora_name.split(':')
                strength_model = float(strength_model.strip())
            except Exception as e: 
                print(f"Failed to parse lora:strength '{e}'")
                strength_model = 0.0
            lora_name = lora_name.strip()
        if not lora_name.endswith('.safetensors'): lora_name += ".safetensors"
        if directory: lora_name = os.path.join(directory, lora_name)
        try:
            return self.load_lora(model, clip, lora_name, strength_model, strength_model)
        except FileNotFoundError as e:
            print(f"{e}")
            return(model, clip)

class LoadLoraModelOnlyByName(LoraLoaderModelOnly):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The diffusion model the LoRA will be applied to."}),
                "lora_name": ("STRING", {"tooltip": "The name of the LoRA; optionally :x for strength (else strength = 1.0)"}),
            },
            "optional": {
                "directory": ("STRING", {"tooltip": "The subdirectory the LoRA is in"})
            }
        }
    CATEGORY = "quicknodes"
    FUNCTION = "func"

    def func(self, model, lora_name, directory=""):
        if not lora_name: return(model, )
        strength_model = 1.0
        if ':' in lora_name:
            lora_name, strength_model = lora_name.split(':')
            try: strength_model = float(strength_model.strip())
            except Exception as e: print(e)
            lora_name = lora_name.strip()
        if not lora_name.endswith('.safetensors'): lora_name += ".safetensors"
        if directory: lora_name = os.path.join(directory, lora_name)
        return self.load_lora_model_only(model, lora_name, strength_model)

CLAZZES = [LoadLoraByName, LoadLoraModelOnlyByName]