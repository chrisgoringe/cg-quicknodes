import torch
from comfy.model_patcher import ModelPatcher

def create_weight_list(length:int, start:float, intermediates:list[tuple[float,float]], end:float) -> list[float]:
    points = [(0.0,start),] + intermediates + [(1.0,end),]
    def value(fraction):
        for i in range(len(points)):
            if fraction >= points[i][0] and fraction <= points[i+1][0]:
                f = (fraction - points[i][0]) / (points[i+1][0] - points[i][0])
                return ((1-f)*points[i][1] + f*points[i+1][1])
        raise Exception()
    return  [ value(x/(length-1)) for x in range(length) ]

class WanModelLatentSlicer:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required":{
            "model": ("MODEL",),
            "subsize": ("INT", {"default":81, "min":5, "step":4}),
            "step": ("INT", {"default":32, "min":4, "step":4}),
        }}
    CATEGORY = "quicknodes/models"
    RETURN_TYPES = ("MODEL",)
    FUNCTION = "func"    


    def func(self, model:ModelPatcher, subsize:int, step:int):
        subsize = 1 + (subsize-1)//4
        step    = step // 4

        if step>subsize: raise Exception("Step can't be larger than subsize")

        def wrapper(fn, args):
            input:torch.Tensor = args['input']

            L = input.shape[2]

            total_out = torch.zeros_like(input)
            scale_out = torch.zeros_like(input)
            ones      = torch.ones_like(input)

            subsize_ = min(L, subsize)
            starts   = list(range(0, L-subsize_, step)) + [L-subsize_,]
            W        = torch.tensor(create_weight_list(subsize_, 0.1, [(0.5,1.0),], 0.1), device=input.device).reshape((1,1,subsize_,1,1))

            print(f"\nsubsize_ = {subsize_}, L = {L}, starts = {starts}")

            for start in starts:
                f = fn(input[:,:,start:start+subsize_,:,:], args['timestep'], **args['c'])
                total_out[:,:,start:start+subsize_,:,:] = total_out[:,:,start:start+subsize_,:,:] +    f * W
                scale_out[:,:,start:start+subsize_,:,:] = scale_out[:,:,start:start+subsize_,:,:] + ones * W

            return total_out / scale_out


        model.set_model_unet_function_wrapper(wrapper)
        return (model,)
    
CLAZZES = [WanModelLatentSlicer,]