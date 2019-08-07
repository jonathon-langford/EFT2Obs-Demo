import os, sys
import math
from optparse import OptionParser
import yoda

# Import dicts storing STXS processes and EFT coeff.
from STXS import STXS_bins
from EFT import HEL_parameters

# Import Ai matrix from WG1 note
from wg1_note.stage1_Ai import Ai_matrix_wg1

# Import plotting scripts
from plotting.stxs2eft_plotting_scripts import plot_Ai_comparison

proc_to_STXS = {'ggh':'GG2H','vbf':'QQ2HQQ','wh':'QQ2HLNU','zh':'QQ2HLL','tth':'TTH'}
offset = {'stage0':2, 'stage1':1, 'stage1_1':1}

def leave( exit=True ):
  print "~~~~~~~~~~~~~~~~~~~~~~~ STXS2EFT: (extract scale functions) END ~~~~~~~~~~~~~~~~~~~~~~~"
  if exit: sys.exit(1)


def get_options():
  parser = OptionParser()
  parser.add_option('--stage', dest='stage', default='0', help="STXS stage [0,1,1_1]")
  parser.add_option('--processes', dest='processes', default='ggh', help="Comma separated list of signal process")
  parser.add_option('--textOutput', dest='textOutput', default=0, type='int', help="Display scaling functions on screen [1=yes,0=no]")
  parser.add_option('--outputDir', dest='outputDir', default='', help='Directory to store output plots. If specified then plots will be saved.')
  parser.add_option('--verbose', dest='verbose', default=0, type='int', help='Verbose output to screen [1=yes,0=no]')
  return parser.parse_args()
(opt,args) = get_options()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR EXTRACT INTERFERENCE TERM
def extract_Ai( stage, process, inputFile ):

  # Check input yoda file exists
  if not os.path.exists( inputFile ):
    print " --> [ERROR] input file %s does not exists. Leaving..."%inputFile
    leave()

  # Extract all objects from yoda file
  aos = yoda.read( inputFile )
  # Add hists for specified stage to dict: loop over HEL params
  histDict = {}

  # Requires a suffix: stage > 0 hists have additional string in name
  if stage == '0': suffix = ""
  else: suffix = "_pTjet30"
  for param in HEL_parameters: histDict[ param['param'] ] = aos[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[int_%s]'%(stage,suffix,param['param'])]
  # Also add SM
  histDict['sm'] = aos[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[sm]'%(stage,suffix)]

  # Define dicts to store Ai (+stat unc) for each param for each STXS process
  Ai = {}
  u_Ai = {}
  # Loop over bins in STXS: relevant to process
  s = "stage%s"%stage
  for stxs_idx in range( len( STXS_bins[s] ) ):
    # Require first part of string matches process
    if STXS_bins[s][stxs_idx].split("_")[0] == proc_to_STXS[process]:
    
      # Extract sm bin value (+uncertainty(
      x_sm = histDict['sm'].bins[stxs_idx].sumW
      u_sm = math.sqrt( histDict['sm'].bins[stxs_idx].sumW2 )

      # For each param: determine scaling (+stat uncertainty) and add to tmp dictionaries
      ai_tmp = {}
      u_ai_tmp = {}
      for param in HEL_parameters:
        p = param['param']
        ci = param['value']
        x_rwgt = histDict[p].bins[stxs_idx].sumW
        u_rwgt = math.sqrt( histDict[p].bins[stxs_idx].sumW2 )
        ai_tmp[p] = (x_rwgt-x_sm)/(x_sm*ci)
        u_ai_tmp[p] = abs(ai_tmp[p]*math.sqrt((u_rwgt/x_rwgt)*(u_rwgt/x_rwgt)+(u_sm/x_sm)*(u_sm/x_sm)))

      # Pruning: only save HEL params which have Ai > 0.001*max_Ai
      ai_pruned = {}
      u_ai_pruned = {}
      max_ai = -1
      for p,ai in ai_tmp.iteritems():
        if abs(ai) > max_ai: max_ai = abs(ai)
      for p,ai in ai_tmp.iteritems():
        if abs(ai) > 0.001*max_ai: 
          ai_pruned[p] = ai
          u_ai_pruned[p] = u_ai_tmp[p]

      # Scaling: scale params that should be scaled and then add to final dict
      ai_final = {}
      u_ai_final = {}
      for param in HEL_parameters:
        p = param['param']
        t = param['title']
        # For parameters passing pruning
        if p in ai_pruned:
          # Scale
          if 'divide_by' in param:
            ai_pruned[p] = ai_pruned[p]/param['divide_by']
            u_ai_pruned[p] = u_ai_pruned[p]/param['divide_by']
          # Add to final dictionary with title
          ai_final[t] = ai_pruned[p]
          u_ai_final[t] = u_ai_pruned[p]

      # Add final Ai to overall dict for each STXS process
      Ai[ STXS_bins[s][stxs_idx] ] = ai_final
      u_Ai[ STXS_bins[s][stxs_idx] ] = u_ai_final
        
  # Return Ai and stat uncertainty dicts 
  return Ai, u_Ai

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR DISPLAYING SCALING FUNCTIONS TO SCREEN
def sf2text( stage, process, ai_matrix ):
  print ""
  print "~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
  print " --> SCALING FUNCTIONS FOR: * process = %s"%proc
  print "                            * stage = %s"%stage 
  print ""
  # Loop over STXS bins relevant to process
  s = "stage%s"%stage
  for stxs_bin in STXS_bins[s]:

    if stxs_bin.split("_")[0] == proc_to_STXS[process]:

      # Construct line
      line = '1.0'
      # Loop over HEL parameters and extract scaling for specific bin
      for param in HEL_parameters:
        t = param['title']
        if t in ai_matrix[process][stxs_bin]:
          ai = ai_matrix[process][stxs_bin][t]
          sign = "+" if ai>=0 else "-"
          line += ' %s %.3g*%s'%(sign,abs(ai),t)
    
      # Print to screen
      print "   --> %s = %s"%(stxs_bin,line)

  print "~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
  print ""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN PROGRAM
if __name__ == '__main__':


  print "~~~~~~~~~~~~~~~~~~~~~~~~~ STXS2EFT: (extract scale functions) ~~~~~~~~~~~~~~~~~~~~~~~~~"

  # Loop over processes and store Ai (+unc) 
  Ai_matrix, u_Ai_matrix = {}, {}
  for proc in opt.processes.split(","): 
    fin = "../../Events/%s/yoda/%s.yoda"%(proc,proc)
    Ai_matrix[proc], u_Ai_matrix[proc] = extract_Ai( opt.stage, proc, fin )
    if opt.textOutput: sf2text( opt.stage, proc, Ai_matrix )

  # Plotting: if user has set outputDir then plot
  if opt.outputDir != '': 
    for proc in opt.processes.split(","):
      plot_Ai_comparison( opt.outputDir, opt.stage, proc, Ai_matrix_wg1, Ai_matrix, u_Ai_matrix, STXS_bins, HEL_parameters, proc_to_STXS, verbose=opt.verbose )

  # Finished
  leave( exit=False )
