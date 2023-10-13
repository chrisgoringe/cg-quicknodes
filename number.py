import yaml, os
module_root_directory = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(module_root_directory,'config.yaml')

def read_config(item):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)[item]

class CommonSizes:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(s):
        return { "required":  { "size": (read_config('sizes'), {}) } }
    RETURN_TYPES = ("INT","INT")
    RETURN_NAMES = ("width","height")
    FUNCTION = "func"
    def func(self,size:str):
        x, y = [int(v) for v in size.split('x')]
        return (x,y)
    
CLAZZES = [CommonSizes]