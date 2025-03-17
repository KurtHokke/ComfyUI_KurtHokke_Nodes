import { app } from "/scripts/app.js";
import { ComfyWidgets } from "/scripts/widgets.js";

app.registerExtension({
    name: "KurtHokke2.Nodes",

    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === 'DebugAny2') {

            // Runs when the node is created, adds a text widget to the custom node

            const onNodeCreated = nodeType.prototype.onNodeCreated;

            nodeType.prototype.onNodeCreated = function () {
                // This is the node
                const node = onNodeCreated ? onNodeCreated.apply(this, arguments) : undefined;

                // Counts the nodes to ensure the node isn't duplicated
                const nodeFilter = app.graph._nodes.filter((item) => item.type == nodeData.name)

                // Sets the node name
                const nodeName = `${nodeData.name}_${nodeFilter.length}`;

                // Adds a textbox input
                const widget = ComfyWidgets.STRING(
                  this,
                  nodeName,
                  [
                    "STRING",
                    {
                      default: "",
                      placeholder: "Text will be shown here",
                      multiline: true,
                    },
                  ],
                  app
                );

                // Sets the textbox to read only
                widget.widget.inputEl.readOnly = true;

                return node;
            }


            // Runs when the queue is executed, binds the setText function when run

            const onExecuted = nodeType.prototype.onExecuted;

            nodeType.prototype.onExecuted = function (text) {
                onExecuted?.apply(this, arguments);

                // Runs the text transforms
                setText.call(this, text?.string);
            }


            // Runs when the node is loaded, binds the setText function when run

            const onConfigure = nodeType.prototype.onConfigure;

            nodeType.prototype.onConfigure = function (node) {
                onConfigure?.apply(this, arguments);

                // Runs the text transforms
                if (node?.widgets_values?.length) {
                    setText.call(this, node.widgets_values);
                }
            }


            // Takes the text array and sets the widget value

            const setText = function (textArray) {
                if (textArray.length) {
                    let text = '';

                    if (Array.isArray(textArray)) {
                        text = textArray.filter((word) => typeof word === 'string' && word.trim() !== "")
                                        .map((word) => word.trim())
                                        .join(" ");
                    }

                    const widget = this?.widgets.findIndex((item) => item.type == "customtext");

                    if (widget !== -1) { // Ensure widget exists before trying to assign a value
                        this.widgets[widget].value = text;
                    }

                    // this.widgets[(widget)].value = text;

                    app.graph.setDirtyCanvas(true);
                  }
            }
        }
    }
});