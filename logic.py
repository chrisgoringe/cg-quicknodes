from comfy_api.latest import io
from typing import Any
import torch
import random

DESC = '''Takes any input and returns a boolean. 
Tensors return torch.any( t!=0 ).
strings return False if empty or if they are "false", "no", "off", or "0" (case-insensitive).
All other inputs return their python truthiness.
'''

class Truthiness(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id      = "cg_Truthiness",
            display_name = "Truthiness",
            category     = "quicknodes/logic",
            inputs       = [ 
                io.AnyType.Input("anything"),
            ],
            outputs      = [
                io.Boolean.Output("truth"),
            ],
            description  = DESC,
        )
    
    @classmethod
    def execute(cls, anything:Any) -> io.NodeOutput: # type: ignore
        if anything is None: 
            return io.NodeOutput( False )

        if isinstance(anything,torch.Tensor):
            return io.NodeOutput( torch.any( anything!=0 ) )
        
        if isinstance(anything,str):
            if not anything.strip(): return io.NodeOutput( False )
            if anything.strip().lower() in ["false","no","off","0"]: return io.NodeOutput( False )
        
        return io.NodeOutput( bool(anything) )
    
class RandomBoolean(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id      = "cg_RandomBoolean",
            display_name = "Random Boolean",
            category     = "quicknodes/logic",
            inputs       = [ 
                io.Float.Input("p", default=0.5, tooltip="Probability of True"),
            ],
            outputs      = [
                io.Boolean.Output("boolean"),
            ],
        )
    
    @classmethod
    def execute(cls, p:float) -> io.NodeOutput: # type: ignore
        return io.NodeOutput( random.random()<p )

COMPARES = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<":  lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">":  lambda a, b: a > b,
    ">=": lambda a, b: a >= b
}

class Compare(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id      = "cg_Compare",
            display_name = "Compare",
            category     = "quicknodes/logic",
            inputs       = [ 
                io.AnyType.Input("a"),
                io.AnyType.Input("b"),
                io.Combo.Input("op", options=[k for k in COMPARES], default="==", tooltip="Comparison operator"),
            ],
            outputs      = [
                io.Boolean.Output("result"),
            ],
        )
    
    @classmethod
    def execute(cls, a:Any, b:Any, op:str) -> io.NodeOutput: # type: ignore
        return io.NodeOutput( COMPARES[op](a, b) )


CLAZZES = [Truthiness, RandomBoolean, Compare]