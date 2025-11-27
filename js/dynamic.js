import { app } from "../../../scripts/app.js";

function rationalise(node) {
    const guide = node.widgets[0].value
    const constraint = node.widgets[1].value
    var w = node.widgets[2].value
    var h = node.widgets[3].value
    var ar = node.widgets[4].value

    if (w!=node.last_w && h==node.last_h) {
        h = guide*guide/w
    } else if (w==node.last_w && h!=node.last_h) {
        w = guide*guide/h
    } else {
        h = Math.sqrt( (guide*guide)/ar )
        w = Math.sqrt( (guide*guide)*ar )
    } 
    
    w  = Math.round( w/constraint ) * constraint
    h  = Math.round( h/constraint ) * constraint
    ar = w/h

    if (w!=node.widgets[2].value)  node.widgets[2].value = w
    if (h!=node.widgets[3].value)  node.widgets[3].value = h
    if (ar!=node.widgets[4].value) node.widgets[4].value = ar

    node.last_w = w
    node.last_h = h
    node.last_ar = ar
}

app.registerExtension({
	name: "cg.quicknodes.dynamic",
    async nodeCreated(node) {
        if (node.comfyClass=='DynamicSizePicker') {
            setInterval(rationalise, 1000, node)
        }
    }
})