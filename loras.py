from nodes import LoraLoader, LoraLoaderModelOnly
import os

class LoraByNameAddin:
    def get_loras(self, lora_name, directory, suffix="") -> list[tuple[str, float]]:
        lora_names = []
        for entry in [n.strip() for n in lora_name.split(',') if n.strip()]:
            if not ':' in entry: entry += ':1.0'
            name, strength = entry.split(':')
            name = name.strip()
            try:
                strength = float(strength.strip())
            except ValueError:
                print(f"Failed to parse strength '{strength}' for lora '{name}', defaulting to 1.0")
                strength = 1.0

            name = f"{os.path.splitext(name)[0]}{suffix}.safetensors"

            if directory: name = os.path.join(directory, name)
            lora_names.append((name, strength))
        return lora_names

class LoadLoraByName(LoraLoader, LoraByNameAddin):
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
        for name, strength in self.get_loras(lora_name, directory):
            try: model, clip = self.load_lora(model, clip, name, strength, strength)
            except FileNotFoundError as e: print(f"{e}")
        return(model, clip)

class LoadLoraModelOnlyByName(LoraLoaderModelOnly, LoraByNameAddin):
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The diffusion model the LoRA will be applied to."}),
                "lora_name": ("STRING", {"tooltip": "The name of the LoRA; optionally :x for strength (else strength = 1.0)"}),
            },
            "optional": {
                "directory": ("STRING", {"tooltip": "The subdirectory the LoRA is in"}),
                "suffix": ("STRING", {"tooltip": "Suffix to add to lora name before .safetensors", "default": ""}),
            }
        }
    CATEGORY = "quicknodes"
    FUNCTION = "func"

    def func(self, model, lora_name, directory="", suffix=""):
        for name, strength in self.get_loras(lora_name, directory, suffix):
            try: model = self.load_lora_model_only(model, name, strength)[0]
            except FileNotFoundError as e: print(f"{e}")
        return (model, )

CLAZZES = [] # [LoadLoraByName, LoadLoraModelOnlyByName]