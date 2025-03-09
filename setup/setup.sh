#!/bin/bash

if [[ "$(basename $(realpath ./))" == "custom_nodes" ]]; then
  nodedir=$(realpath ./)
elif [[ "$(basename $(realpath ../))" == "custom_nodes" ]]; then
  nodedir=$(realpath ../)
elif [[ "$(basename $(realpath ../../))" == "custom_nodes" ]]; then
  nodedir=$(realpath ../../)
else
  echo "run script in \$ComfyUI/custom_nodes/ComfyUI_KurtHokke-Nodes"
  exit
fi

custom_node_array=(
"ltdrdata/ComfyUI-Manager"
"crystian/ComfyUI-Crystools"
"cubiq/ComfyUI_essentials"
"kijai/ComfyUI-KJNodes"
"VykosX/ControlFlowUtils"
"pythongosssss/ComfyUI-Custom-Scripts"
"rgthree/rgthree-comfy"
"mcmonkeyprojects/sd-dynamic-thresholding"
)

for line in "${custom_node_array[@]}"; do
  if [[ ! -d "${nodedir}/$(basename $line)" ]]; then
    git clone "https://github.com/${line}.git" "${nodedir}/$(basename $line)" && \
    if [[ -f "${nodedir}/$(basename $line)/requirements.txt" ]]; then
      if command -v pip &>/dev/null; then
        pip install -r "${nodedir}/$(basename $line)/requirements.txt"
      else
        echo "pip not accessable"
      fi
    fi
  else
    echo "${nodedir}/$(basename $line) already exists, skipping."
  fi
done