import sys, os, importlib, re, os
sys.path.insert(0,os.path.dirname(os.path.realpath(__file__)))
from .common import module_root_directory

NODE_CLASS_MAPPINGS= {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def pretty(name:str):
    return " ".join(re.findall("[A-Z][a-z]*", name))

for module in [os.path.splitext(f)[0] for f in os.listdir(module_root_directory) if f.endswith('.py') and not f.startswith('_')]:
    imported_module = importlib.import_module(f"{module}")
    if 'CLAZZES' in imported_module.__dict__:
        for clazz in imported_module.CLAZZES:
            name = clazz.__name__
            NODE_CLASS_MAPPINGS[name] = clazz
            NODE_DISPLAY_NAME_MAPPINGS[name] = pretty(name)

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

#import shutil
#from .common import module_src_directory, module_js_directory, application_root_directory, application_web_extensions_directory
#shutil.copytree(module_js_directory, application_web_extensions_directory, dirs_exist_ok=True)
