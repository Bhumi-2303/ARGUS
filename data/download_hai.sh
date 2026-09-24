#!/bin/bash
mkdir -p hai/raw
cd hai/raw
for file in hai-train1.csv hai-train2.csv hai-train3.csv hai-train4.csv hai-test1.csv hai-test2.csv label-test1.csv label-test2.csv summary_label1.txt summary_label2.txt; do
    echo "Downloading $file..."
    curl -L --connect-timeout 10 --max-time 60 -o "$file" "https://github.com/icsdataset/hai/raw/master/hai-23.05/$file"
done
