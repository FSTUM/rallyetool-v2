#!/bin/bash

# This function creates a 1 2 5 10 and 30 sec slice for each input file 
prepareSong () {
        len=(1 3 5 10 30)
        for l in "${len[@]}" 
        do
                echo "---------------------------------------------------------------"
                echo "Creating $l-$1"
                ffmpeg -i $f -ss 00:00:00 -to 00:00:$l -c copy output/$l-$f
                echo "---------------------------------------------------------------"
        done
}

# Create the output folder
mkdir -p output

# Loop songs in current directory 
for f in *.m4a *.mp3 *.wav
do 
    prepareSong $f 
done 
echo "Done"
