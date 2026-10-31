import time
from comfy.model_management import throw_exception_if_processing_interrupted
from comfy_api.latest import io
from typing import Any

template = io.MatchType.Template("waitforit")

class WaitForIt(io.ComfyNode):
    @classmethod
    def define_schema(cls):
        return io.Schema(
            node_id      = "cg.Wait For It",
            display_name = "Wait For It",
            description  = "Control execution sequence; pass the first input through only when the second is available",
            inputs       = [
                io.MatchType.Input("input", template=template, tooltip="passed directly to out"),
                io.Autogrow.Input("trigger", 
                    template=io.Autogrow.TemplatePrefix(
                        input=io.AnyType.Input("trigger"), prefix="trigger", min=1, max=9,
                    )
                ),
            ],
            outputs      = [
                io.MatchType.Output(template=template, display_name="output")
            ],
            category     = "quicknodes/wait",
        )

    @classmethod
    def execute(cls, input:Any, trigger:dict) -> io.NodeOutput: # type: ignore
        return io.NodeOutput(input, )

class WaitABit:
    CATEGORY = "quicknodes"
    @classmethod    
    def INPUT_TYPES(cls):
        return { "required":  { "seconds": ("INT", {"default":0}), "image": ("IMAGE",{}) }}
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "func"
    def func(self,seconds, image):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            throw_exception_if_processing_interrupted()
            time.sleep(1)
        return (image,)
    
CLAZZES = [WaitABit,WaitForIt,]