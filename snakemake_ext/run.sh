#!/bin/bash
export PYTHONPATH=$(pwd)

snakemake \
    --cores 40 \
    --configfile $(pwd)/profiles/my_hpc_profile/config.yaml \
    --forceall \
    --verbose

