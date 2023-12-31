import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
//import { ComfyWidgets } from "../../../scripts/widgets.js";
import { $el } from "../../../scripts/ui.js";

const MARGIN = 8;

function get_position_style(ctx, scroll_width, widget_width, y, node_width, node_height) {
    const elRect = ctx.canvas.getBoundingClientRect();
    const transform = new DOMMatrix()
        .scaleSelf(elRect.width / ctx.canvas.width, elRect.height / ctx.canvas.height)
        .multiplySelf(ctx.getTransform())
        .translateSelf(MARGIN, MARGIN + y);

    const x = Math.max(0, Math.round(ctx.getTransform().a*(node_width - scroll_width - 2*MARGIN)/2));
    return {
        transformOrigin: '0 0',
        transform: transform,
        left: `${x}px`, 
        top: `0px`,
        position: "absolute",
        maxWidth: `${widget_width - MARGIN*2}px`,
        maxHeight: `${node_height - MARGIN*2 - y}px`,
        width: `auto`,
        height: `auto`,
        overflow: `auto`,
    }
}

class Timer {
    static all_times = []
    static clear() { 
        Timer.all_times = []; 
        Timer.runs_since_clear = 0; 
        if (Timer.onChange) Timer.onChange();
    }

    static start() {
        const t = LiteGraph.getTime();;
        Timer.startTime = t;
        Timer.lastChangeTime = t;
    }

    static _format(number, dp=2) { return `${(number/1000).toFixed(dp)} s` }

    static add_timing(id, dt) {
        var this_node_data = Timer.all_times.find((node_data)=>node_data[0]==id);
        if (!this_node_data) {
            this_node_data = [id,0,0,0,0];
            Timer.all_times.push(this_node_data);
        }
        this_node_data[1] += 1;
        if (!Timer.runs_since_clear || this_node_data[1] > Timer.runs_since_clear) Timer.runs_since_clear = this_node_data[1]
        this_node_data[2] += dt;
        this_node_data[3] = this_node_data[2] / this_node_data[1];
    }

    static tick( {detail} ) {
        if (detail==Timer?.currentNodeId) return;
        //console.log(`Entering ${detail}`);

        const t = LiteGraph.getTime();

        Timer.add_timing(Timer.currentNodeId ? Timer.currentNodeId : "startup", t - Timer.lastChangeTime)

        Timer.lastChangeTime = t;
        Timer.currentNodeId = detail;

        if (!Timer.currentNodeId) Timer.add_timing("total", t - Timer.startTime)

        if (Timer.onChange) Timer.onChange();
    }

    static html() {
        const table = $el("table",{
                "textAlign":"right",
                "border":"1px solid",
                //"overflow": "auto",
            },[
            $el("tr",[
                $el("th", {"textContent":"Node"}),
                $el("th", {"textContent":"Runs"}),
                $el("th", {"textContent":"Per\u00A0run"}),
                $el("th", {"textContent":"Per\u00A0flow"}),
            ])
        ]);
        Timer.all_times.forEach((node_data) => {node_data[4] = node_data[2] / Timer.runs_since_clear})
        Timer.all_times.sort((a,b)=>{ return b[4]-a[4]; })
        Timer.all_times.forEach((node_data) => {
            table.append($el("tr",[
                $el("td", {style:{"textAlign":"right"},"textContent":node_data[0]}),
                $el("td", {style:{"textAlign":"right"},"textContent":node_data[1].toString()}),
                $el("td", {style:{"textAlign":"right"},"textContent":Timer._format(node_data[3])}),
                $el("td", {style:{"textAlign":"right"},"textContent":Timer._format(node_data[4])}),
            ]))
        });
        return table;
    }
}

app.registerExtension({
	name: "cg.quicknodes.timer",
    setup() {
        api.addEventListener("executing", Timer.tick);
    },
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass=="Timer") {
            const orig_executionStart = nodeType.prototype.onExecutionStart;
            nodeType.prototype.onExecutionStart = function () {
                orig_executionStart?.apply(this, arguments);
                Timer.start();
            }

            const orig_nodeCreated = nodeType.prototype.onNodeCreated;
            nodeType.prototype.onNodeCreated = function () {
                orig_nodeCreated?.apply(this, arguments);

                this.addWidget("button", "clear", "", Timer.clear);

                const widget = {
                    type: "HTML",
                    name: "flying",
                    draw(ctx, node, widget_width, y, widget_height) { 
                        Object.assign(this.inputEl.style, get_position_style(ctx, this.inputEl.scrollWidth, widget_width, y, node.size[0], node.size[1]));
                    },
                };
                widget.inputEl = $el("div",[$el("span"),]);

                document.body.appendChild(widget.inputEl);

                this.addCustomWidget(widget);
                this.onRemoved = function () { widget.inputEl.remove(); };
                this.serialize_widgets = false;

                Timer.onChange = function() {
                    widget.inputEl.replaceChild(Timer.html(), widget.inputEl.firstChild);
                    //this.onResize?.(this.size);
                }
            }
        }
    },

})