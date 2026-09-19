#!/bin/bash
echo "Waiting for background jobs to finish..."
while true; do
    count=0
    for seed in 123 456 789 1011; do
        if grep -q "Done seed $seed" scratch/repo_$seed/run_$seed.log 2>/dev/null; then
            echo "Seed $seed finished."
        else
            count=$((count+1))
        fi
    done
    if [ $count -eq 0 ]; then
        echo "All seeds finished!"
        break
    fi
    echo "Waiting for $count seeds... sleeping 60s"
    sleep 60
done
