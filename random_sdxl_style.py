import random, os

module_root_directory = os.path.dirname(os.path.realpath(__file__))
module_resource_directory = os.path.join(module_root_directory,'resources')

CLAZZES = []

class SeedContext():
    """
    Context Manager to allow one or more random numbers to be generated, optionally using a specified seed, 
    without changing the random number sequence for other code.
    """
    def __init__(self, seed=None):
        self.seed = seed
    def __enter__(self):
        self.state = random.getstate()
        if self.seed:
            random.seed(self.seed)
    def __exit__(self, exc_type, exc_val, exc_tb):
        random.setstate(self.state)

try:
    from custom_nodes.sdxl_prompt_styler.sdxl_prompt_styler import SDXLPromptStyler, read_json_file
    class RandomSdxlStyle(SDXLPromptStyler):
        resource_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),'resources')
        @classmethod
        def INPUT_TYPES(cls):
            it = SDXLPromptStyler.INPUT_TYPES()
            it['optional'] = { "seed":("INT", {"default":0,"min": 0,"max":0xffffffffffffffff})}
            it['required'].pop('style')
            it['required']['json_file'] = (list((f for f in os.listdir(module_resource_directory) if f.endswith("styles.json"))),{})

            return it
        CATEGORY = 'quicknodes'
        FUNCTION = 'func'
        RETURN_TYPES = ('STRING','STRING','STRING','INT',)
        RETURN_NAMES = ('positive','negative','style_name','seed',)
        def func(self, text_positive, text_negative, log_prompt, json_file, seed=None):
            file_path = os.path.join(module_resource_directory, json_file)
            self.json_data = read_json_file(file_path)
  
            with SeedContext(seed):
                style = random.choice(self.json_data)
                stylename = style['name']

            return self.prompt_styler(text_positive, text_negative, stylename, log_prompt)+(stylename,seed,)
        
    CLAZZES.append(RandomSdxlStyle)

except:
    print("Random SDXL Prompt requires sdxl_prompt_styler")

