import { app } from "../../../scripts/app.js";

app.registerExtension({
	name: "cg.quicknodes.expanding",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeType.comfyClass=="ExpandingMerge") {
            const onConnectionsChange = nodeType.prototype.onConnectionsChange;
            nodeType.prototype.onConnectionsChange = function (side,slot,connect,link_info,output) {     
                console.log(arguments)
                if (side==1) {
                    const last_slot = this.inputs.length - 1;
                    if (slot==last_slot && link_info && last_slot<20) {
                        this.addInput(`s${last_slot+1}`, "STRING")
                    }
                }  
            }
            return onConnectionsChange?.apply(this, arguments);
        }
    }
})