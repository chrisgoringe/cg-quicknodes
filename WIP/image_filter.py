from PIL import ImageFilter, Image

class ImageFilter:
    CATEGORY = "image/filters"

    FILTERS = {
        "Blur"              : ImageFilter.BLUR,
        "Contour"           : ImageFilter.CONTOUR,
        "Detail"            : ImageFilter.DETAIL,
        "Edge Enhance"      : ImageFilter.EDGE_ENHANCE,
        "Edge Enhance More" : ImageFilter.EDGE_ENHANCE_MORE,
        "Emboss"            : ImageFilter.EMBOSS,
        "Find Edges"        : ImageFilter.FIND_EDGES,
        "Sharpen"           : ImageFilter.SHARPEN,
        "Smooth"            : ImageFilter.SMOOTH,
        "Smooth More"       : ImageFilter.SMOOTH_MORE,
    }

    @classmethod    
    def INPUT_TYPES(cls):
        return { "required":{
            "image" : ("IMAGE",{}),
            "function" : ([x for x in cls.FILTERS]),
        } }

    RETURN_TYPES = ( "IMAGE", )
    RETURN_NAMES = ( "image", )
    FUNCTION = "func"

    def func(self, image, function):
        outputs = []
        for i in image:
            im = Image.fromarray(np.clip(255. * i.cpu().numpy(), 0, 255).astype(np.uint8))
            im = im.filter(self.FILTERS[function])
            j = ImageOps.exif_transpose(im)
            im = j.convert("RGB")
            im = np.array(im).astype(np.float32) / 255.0
            im = torch.from_numpy(im)[None,]
            outputs.append(im)

        return ( torch.cat(outputs, dim=0), )
    
CLAZZES = [ImageFilter]