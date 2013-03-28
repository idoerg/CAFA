#!/bin/bash

infile=$1
outfile=$2

`sort $infile | uniq > $outfile` 