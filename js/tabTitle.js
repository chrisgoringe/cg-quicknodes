import { app } from "../../../scripts/app.js";
import { api } from "../../../scripts/api.js";

function set_title(s) {
    if (document.visibilityState == 'visible') document.getElementsByTagName('title')[0].innerText = s;
}

function add_to_widget(w) {
    set_title(w.value)
    const _callback = w.callback
    w.callback = function(x) { 
        w.value = x
        _callback?.(x)
        set_title(x) 
    }    
}

app.registerExtension({
	name: "cg.quicknodes.tabtitle",

    async nodeCreated(node) {
        if (node.comfyClass=="TabTitle") {
            const messageHandler = function (event) {
                if (this.id == app.runningNodeId) set_title(event.detail.message);
            }.bind(node)
            api.addEventListener("cg.quicknodes.tabtitle", messageHandler);
            add_to_widget(node.widgets[0])
        }
    },

    async afterConfigureGraph() {
        app.graph._nodes.forEach((node) => {
            if (node.comfyClass=="TabTitle") set_title(node.widgets[0].value)
        });
    }
})