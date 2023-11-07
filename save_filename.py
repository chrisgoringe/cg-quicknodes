from nodes import SaveImage

class SaveFilename(SaveImage):
    CATEGORY = "quicknodes"

    RETURN_TYPES = ("STRING",)
    RETURN_NAME = ("filename",)
    FUNCTION = "func"

    def func(self, **kwargs):
        ret = self.save_images(**kwargs)
        ret['result'] = ( ret['ui']['images'][0]['filename'], )
        return ret
        
CLAZZES = [SaveFilename]