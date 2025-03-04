import { app } from "../../../scripts/app.js";

//Stole this from https://github.com/kijai/ComfyUI-KJNodes
//Thank you though!

app.registerExtension({
    name: "KurtHokke-Nodes.appearance",
        nodeCreated(node) {
            switch (node.comfyClass) {
                case "UnetClipLoraLoader":
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "SamplerSel":
                    node.setSize([250, 58]);
                    node.color = "#a31d4c";
                    node.bgcolor = "#d42c72";
                    break;
                case "SchedulerSel":
                    node.setSize([250, 58]);
                    node.color = "#076b3e";
                    node.bgcolor = "#29ab56";
                    break;
                case "EmptyLatentSize":
                    node.setSize([160, 117]);
                    break;
                case "EmptyLatentSize64":
                    node.setSize([160, 117]);
                    break;
            }
        }
});