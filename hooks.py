
class _DetailerHook:
    cur_step = 0
    total_step = 0

    def __init__(self):
        pass

    def set_steps(self, info):
        self.cur_step, self.total_step = info

    def post_decode(self, pixels):
        return pixels

    def post_upscale(self, pixels):
        return pixels

    def post_encode(self, samples):
        return samples

    def pre_decode(self, samples):
        return samples

    def pre_ksample(self, model, seed, steps, cfg, sampler_name, scheduler, positive, negative, upscaled_latent,
                    denoise):
        return model, seed, steps, cfg, sampler_name, scheduler, positive, negative, upscaled_latent, denoise

    def post_crop_region(self, w, h, item_bbox, crop_region):
        return crop_region

    def touch_scaled_size(self, w, h):
        return w, h
    
    def cycle_latent(self, latent):
        return latent

    def post_detection(self, segs):
        return segs

    def post_paste(self, image):
        return image

    def get_custom_noise(self, seed, noise, is_touched):
        return noise, is_touched
    
class _Shrink(_DetailerHook):
    def __init__(self, delta):
        self.delta = delta//2

    def post_crop_region(self, w, h, item_bbox, crop_region):
        x1, y1, x2, y2 = crop_region
        if x1-self.delta < x2+self.delta and x1-self.delta > 0 and x2+self.delta < w:
            x1 -= self.delta
            x2 += self.delta
        if y1-self.delta < y2+self.delta and y1-self.delta > 0 and y2+self.delta < h:
            y1 -= self.delta
            y2 += self.delta
        
        return [x1, y1, x2, y2]    

class Shrink:
    CATEGORY = "quicknodes/hooks"
    @classmethod    
    def INPUT_TYPES(s): return { "required":  { 
        "size_delta" : ("INT", {"default":-8, "min":-256, "max":256, "tooltip":"change in dimension of box each cycle"}),
    } }
    RETURN_TYPES = ("DETAILER_HOOK",)

    FUNCTION = "func"
    def func(self, size_delta): 
        return (_Shrink(size_delta),)


CLAZZES = [Shrink]