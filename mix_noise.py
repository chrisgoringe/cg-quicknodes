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
    renormalise:bool
    mask:Union[torch.Tensor, None] = None

    @property
    def seed(self): return self.noise1.seed

    def generate_noise(self, input_latent:torch.Tensor) -> torch.Tensor:
        noise1 = self.noise1.generate_noise(input_latent)
        noise2 = self.noise2.generate_noise(input_latent)
        mixed_noise = noise1 * (1.0-self.weight2) + noise2 * (self.weight2)
        
        if self.mask is not None:
            while len(self.mask.shape)<4: self.mask.unsqueeze_(0)
            mask:torch.Tensor = torch.nn.functional.interpolate(self.mask, size=input_latent['samples'].shape[-2:], mode='bilinear')
            mask = mask.expand(-1,noise1.shape[1],-1,-1)
            mixed_noise = mixed_noise * (mask) + noise1 * (1.0-mask)

        if self.renormalise:
            std, mean = torch.std_mean(mixed_noise)
            mixed_noise = (mixed_noise - mean)/(std+1e-8)

        return mixed_noise

class MixNoise:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { 
            "required":  { 
                "noise1": ("NOISE",), 
                "noise2": ("NOISE",), 
                "weight2": ("FLOAT", {"default":0.01, "step":0.001}),
                "renormalise": (["yes","no"],),
                }, 
            "optional" : {
                "mask": ("MASK",),
            }
        }

    RETURN_TYPES = ("NOISE",)
    FUNCTION = "func"

    def func(self, noise1, noise2, weight2, renormalise, mask=None):
        return (Noise_MixedNoise(noise1, noise2, weight2, renormalise=='yes', mask),)

CLAZZES = [MixNoise]