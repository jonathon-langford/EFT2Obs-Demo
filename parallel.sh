#!/bin/bash

# Set up environment
export EFT2OBS_BASE=$1
cd $EFT2OBS_BASE

#Input to run.py
mode=$2
process=$3
job_number=$4
n_events=$5
delete_mg5_run_dir=$6

# Run
python run_parallel.py --mode $mode --process $process --runLabel run_${job_number} --nEvents $n_events --deleteMG5RunDir $delete_mg5_run_dir

