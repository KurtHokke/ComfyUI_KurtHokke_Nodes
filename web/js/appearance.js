import { app } from "../../../scripts/app.js";
//Stole this from https://github.com/kijai/ComfyUI-KJNodes
//Thank you though!
app.registerExtension({
    name: "KurtHokke-Nodes.appearance",
        nodeCreated(node) {
            switch (node.comfyClass) {
                case "AIO_Tuner_Pipe":
                    node.shape = "box";
                    node.color = "#386692";
                    node.bgcolor = "#3053BC";
                    break;
                case "Node_BOOL":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_BOOL":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_BOOL":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_BOOL":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_BOOL":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_BOOL":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_BOOL":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_INT":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_Float":
                    node.setSize([200, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_String":
                    node.setSize([225, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "Node_StringMultiline":
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "SedOnString":
                    node.setSize([225, 58]);
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "UnetClipLoraLoader":
                    node.color = "#3f2b75";
                    node.bgcolor = "#6233b8";
                    break;
                case "UnetClipLoraLoaderBasic":
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
                case "CkptPipe":
                    node.setSize([285, 68]);
                    node.color = "#583585";
                    node.bgcolor = "#4d2c78";
                    break;
                case "ModelPipe1":
                    node.setSize([140, 62]);
                    node.color = "#174091";
                    node.bgcolor = "#003194";
                    break;
                case "ModelPipe2":
                    node.setSize([140, 62]);
                    node.color = "#174091";
                    node.bgcolor = "#003194";
                    break;
            }
        }
});