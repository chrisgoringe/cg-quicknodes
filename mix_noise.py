from dataclasses import dataclass
import torch

class AbstractNoise:
    def generate_noise(self, input_latent:torch.Tensor) -> torch.Tensor:
        raise NotImplementedError()
    
@dataclass
class Noise_MixedNoise(AbstractNoise):
    noise1:AbstractNoise
    noise2:AbstractNoise
    weight2:float

    def generate_noise(self, input_latent:torch.Tensor) -> torch.Tensor:
        return self.noise1.generate_noise(input_latent) * (1.0-self.weight2) + \
               self.noise2.generate_noise(input_latent) * (self.w1)

class MixNoise:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { 
            "noise1": ("NOISE",), 
            "noise2": ("NOISE",), 
            "weight2": ("float", {"default":0.01, "step":0.001})
        }}

    RETURN_TYPES = ("NOISE",)
    FUNCTION = "func"

    def func(self, noise1, noise2, weight2):
        return Noise_MixedNoise(noise1, noise2, weight2)

CLAZZES = [MixNoise]