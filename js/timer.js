import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
//import { ComfyWidgets } from "../../../scripts/widgets.js";
import { $el } from "../../../scripts/ui.js";

const MARGIN = 2;

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

class Timer {
    static all_times = []
    static clear() { Timer.all_times = []; Timer.runs_since_clear = 0}
    static start() {
        Timer.display("\n--- Run Started ---\n");
        const t = LiteGraph.getTime();;
        Timer.startTime = t;
        Timer.lastChangeTime = t;
    }

    static end() {
        const time_string = Timer._format((Timer.lastChangeTime - Timer.startTime));
        Timer.display("---  Run Ended  ---\n");
        Timer.display(`${time_string} total\n\n`);
        console.log(Timer.html());
    }

    static display(string) {
        if (Timer.onInfoAdded) Timer.onInfoAdded(string);
        console.log(string);
    }

    static _name(node_id) { return (node_id) ? `${node_id.toString().padStart(4)}` : "startup"; }
    static _format(number, dp=2, pad=8) { return `${(number/1000).toFixed(dp).padStart(pad)} s` }

    static tick( {detail} ) {
        if (detail==Timer?.currentNodeId) return;
        console.log(`Entering ${detail}`);

        const t = LiteGraph.getTime();
        const dt = t - Timer.lastChangeTime;
        const time_string = Timer._format(dt);
        const node_string = Timer._name(Timer.currentNodeId);

        Timer.display(`${time_string} in ${node_string}\n`);

        var this_node_data = Timer.all_times.find((node_data)=>node_data[0]==Timer.currentNodeId);
        if (!this_node_data) {
            this_node_data = [Timer.currentNodeId,0,0,0,0];
            Timer.all_times.push(this_node_data);
        }
        this_node_data[1] += 1;
        if (!Timer.runs_since_clear || this_node_data[1] > Timer.runs_since_clear) Timer.runs_since_clear = this_node_data[1]
        this_node_data[2] += dt;
        this_node_data[3] = this_node_data[2] / this_node_data[1];
        this_node_data[4] = this_node_data[2] / Timer.runs_since_clear;

        Timer.lastChangeTime = t;
        Timer.currentNodeId = detail;

        if (!Timer.currentNodeId) Timer.end();
    }

    static html() {
        const table = $el("table",{
                "textAlign":"right",
                "border":"1px solid",
            },[
            $el("tr",[
                $el("th", {"textContent":"Node"}),
                $el("th", {"textContent":"Runs"}),
                $el("th", {"textContent":"Per run"}),
                $el("th", {"textContent":"Per flow"}),
            ])
        ]);
        Timer.all_times.sort((a,b)=>{ return b[4]-a[4]; })
        Timer.all_times.forEach((node_data) => {
            table.append($el("tr",[
                $el("td", {style:{"textAlign":"right"},"textContent":Timer._name(node_data[0])}),
                $el("td", {style:{"textAlign":"right"},"textContent":node_data[1].toString().padStart(4)}),
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

                const widget = {
                    type: "HTML",
                    name: "flying",
                    draw(ctx, node, widget_width, y, widget_height) { 
                        Object.assign(this.inputEl.style, get_position_style(ctx, widget_width, y, node.size[1]));
                    },
                    computeSize() {
                        return [this.inputEl.scrollWidth, this.inputEl.scrollHeight];
                    }
                };
                widget.inputEl = $el("span",[$el("span"),]);
                document.body.appendChild(widget.inputEl);

                this.addCustomWidget(widget);
                this.onRemoved = function () { widget.inputEl.remove(); };
                this.serialize_widgets = false;

                Timer.onInfoAdded = function(string) {
                    widget.inputEl.replaceChild(Timer.html(), widget.inputEl.firstChild);
                    this.onResize?.(this.size);
                }
            }
        }
    },

})