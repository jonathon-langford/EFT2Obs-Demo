import os, sys
from optparse import OptionParser
# ROOT specific libraries
import ROOT

#Import dicts storing STXS processes and EFT coefficients
from STXS import STXS_bins
from EFT import HEL_parameters

proc_to_STXS = {'ggh':'GG2H'}
offset = {'stage0':2, 'stage1':1, 'stage1_1':1}

def leave():
  print "~~~~~~~~~~~~~~~~~~~~~~~ STXS2EFT: (extract scale functions) END ~~~~~~~~~~~~~~~~~~~~~~~"
  sys.exit(1)


  print "~~~~~~~~~~~~~~~~~~~~~~~~~ STXS2EFT: (extract scale functions) ~~~~~~~~~~~~~~~~~~~~~~~~~"
  
def get_options():
  parser = OptionParser()
  parser.add_option('--stage', dest='stage', default='0', help="STXS stage [0,1,1_1]")
  parser.add_option('--process', dest='process', default='ggh', help="Signal process")
  parser.add_option('--inputFile', dest='inputFile', default='', help="Input root file")
  return parser.parse_args()

(opt,args) = get_options()

def extract_SF( stage, process, inputFile ):

  # Check if input root file exists
  if not os.path.exists( inputFile ):
    print " --> [ERROR] input file %s does not exists. Leaving..."%inputFile
    leave()

  # Open root file
  f_in = ROOT.TFile( inputFile )

  # Extract histograms for specified stage and store in dict: loop over HEL parameters
  histDict = {}

  # Require suffix to as stage > 0 hists have different names
  if stage == '0': suffix = ""
  else: suffix = "_pTjet30"
  for param in HEL_parameters: histDict[ param['param'] ] = f_in.Get('HiggsTemplateCrossSections/STXS_stage%s%s[int_%s]'%(stage,suffix,param['param']))
  # Also add SM
  histDict['sm'] = f_in.Get('HiggsTemplateCrossSections/STXS_stage%s%s[sm]'%(stage,suffix))

  #Scale all histograms
  for hist in histDict: histDict[hist].Scale(1,'width')

  # Loop over bins in STXS distribution relevant to process
  s = "stage%s"%stage
  for stxs_idx in range( len( STXS_bins[s] ) ):
    # Require first part of string matches process
    if STXS_bins[s][stxs_idx].split("_")[0] == proc_to_STXS[process]:

      # Extract sm bin value
      x_sm = histDict['sm'].GetBinContent( stxs_idx+offset[s] )

      # For each param: determine scaling and add to dict
      param_scaling = {}
      for param in HEL_parameters:
        p = param['param']
        ci = param['value']
        x_tot = histDict[p].GetBinContent( stxs_idx+offset[s] )
        x_int = (x_tot-x_sm)/ci
        x_int /= x_sm
        param_scaling[p] = x_int

      # Only save params which give coeff > 0.001*max coeff
      pruned_param_scaling = {}
      max_coeff = -1
      for p in param_scaling: 
        if param_scaling[p] > max_coeff: max_coeff = param_scaling[p]
      for p in param_scaling:
        if param_scaling[p] > 0.001*max_coeff: pruned_param_scaling[p] = param_scaling[p]

      # Loop over HEL parameters and output scaling functions in nice format
      line = '1.0'
      for param in HEL_parameters:
        p = param['param']
        t = param['title']
        if p in pruned_param_scaling:
          if 'divide_by' in param: coeff = pruned_param_scaling[p]/param['divide_by']
          else: coeff = pruned_param_scaling[p]
          sign = "+" if coeff>=0 else "-"
          line += ' %s %.3g*%s'%(sign,abs(coeff),t)
      
      # Print line to user
      print "%s --> %s"%(STXS_bins[s][stxs_idx],line)

  leave()

if __name__ == '__main__': extract_SF( opt.stage, opt.process, opt.inputFile )
  
    

  

  

