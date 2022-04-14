#!/bin/bash
echo "Creating base conda environment for Python $PYTHON_VERSION"
conda create --yes --prefix /home/miniconda3/envs python=$PYTHON_VERSION
conda activate /home/miniconda3/envs
conda install sphinx numpy flask

echo "Creating grism_overlap conda environment for Python $PYTHON_VERSION"
conda env update -f "env/environment-${PYTHON_VERSION}.yml" || exit 1
export CONDA_ENV=grism_overlap-$PYTHON_VERSION
source activate $CONDA_ENV

echo "The installed environment:"
conda env export