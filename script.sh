#!/bin/bash
for FILE in /var/tmp/hackathon/more*;
do python3 parallelipipedi.py $FILE;
done