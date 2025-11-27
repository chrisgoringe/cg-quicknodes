from comfy_api.latest import io

class ModelClipList(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id="ModelClipList",
            category="quicknodes/lists",
            description="create lists of the model and clip inputs.",
            inputs=[
                io.Model.Input("model1"),
                io.Clip.Input("clip1"),
                io.Model.Input("model2", optional=True),
                io.Clip.Input("clip2", optional=True),
                io.Model.Input("model3", optional=True),
                io.Clip.Input("clip3", optional=True),
                io.Model.Input("model4", optional=True),
                io.Clip.Input("clip4", optional=True),
            ],
            outputs=[
                io.Model.Output("models", display_name="model_list", is_output_list=True),
                io.Clip.Output("clips", display_name="clip_list", is_output_list=True)
            ],
        )

    @classmethod
    def execute(cls, **kwargs)-> io.NodeOutput:
        models = [ m for x in [1,2,3,4] if (m:=kwargs.get(f"model{x}",None) is not None)]
        clips  = [ c for x in [1,2,3,4] if (c:=kwargs.get(f"clip{x}",None) is not None)]

        return io.NodeOutput(models, clips)
    
CLAZZES = [ ModelClipList ]