import os
import folder_paths

application_root_directory = os.path.dirname(folder_paths.__file__)
application_web_extensions_directory = os.path.join(application_root_directory, "web", "extensions", "cg_quicknodes")

module_root_directory = os.path.dirname(os.path.realpath(__file__))

module_js_directory = os.path.join(module_root_directory, "js")

