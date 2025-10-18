class SplitSigmasAtSigmaValue:
    FUNCTION = "func"
    CATEGORY = "quicknodes/sigmas"
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "sigmas": ("SIGMAS", ),
                "split_at": ("FLOAT", {"default":0.875, "min":0.005, "max":0.995, "step":0.005}),
            }
        }
    RETURN_TYPES = ("SIGMAS","SIGMAS","INT")
    RETURN_NAMES = ("high_sigmas", "low_sigmas", "split_index")
    
    def func(self, sigmas:list[float], split_at:float):
        err = [ abs(s-split_at) for s in sigmas ]
        idx = err.index(min(err))
        return ( sigmas[:idx+1], sigmas[idx:], idx )
    
#CLAZZES = [SplitSigmasAtSigmaValue,]