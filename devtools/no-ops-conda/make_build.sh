#!/usr/bin/env bash

# Basic idea: get the requirements for OPS and put them in a file. Then have
# conda install them.

OPS_CONDA_RECIPE="https://raw.githubusercontent.com/openpathsampling/openpathsampling/master/devtools/conda-recipe"
MYDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

curl ${OPS_CONDA_RECIPE}/meta.yaml | 
    grep "\ \ \ \ \-\ " | 
    sed 's/\ \ \ \ \-\ //' |
    #sed 's/\ .*//' |
    sed 's/\(.*\)\ /\1=/' |
    sort | uniq |
    grep -v "openpathsampling" > ${MYDIR}/ops_reqs.txt

cp ${MYDIR}/../conda-recipe/meta.yaml ${MYDIR}/meta.yaml
export PYTHON=`which python`
echo "#!/bin/bash
conda install --file ${MYDIR}/ops_reqs.txt" > ${MYDIR}/build.sh
echo 'export ORIG=`pwd`
cd && git clone https://github.com/choderalab/openpathsampling
cd openpathsampling && python setup.py install
cd $ORIG

${PYTHON} setup.py install
' >> ${MYDIR}/build.sh
