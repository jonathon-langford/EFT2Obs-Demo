#!/bin/bash

# Delete all.txt if already exists
if test -f "latex/all.txt"; then
  rm latex/all.txt
  echo "Deleting current latex file"
fi

# Run python script to generate individual tables
for stage in {0,1,1_1}; do python extract_SF.py --stage $stage --processes ggh,vbf,wh,zh,tth --freezeOtherParameters 1 --latexOutput 1; done


# Concatenate scripts
for tab in {Ai_stage0_ggh_vbf_wh_zh_tth,Bij_stage0_ggh_vbf_wh_zh_tth,Ai_stage1_ggh_vbf,Ai_stage1_wh_zh_tth,Bij_stage1_ggh,Bij_stage1_vbf,Bij_stage1_wh_zh_tth,Ai_stage1_1_ggh,Ai_stage1_1_vbf,Ai_stage1_1_wh_zh_tth,Bij_stage1_1_ggh,Bij_stage1_1_vbfset1,Bij_stage1_1_vbfset2,Bij_stage1_1_wh,Bij_stage1_1_zh_tth};
  do cat latex/tab_${tab}.txt >> latex/all.txt;
done

echo "Final: latex/all.txt"

# Remove individual tables
rm latex/tab_*

# Copy tables to clipboard
xclip -sel cli < latex/all.txt
