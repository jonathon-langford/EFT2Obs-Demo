#!/bin/bash

# Set up environment
export EFT2OBS_BASE=$1
cd $EFT2OBS_BASE

#Input to run.py
process=$2
job_number=$3
n_events=$4
classification_only=$5
save_mg5_run_dir=$6
save_hepmc=$7

# Run
python run_parallel.py --process $process --runLabel run_${job_number} --nEvents $n_events --classificationOnly $classification_only --saveMG5RunDir $save_mg5_run_dir --saveHepMC $save_hepmc

