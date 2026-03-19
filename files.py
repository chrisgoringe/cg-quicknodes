from comfy_api.latest import io
from pathlib import Path

class RenameFile(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id        = "RenameFile",
            display_name   = "Rename File",
            category       = "quicknodes/io",
            inputs         = [ 
                io.String.Input("filepath"),
                io.String.Input("newfilepath")
            ],
            outputs        = [ 
                io.String.Output("result", display_name = "result")
            ],
            is_output_node = True
        )
    
    @classmethod
    def execute(cls, filepath:str|Path, newfilepath:str|Path ): # type: ignore
        filepath = Path(filepath)
        newfilepath = Path(newfilepath)

        if not filepath.exists(): return io.NodeOutput(f"{filepath} not found")
        if newfilepath.exists(): return io.NodeOutput(f"{newfilepath} already exists: not moving {filepath} over it")
        if not newfilepath.parent.exists(): newfilepath.parent.mkdir(parents=True, exist_ok=True)

        try: filepath.rename(newfilepath)
            
        except Exception as e:
            return io.NodeOutput(f"{e} when trying to rename {filepath} to {newfilepath}")
        
        return io.NodeOutput(f"Renamed {filepath} to {newfilepath}")
    
CLAZZES = [ RenameFile ]