import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

function set_title(s) {
    if (document.visibilityState == 'visible') document.getElementsByTagName('title')[0].innerText = s;
}

app.registerExtension({
	name: "cg.quicknodes.tabtitle",

    async nodeCreated(node) {
        if (node.comfyClass=="TabTitle") {
            const messageHandler = function (event) {
                if (this.id == app.runningNodeId) set_title(event.detail.message);
            }.bind(node)
            api.addEventListener("cg.quicknodes.tabtitle", messageHandler);
        }
    }
})