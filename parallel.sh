#!/bin/bash

# Set up environment
export EFT2OBS_BASE=$1
cd $EFT2OBS_BASE

#Input to run.py
process=$2
job_number=$3
n_events=$4
disable_rwgt=$5
classification_only=$6
save_mg5_run_dir=$7
save_hepmc=$8

# Run
python run_parallel.py --process $process --runLabel run_${job_number} --nEvents $n_events --disableReweight $disable_rwgt --classificationOnly $classification_only --saveMG5RunDir $save_mg5_run_dir --saveHepMC $save_hepmc

