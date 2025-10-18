from comfy_api.v0_0_2 import io

class SimpleInt(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id         = "SimpleInt",
            display_name    = "Int",
            category        = "quicknodes/simples",
            description     = "A simple integer",
            inputs          = [ io.Int.Input("integer_in", display_name="int"), ],
            outputs         = [ io.Int.Output("integer_out", display_name="int"), ],
        )

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput: 
        return io.NodeOutput(kwargs['integer_in'],)
    
class SimpleFloat(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id         = "SimpleFloat",
            display_name    = "Int",
            category        = "quicknodes/simples",
            description     = "A simple integer",
            inputs          = [ io.Float.Input("float_in", display_name="float"), ],
            outputs         = [ io.Float.Output("float_out", display_name="float"), ],
        )

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput: 
        return io.NodeOutput(kwargs['float_in'],)
    
class SimpleString(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id         = "SimpleString",
            display_name    = "Int",
            category        = "quicknodes/simples",
            description     = "A simple integer",
            inputs          = [ io.String.Input("string_in", display_name="string"), ],
            outputs         = [ io.String.Output("string_out", display_name="string"), ],
        )

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput: 
        return io.NodeOutput(kwargs['string_in'],)
    
    
class SimpleMultilineString(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id         = "SimpleMultilineString",
            display_name    = "Int",
            category        = "quicknodes/simples",
            description     = "A simple integer",
            inputs          = [ io.String.Input("string_in", display_name="string", multiline=True), ],
            outputs         = [ io.String.Output("string_out", display_name="string"), ],
        )

    @classmethod
    def execute(cls, **kwargs) -> io.NodeOutput: 
        return io.NodeOutput(kwargs['string_in'],)

CLAZZES = [SimpleInt,SimpleFloat,SimpleMultilineString, SimpleString]