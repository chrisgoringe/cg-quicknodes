import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

class Timer {
    static currentNodeId = null;
    static lastChangeTime = null;

    static start() {
        Timer.display("\n--- Run Started ---\n");
        const t = LiteGraph.getTime();;
        Timer.startTime = t;
        Timer.lastChangeTime = t;
        //Timer.currentNodeId = app.runningNodeId;
    }

    static end() {
        const totaltime = (Timer.lastChangeTime - Timer.startTime).toString().padStart(7);
        Timer.display("---  Run Ended  ---\n");
        Timer.display(`${totaltime} ms total\n\n`);
        Timer.lastChangeTime = null;
    }

    static display(string) {
        if (Timer.displayNode) {
            Timer.displayNode.widgets[1].value += string;
            Timer.displayNode.onResize?.(Timer.displayNode.size);
        }
        console.log(string);
    }

    static clear() {
        if (Timer.displayNode) {
            Timer.displayNode.widgets[1].value = "";
            Timer.displayNode.onResize?.(Timer.displayNode.size);
        }
    }

    static tick( {detail} ) {
        if (detail==Timer?.currentNodeId) return;
        console.log(`Entering ${detail}`);

        const t = LiteGraph.getTime();
        const dt = t - Timer.lastChangeTime;
        const time_ms_string = dt.toString().padStart(7);
        const node_string = (Timer.currentNodeId) ? `node #${Timer.currentNodeId}` : "startup";

        Timer.display(`${time_ms_string} ms in ${node_string}\n`);

        Timer.lastChangeTime = t;
        Timer.currentNodeId = detail;

        if (!Timer.currentNodeId) Timer.end();
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