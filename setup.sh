#!/usr/bin/env bash
set -x
set -e

### SET ENVIRONMENT VARIABLES HERE
LHAPDF_CONFIG_PATH="/cvmfs/cms.cern.ch/slc7_amd64_gcc630/external/lhapdf/6.2.1-ghjeda/bin/lhapdf-config"
MG_DIR="MG5_aMC_v2_6_5"
MG_TARBALL="MG5_aMC_v2.6.5.tar.gz"
###

wget https://launchpad.net/mg5amcnlo/2.0/2.6.x/+download/${MG_TARBALL}
tar -zxf ${MG_TARBALL}
rm ${MG_TARBALL}

# Create MG config
{
	echo "set lhapdf ${LHAPDF_CONFIG_PATH}"
	echo "set auto_update 0"
	echo "set automatic_html_opening False"
	echo "save options"
  echo "install pythia8"
} > mgconfigscript

# Apply path: allows weights to be saved when converting lhe to hepmc
pushd ${MG_DIR}
./bin/mg5_aMC ../mgconfigscript
patch -p0 < ../MG5aMC_PY8_interface.cc.patch
pushd HEPTools/MG5aMC_PY8_interface
python compile.py ../pythia8
popd
popd

# Import HEL FeynRules model into MG
pushd ${MG_DIR}/models
wget https://feynrules.irmp.ucl.ac.be/raw-attachment/wiki/HEL/HEL_UFO.tar.gz
tar -zxf HEL_UFO.tar.gz
rm HEL_UFO.tar.gz
popd

# Download and install Rivet v3.0.0
wget https://phab.hepforge.org/source/rivetbootstraphg/browse/3.0.0/rivet-bootstrap?view=raw -O rivet-bootstrap
bash rivet-bootstrap

# Set up Rivet environment
source local/rivetenv.sh
export RIVET_ANALYSIS_PATH=${PWD}/Classification
#source rivet_env.sh

# Build classification tool
pushd Classification
rivet-buildplugin RivetHiggsTemplateCrossSections.so HiggsTemplateCrossSections.cc
popd

echo " --> SETUP COMPLETE!"
