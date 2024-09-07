#!/bin/bash

# Declare an associative array where the keys are 'atimg' and the values are 'cap1:cap2' pairs
declare -A pairs=(
  # ["gender/male"]="gender/science:gender/liberal-arts"
  # ["gender/female"]="gender/science:gender/liberal-arts"
  # ["intersectional/white-male"]="gender/science:gender/liberal-arts"
  # ["intersectional/black-female"]="gender/science:gender/liberal-arts"
  # ["arab-muslim/arab-muslim"]="valence/pleasant:valence/unpleasant"
  ["arab-muslim/other-people"]="valence/pleasant:valence/unpleasant"
  # ["american_race/european-american-google"]="valence/pleasant:valence/unpleasant"
  # ["american_race/african-american-google"]="valence/pleasant:valence/unpleasant"
  # ["american_race/asian-american-google"]="valence/pleasant:valence/unpleasant"
  # ["sexuality/gay"]="valence/pleasant:valence/unpleasant"
  # ["sexuality/straight"]="valence/pleasant:valence/unpleasant"
)

# List of GPUs to use
GPU_IDS=(2 3 4 5 6)
IDX=0

# Loop through the associative array and call the Python script with the parameters
for clip_model in 'RN50x4' 'ViT-L14' 'ViT-B32'
do 
for atimg in "${!pairs[@]}"; do
  IFS=':' read -r -a captions <<< "${pairs[$atimg]}"
  cap1="${captions[0]}"
  cap2="${captions[1]}"
  
  # Check if all GPUs are in use
  if [ $IDX -eq 0 ]; then
    wait
  fi
  
  # Call the Python script with the current pair of arguments and assign GPU ID
  CUDA_VISIBLE_DEVICES=${GPU_IDS[$IDX]} python main.py --data_name clipmm --attribute_image "$atimg" --target_caption1 "$cap1" --target_caption2 "$cap2" --clip_model ${clip_model} &

  # Increment IDX and reset if it exceeds the number of GPUs
  IDX=$((IDX+1))
  if [ $IDX -ge ${#GPU_IDS[@]} ]; then
    IDX=0
  fi
done
done

# Wait for all background processes to finish
wait
