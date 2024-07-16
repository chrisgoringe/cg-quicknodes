from dataclasses import dataclass
import torch
from typing import Union

class AbstractNoise:
    def generate_noise(self, input_latent:torch.Tensor) -> torch.Tensor:
        raise NotImplementedError()
    
@dataclass
class Noise_MixedNoise(AbstractNoise):
    noise1:AbstractNoise
    noise2:AbstractNoise
    weight2:float
    mask:Union[torch.Tensor, None] = None

    @property
    def seed(self): return self.noise1.seed

    def generate_noise(self, input_latent:torch.Tensor) -> torch.Tensor:
        noise1 = self.noise1.generate_noise(input_latent)
        noise2 = self.noise2.generate_noise(input_latent)
        mixed_noise = noise1 * (1.0-self.weight2) + noise2 * (self.weight2)
        
        if self.mask:
            mask = torch.nn.functional.interpolate(self.mask.unsqueeze(), size=input_latent.size, mode='bilinear')
            mixed_noise = mixed_noise * (mask) + noise1 * (1.0-mask)
        return (mixed_noise,)

class MixNoise:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { 
            "required":  { 
                "noise1": ("NOISE",), 
                "noise2": ("NOISE",), 
                "weight2": ("FLOAT", {"default":0.01, "step":0.001})
                }, 
            "optional" : {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("NOISE",)
    FUNCTION = "func"

    def func(self, noise1, noise2, weight2, mask=None):
        return (Noise_MixedNoise(noise1, noise2, weight2, mask),)

CLAZZES = [MixNoise]