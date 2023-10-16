import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";
import { ComfyWidgets } from "../../../scripts/widgets.js";

class Timer {
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
    }

    static display(string) {
        if (Timer.onInfoAdded) Timer.onInfoAdded(string);
        console.log(string);
    }

    static _format(number, dp=2, pad=8) { return `${(number/1000).toFixed(dp).padStart(pad)} s` }

    static tick( {detail} ) {
        if (detail==Timer?.currentNodeId) return;
        console.log(`Entering ${detail}`);

        const t = LiteGraph.getTime();
        const time_string = Timer._format(t - Timer.lastChangeTime);
        const node_string = (Timer.currentNodeId) ? `node #${Timer.currentNodeId.toString().padStart(4)}` : "   startup";

        Timer.display(`${time_string} in ${node_string}\n`);

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
                this.addWidget("button", "Clear", "", function() {
                    w.value = "";
                    this.onResize?.(this.size);
                }, { serialize: false },);
                const w = ComfyWidgets["STRING"](this, "display_text_widget", ["STRING", { multiline: true }], app).widget;
                w.inputEl.readOnly = true;
                w.inputEl.style.opacity = 0.6;
                w.inputEl.style.fontSize = "9pt";
                w.value = "";

                Timer.onInfoAdded = function(string) {
                    w.value += string;
                    this.onResize?.(this.size);
                }
            }
        }
    },

})