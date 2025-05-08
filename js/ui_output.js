import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";
import { ComfyWidgets } from "../../scripts/widgets.js";

function registerUiOutputListener(nodeType, nodeData, message_type, func) {
	if (nodeData?.ui_output?.includes(message_type) || nodeData?.description?.includes(message_type)) {
		const onExecuted = nodeType.prototype.onExecuted;
		nodeType.prototype.onExecuted = function (message) {
			onExecuted?.apply(this, arguments);
			if (message[message_type]) {
				var the_message = message[message_type];
				var node = undefined;
				if (typeof the_message[0] === 'string' && the_message[0].startsWith('id=')) {
					node = this.graph._nodes_by_id[the_message[0].slice(3)];
					the_message.splice(0,1);
				} else {
					node = this;
				}
				func.apply(node, [the_message]);
			}
		};
	}
};

export function display_message_function(message, node) {
	const text_widget_name = "display_text_widget$$"
	node = node ?? this
	var w = node.widgets?.find((w) => w.name === text_widget_name);
	if (w === undefined) {
		w = ComfyWidgets["STRING"](node, text_widget_name, ["STRING", { multiline: true }], app).widget;
		w.inputEl.readOnly = true;
		w.inputEl.style.opacity = 0.6;
		w.inputEl.style.fontSize = "12pt";
	}
	w.value = message;
	if (this.title?.includes("+")) {
		w.inputEl.style.fontSize = "300%"
	}
	node.onResize?.(node.size);
};

function terminate_function(message) { 
	if (message[0]==="terminate") { 
		document.getElementById("autoQueueCheckbox").checked = false;
		api.interrupt(); 
	} else if (message[0]==="autoqueueoff") {
		document.getElementById("autoQueueCheckbox").checked = false;
	}
};

function modify_self_function(message) {
	message.forEach(self_modify => {
		var w = this.widgets?.find((w) => w.name === self_modify[0])
		if (w) {
			w.value = self_modify[1];
			this.onResize?.(this.size);
		}
	});
};

function modify_other_function (message) {
	message.forEach(update => {
		var node_id = parseInt(update[0]);
		var widget_name = update[1];
		var text = update[2];
		var node = this.graph._nodes_by_id[node_id];
		var widget = node?.widgets.find((w) => w.name===widget_name);
		if (widget) { 
			widget.value = text; 
			node.onResize?.(node.size);
		} else { console.log("cg.custom.core.ModifyOther - Widget "+widget_name+" not found")}
	});
};

function title_color_function(message) {
	var col = message[0];
	if (col==='reset') {
		if (this.color_was_originally==='not-set') { col = undefined; } 
		else { col = this.color_was_originally; }
	} else {
		if (this.color_was_originally===undefined) {
			if (this.color) { this.color_was_originally = this.color; }
			else { this.color_was_originally = "not-set"; }
		}
	}
	this.color = col;
	this.onResize?.(this.size);
};

app.registerExtension({
	name: "cg.ui_output_actions",
	version: 4,
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
        registerUiOutputListener(nodeType, nodeData, 'terminate', terminate_function);
		registerUiOutputListener(nodeType, nodeData, 'display_text', display_message_function);
        registerUiOutputListener(nodeType, nodeData, 'modify_self', modify_self_function);
        registerUiOutputListener(nodeType, nodeData, 'modify_other', modify_other_function);
		registerUiOutputListener(nodeType, nodeData, 'set_title_color', title_color_function);
	},
});

