import { app } from "../../../scripts/app.js";
import { $el } from "../../../scripts/ui.js";

const MARGIN = 4;

function get_position_style(ctx, widget_width, y, node_height) {
    const elRect = ctx.canvas.getBoundingClientRect();
    const transform = new DOMMatrix()
        .scaleSelf(elRect.width / ctx.canvas.width, elRect.height / ctx.canvas.height)
        .multiplySelf(ctx.getTransform())
        .translateSelf(MARGIN, MARGIN + y);

    return {
        transformOrigin: '0 0',
        transform: transform,
        left: `0px`, 
        top: `0px`,
        position: "absolute",
        maxWidth: `${widget_width - MARGIN*2}px`,
        maxHeight: `${node_height - MARGIN*2}px`,
        width: `auto`,
        height: `auto`,
    }
}

app.registerExtension({
	name: "cg.quicknodes.html",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass=="HtmlNode") {

            const orig_nodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                orig_nodeCreated?.apply(this, arguments);

                const widget = {
                    type: "HTML",
                    name: "flying",
                    draw(ctx, node, widget_width, y, widget_height) { 
                        Object.assign(this.inputEl.style, get_position_style(ctx, widget_width, y, node.size[1]));
                    },
                };
                widget.inputEl = $el("img", { src: "http://127.0.0.1:8188/view?filename=misc-stained+glass_00001_.png&subfolder=2023-10-16&type=output" });
                document.body.appendChild(widget.inputEl);

                this.addCustomWidget(widget);
                this.onRemoved = function () { widget.inputEl.remove(); };
                this.serialize_widgets = false;

            }
        }
    },

})

