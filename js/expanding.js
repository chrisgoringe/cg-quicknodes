import { app } from "../../../scripts/app.js";

app.registerExtension({
	name: "cg.quicknodes.expanding",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass=="ExpandingMerge") {
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function (side,slot,connect,link_info,output) {     
                if (side==1) {
                    const x = len(this.inputs) - 1
                    this.addInput(`s${x}`, "STRING")
                }   
            }
            return onConnectionsChange?.apply(this, arguments);
        }
    }
})