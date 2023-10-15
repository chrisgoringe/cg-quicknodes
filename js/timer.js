import { app } from "../../../scripts/app.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

class Timer {
    static currentNodeId = null;
    static lastChangeTime = null;
    static start() {
        Timer.display("\n--- Run Started ---\n");
        const d = new Date();
        const t = d.getTime();
        Timer.startTime = t;
        Timer.lastChangeTime = t;
        Timer.currentNodeId = app.runningNodeId;
    }

    static display(string) {
        if (Timer.displayNode) {
            Timer.displayNode.widgets[1].value += string;
            Timer.displayNode.onResize?.(Timer.displayNode.size);
        }
    }

    static clear() {
        if (Timer.displayNode) {
            Timer.displayNode.widgets[1].value = "";
            Timer.displayNode.onResize?.(Timer.displayNode.size);
        }
    }

    static tick() {
        if (app.runningNodeId==Timer?.currentNodeId) return;

        const d = new Date();
        const t = d.getTime();
        const nd = Timer.currentNodeId ? Timer.currentNodeId : 0;

        if (!Timer.lastChangeTime) {
            Timer.display("X")
            Timer.lastChangeTime = t;
            Timer.currentNodeId = app.runningNodeId;
            return;
        }

        const dt = t - Timer.lastChangeTime;
        const time = dt.toString().padStart(6);
        const node = (nd>0) ? `node #${nd}` : "startup" ;
        Timer.display(`${time} ms in ${node}\n`);

        Timer.lastChangeTime = t;
        Timer.currentNodeId = app.runningNodeId;

        if (!Timer.currentNodeId) {
            Timer.lastChangeTime = null;
            const total = t - Timer.startTime;
            const totaltime = dt.toString().padStart(6);
            Timer.display("---  Run Ended  ---\n");
            Timer.display(`${totaltime} ms total\n\n`);
        }
    }
}

app.registerExtension({
	name: "cg.quicknodes.timer",
    setup() {
        const draw = LGraphCanvas.prototype.draw;
        LGraphCanvas.prototype.draw = function() {
            Timer.tick();
            draw.apply(this,arguments);
        }
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
                this.addWidget("button", "Clear", "", Timer.clear);
                const w = ComfyWidgets["STRING"](this, "display_text_widget", ["STRING", { multiline: true }], app).widget;
                w.inputEl.readOnly = true;
                w.inputEl.style.opacity = 0.6;
                w.inputEl.style.fontSize = "9pt";
                w.value = "";
                Timer.displayNode = this;
            }
        }
    },

})