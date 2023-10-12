import yaml, os
import folder_paths

application_root_directory = os.path.dirname(folder_paths.__file__)
application_web_extensions_directory = os.path.join(application_root_directory, "web", "extensions")

module_root_directory = os.path.dirname(os.path.realpath(__file__))
config_file = os.path.join(module_root_directory,'config.yaml')
module_js_directory = os.path.join(module_root_directory, "js")

def read_config(item):
    with open(config_file, 'r') as file:
        return yaml.safe_load(file)[item]