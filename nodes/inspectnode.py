from custom_nodes.ComfyUI_KurtHokke_Nodes.utils import CATEGORY, any, prefix
from custom_nodes.ControlFlowUtils.Helpers import replace_caseless, cint, cbool, safe_eval, filter_node_id, debug_print
import json
import re
import torch

class InspectNode:

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text":("STRING", {"default": '',"multiline": True,"defaultInput": False,"print_to_screen": True}),
                "output_type": (["ANY","STRING","INT","FLOAT","BOOLEAN","LIST","TUPLE","DICT","JSON","FORMULA"],{"tooltip":"The type the Passthrough or Text should be converted to"}),
            },
                "optional": {
                    "passthrough":(any, {"default": "","multiline": True,"forceInput": True,"tooltip": "Any value or data to be visualized and forwarded by this node"}),
                    "aux":(any, {"default": "","forceInput": True, "tooltip": "Any optional Auxiliary data to be processed by this node"}),"aux2":(any, {"default": "","forceInput": True, "tooltip": "Any optional Auxiliary data to be processed by this node"}),"aux3":(any, {"default": "","forceInput": True, "tooltip": "Any optional Auxiliary data to be processed by this node"}),"aux4":(any, {"default": "","forceInput": True, "tooltip": "Any optional Auxiliary data to be processed by this node"}),"aux5":(any, {"default": "","forceInput": True, "tooltip": "Any optional Auxiliary data to be processed by this node"}),
            },    "hidden": { "unique_id": "UNIQUE_ID" }
        }

    RETURN_TYPES = (any,)
    RETURN_NAMES = ("*",)
    FUNCTION = "inspect_node"
    OUTPUT_NODE = True
    CATEGORY = CATEGORY.MAIN.value + CATEGORY.UTILS.value

    PREVIOUS = ""

    def replace_vars(self,passthrough,aux_list):

        from custom_nodes.ControlFlowUtils.ControlFlowUtils import VYKOSX_STORAGE_DATA
        #global VYKOSX_STORAGE_DATA

        if passthrough is None: passthrough = ""

        ret,append_mem = "",False

        #try:

        #Passthrough Replacements:

        if isinstance(passthrough, torch.Tensor):

            ret = passthrough

        else:

            ret = str(passthrough)

            if "%prev%" in ret.casefold():
                #debug_print (">> %PREV% FOUND IN TEXT!")
                ret = replace_caseless(ret,"%prev%", str(repr( self.PREVIOUS)).replace("'",""))

            if "__MEM__STORAGE__CLEAR__" in ret:
                #debug_print ("MEM CLEAR REQUEST!")
                ret = ret.replace("__MEM__STORAGE__CLEAR__", "")
                VYKOSX_STORAGE_DATA = {}

            if "__MEM__STORAGE__GET__" in ret:
                ret = ret.replace("__MEM__STORAGE__GET__", str(repr( VYKOSX_STORAGE_DATA)).strip("'\""))

            if "__MEM__STORAGE__SET__" in ret:

                if aux_list is not None and type(aux_list[0]) is dict:
                    VYKOSX_STORAGE_DATA = aux_list[0]
                    ret = ret.replace("__MEM__STORAGE__SET__", "")

                else:
                    raise Exception("__MEM__STORAGE__SET__ requires a valid dictionary input in the first Aux_Input!")

            if "__MEM__STORAGE__KEYS__" in ret:

                ret = ret.replace("__MEM__STORAGE__KEYS__", ", ".join([k for k in VYKOSX_STORAGE_DATA]) )

        if aux_list is not None:

            for i,aux in enumerate(aux_list):

                if aux is not None:

                    aux = str(aux)#"" if aux is None else str(aux)

                    if aux.casefold() == "%clear%":

                        #debug_print (">> CLEAR SIGNAL RECEIVED!")

                        ret,self.PREVIOUS = "",""

                    else:

                        if "%prev%" in aux.casefold():
                            #debug_print (">> %PREV% FOUND IN AUX!")
                            aux = replace_caseless(aux,"%prev%", str(repr( self.PREVIOUS)).replace("'",""))

                        if "__MEM__STORAGE__CLEAR__" in aux:
                            #debug_print ("__MEM__STORAGE__CLEAR__ IN AUX")
                            ret = ret.replace("__MEM__STORAGE__CLEAR__", "")
                            VYKOSX_STORAGE_DATA = {}

                        if "__MEM__STORAGE__GET__" in aux:
                            #debug_print ("__MEM__STORAGE__GET__ IN AUX")
                            aux = aux.replace("__MEM__STORAGE__GET__", "")
                            ret+= str(repr( VYKOSX_STORAGE_DATA)).strip("'\"")

                        if "__MEM__STORAGE__SET__" in aux:

                            #debug_print ("__MEM__STORAGE__SET__ IN AUX")

                            if i!=0 and type(aux_list[0]) is dict:
                                VYKOSX_STORAGE_DATA = aux_list[0]
                                aux = aux.replace("__MEM__STORAGE__SET__", "")

                            else:
                                raise Exception("__MEM__STORAGE__SET__ requires a valid dictionary input in the first Aux_Input!")

                        if "__MEM__STORAGE__KEYS__" in aux:

                            #debug_print ("__MEM__STORAGE__KEYS__ IN AUX")

                            aux = aux.replace("__MEM__STORAGE__KEYS__", ", ".join([k for k in VYKOSX_STORAGE_DATA]) )

                        if (pos:= aux.find("=>__AUX__DISPLAY__PREFIX__")) > 0:
                            ret = aux[:pos]+ret

                        if (pos:= aux.find("__AUX__DISPLAY__SUFFIX__=>")) != -1:
                            ret+= aux[pos+26:] #26 = len("__AUX__DISPLAY__SUFFIX__=>")

                        if (aux_var := "%aux" + ( "" if i==0 else str(i+1) ) + "%") in ret.casefold():

                            #debug_print ("REPLACING '",aux_var,"' in '",ret,"' with '",aux,"'!",end="")

                            ret = replace_caseless(ret,aux_var,aux)

                            if "...," in ret: #Remove ellipsis from tensor representations as it causes issues with safe_eval
                                #Remove the ellipsis while preserving the alignment. The tensor repr is not valid for direct tensor manipulations but at least it won't error.
                                ret = re.sub(r'\],\s*\.\.\.\s*,(\s*\n\s*)\[', '],\\1[', ret)

        if "%" in ret:

            l_pos = ret.find("%")
            if l_pos!= -1:
                r_pos = ret.find("%",l_pos+1)
                if r_pos!=-1:
                    name = ret[l_pos+1:r_pos]
                    if name in VYKOSX_STORAGE_DATA:
                        ret = ret.replace("%"+name+"%", str(repr( VYKOSX_STORAGE_DATA[name])).replace("'",""))
                        if "...," in ret: #Remove ellipsis from tensor representations as it causes issues with safe_eval
                            #Remove the ellipsis while preserving the alignment. The tensor repr is not valid for direct tensor manipulations but at least it won't error.
                            ret = re.sub(r'\],\s*\.\.\.\s*,(\s*\n\s*)\[', '],\\1[', ret)

        #except Exception as x:
            #raise Exception("AN UNEXPECTED ERROR OCURRED WHILE REPLACING VARIABLES:",x)

        #debug_print (">> PROCESSED TEXT AFTER VARIABLE REPLACEMENT: '",ret,"'",end="")

        self.PREVIOUS = ret

        return ret

    def inspect_node(self,text="",output_type="ANY",passthrough=None,aux=None,aux2=None,aux3=None,aux4=None,aux5=None,unique_id=0):

        #TODO:
        #Add $var$ to resolve to the value of mape variables/KJNodes get/set/ and anything everywhere nodes

        aux_list = [aux,aux2,aux3,aux4,aux5]

        #debug_print("\n>> DATA MONITOR [",filter_node_id(unique_id),"]")
        #debug_print("TEXT: ", str(text))
        #debug_print("PASSTHROUGH: ", type(passthrough), repr(passthrough) )
        #debug_print("AUX INPUTS: ", str(aux_list))
        #debug_print("PREV:", self.PREVIOUS)
        #debug_print("OUTPUT TYPE: ", output_type)

        if (passthrough is not None):

            encapsulate = False

            try:
                iterator = iter(passthrough)
            except TypeError:
                encapsulate = True

                #debug_print ("[!] PASSTHROUGH NOT ITERABLE!")

            else:

                #debug_print ("[!] PASSTHROUGH ITERABLE!")

                try:
                    float(passthrough)
                except:
                    debug_print ("[!] PASSTHROUGH NOT NUMERIC!")

                else:

                    #debug_print ("[!] PASSTHROUGH NUMERIC!")

                    encapsulate = True

            ret = self.replace_vars(passthrough,aux_list)

            if ret == "":

                return {"ui": {"text": ret}, "result": (ret,)} #return {"ui": {"text": passthrough}, "result": (passthrough,)}

            else: text = ret

            #debug_print ( "TEXT:", text )

            match output_type:
                case "INT":
                    text = cint(text)
                case "FLOAT":
                    text = float(text)
                case "BOOLEAN":
                    text = cbool(text)
                    encapsulate=True
                case "STRING":
                    text = str(text)
                case "LIST":
                    text = list(text)
                case "TUPLE":
                    text = tuple(text)
                case "DICT":
                    text = dict(text)
                case "JSON":
                    text = json.loads(text),
                case "FORMULA":
                    if text != "":
                        text = safe_eval(str(text))
                    try:
                        float(text)
                    except ValueError:
                        debug_print ("PASSTHROUGH FORMULA NOT NUMERIC!")
                    else:
                        #debug_print ("PASSTHROUGH FORMULA NUMERIC!")
                        encapsulate = True
                case _:
                    text = passthrough

            #debug_print ("RETURN [PASSTHROUGH]:",type(text), repr(text))

            try:
                display_text = repr(text).strip("'\"") if type(text) is not str else text
            except:
                pass
                display_text = json.loads(text)

            if encapsulate:
                return {"ui": {"text": tuple([display_text]) },"result": tuple([text]) }
            else:
                return {"ui": {"text": display_text},"result": (text,)}

        else:

            text = self.replace_vars(text,aux_list)

            match output_type:
                case "INT":
                    text = cint(text)
                case "FLOAT":
                    text = float(text)
                case "BOOLEAN":
                    text = cbool(text)
                case "STRING":
                    text = str(text)
                case "LIST":
                    text = list(text)
                case "TUPLE":
                    text = tuple(text)
                case "JSON":
                    text = json.loads(text),
                case "FORMULA":
                    if text != "":
                        text = safe_eval(str(text))

            #debug_print ("RETURN [TEXT]:",text)

            return (text),    #return {"ui": {"text": str(text)},"result": (text,)}

    @classmethod
    def IS_CHANGED(s,**kwargs):
        return float("nan")