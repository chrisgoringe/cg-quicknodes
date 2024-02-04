import torch

class UniqueImages:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "images": ("IMAGE",), } }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("Unique images",)
    FUNCTION = "func"

    def func(self, images:torch.Tensor):
        B = images.shape[0]
        duplicates = set()
        for i in range(B):
            for j in range(i+1,B):
                if (images[i]==images[j]).all():
                    duplicates.add(j)
        if not duplicates: return (images,)
        print(f"Removing {duplicates}")
        return (torch.stack( tuple(images[i] for i in range(B) if i not in duplicates) ), )

CLAZZES = [UniqueImages]