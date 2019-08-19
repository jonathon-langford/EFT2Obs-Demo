import os, sys
import math
from optparse import OptionParser
import yoda

# Import dicts storing STXS processes and EFT coeff.
from STXS import STXS_bins
from EFT import HEL_parameters

# Import Ai matrix and Bij matrix from WG1 note
from wg1_note.stage1_Ai import Ai_matrix_wg1
from wg1_note.stage1_Bij import Bij_matrix_wg1

# Import plotting scripts
from plotting.stxs2eft_plotting_scripts import plot_Ai_comparison, plot_Bij_comparison

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
  parser.add_option('--plotAi', dest='plotAi', default=0, type='int', help='Plot Ai terms')
  parser.add_option('--plotBij', dest='plotBij', default=0, type='int', help='Plot Bij terms')
  parser.add_option('--outputDir', dest='outputDir', default='', help='Directory to store output plots')
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
# FUNCTION FOR EXTRACTING BSM TERMS: squared + cross terms
def extract_Bij( stage, process, inputFile_sm, inputFile_bsm, ci=0.1 ):
  
  #Check input yoda files exist
  if not os.path.exists( inputFile_sm ):
    print " --> [ERROR] SM input file %s does not exist. Leaving..."%inputFile_sm
    leave()
  if not os.path.exists( inputFile_bsm ):
    print " --> [ERROR] BSM input file %s does not exist. Leaving..."%inputFile_bsm
    leave()

  # Extract all objects from yoda files
  aos_sm = yoda.read( inputFile_sm )
  aos_bsm = yoda.read( inputFile_bsm )

  # Dictionary to store relevant histograms
  histDict = {}

  # Requires a suffix: stage > 0 hists have additional string in name
  if stage == '0': suffix = ""
  else: suffix = "_pTjet30"
  for param_i in HEL_parameters:
    # Squared terms
    if param_i['param'] in ['cG','c3G']: 
      histDict["bsm_%s"%param_i['param']] = aos_bsm[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[bsm_%s]'%(stage,suffix,param_i['param'])]
    # Cross terms
    for param_j in HEL_parameters:
      if HEL_parameters.index(param_i) < HEL_parameters.index(param_j):
        if( param_i['param'] in ['cG','c3G'] )&( param_j['param'] in ['cG','c3G'] ):
          histDict["bsm_%s%s"%(param_i['param'],param_j['param'])] = aos_bsm[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[bsm_%s_%s]'%(stage,suffix,param_i['param'],param_j['param'])]
  # Also add SM
  histDict['sm'] = aos_sm[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[sm]'%(stage,suffix)]

  # Calculate scaling factor: numEntries in SM/numEntries in BSM: FIXME change specific to cG
  #                           required as using different sample of events for bsm and sm
  sf = float(histDict['sm'].numEntries())/float(histDict['bsm_cG'].numEntries())

  # Define dicts to store Bij for each param + param pair for each STXS process
  Bij = {}
  u_Bij = {}
  # Loop over bins in STXS: relevant to process
  s = "stage%s"%stage
  for stxs_idx in range( len( STXS_bins[s] ) ):
    # Require first part of string matches process
    if STXS_bins[s][stxs_idx].split("_")[0] == proc_to_STXS[process]:
    
      # Extract sm bin value (+uncertainty(
      x_sm = histDict['sm'].bins[stxs_idx].sumW
      u_sm = math.sqrt( histDict['sm'].bins[stxs_idx].sumW2 )

      # For each parameter pair: determine squared + cross terms
      bij_tmp = {}
      u_bij_tmp = {}
      for param_i in HEL_parameters:
        p_i = param_i['param']
        for param_j in HEL_parameters:
          p_j = param_j['param']
          if HEL_parameters.index(param_i) < HEL_parameters.index(param_j):
            if( p_i in ['cG','c3G'] )&( p_j in ['cG','c3G'] ):

              x_bsm_i = histDict["bsm_%s"%p_i].bins[stxs_idx].sumW
              u_bsm_i = math.sqrt( histDict["bsm_%s"%p_i].bins[stxs_idx].sumW2 )
              x_bsm_j = histDict["bsm_%s"%p_j].bins[stxs_idx].sumW
              u_bsm_j = math.sqrt( histDict["bsm_%s"%p_j].bins[stxs_idx].sumW2 )

              # Check squared terms have not already been calculated
              if p_i not in bij_tmp:
                bij_tmp[p_i] = sf*(x_bsm_i/(ci*ci*x_sm))
                u_bij_tmp[p_i] = bij_tmp[p_i]*math.sqrt( (u_bsm_i/x_bsm_i)*(u_bsm_i/x_bsm_i) + (u_sm/x_sm)*(u_sm/x_sm) )
              if p_j not in bij_tmp:
                bij_tmp[p_j] = sf*(x_bsm_j/(ci*ci*x_sm))
                u_bij_tmp[p_j] = bij_tmp[p_j]*math.sqrt( (u_bsm_j/x_bsm_j)*(u_bsm_j/x_bsm_j) + (u_sm/x_sm)*(u_sm/x_sm) )

              # Calculate cross-term:
              x_bsm_ij = histDict["bsm_%s%s"%(p_i,p_j)].bins[stxs_idx].sumW
              u_bsm_ij = math.sqrt( histDict["bsm_%s%s"%(p_i,p_j)].bins[stxs_idx].sumW2 )
              bij_tmp["%s%s"%(p_i,p_j)] = sf*(1/(ci*ci*x_sm))*(x_bsm_ij-x_bsm_i-x_bsm_j)
              u_bij_tmp["%s%s"%(p_i,p_j)] = sf*(x_bsm_ij/(ci*ci*x_sm))*math.sqrt((u_bsm_ij/x_bsm_ij)*(u_bsm_ij/x_bsm_ij)+(u_sm/x_sm)*(u_sm/x_sm))
              #u_bij_tmp["%s%s"%(p_i,p_j)] = math.sqrt( ((x_bsm_ij/(ci*ci*x_sm))*(x_bsm_ij/(ci*ci*x_sm))*((u_bsm_ij/x_bsm_ij)*(u_bsm_ij/x_bsm_ij)+(u_sm/x_sm)*(u_sm/x_sm))) )
              #u_bij_tmp["%s%s"%(p_i,p_j)] = math.sqrt( ((x_bsm_ij/(ci*ci*x_sm))*(x_bsm_ij/(ci*ci*x_sm))*((u_bsm_ij/x_bsm_ij)*(u_bsm_ij/x_bsm_ij)+(u_sm/x_sm)*(u_sm/x_sm))) + u_bij_tmp[p_i]*u_bij_tmp[p_i] + u_bij_tmp[p_j]*u_bij_tmp[p_j] )

      
      # TODO: PRUNING

      # Scaling: scale params that should be scaled and then add to final dict        
      bij_final = {}
      u_bij_final = {}
      for param_i in HEL_parameters:
        p_i = param_i['param']
        t_i = param_i['title']
        for param_j in HEL_parameters:
          p_j = param_j['param']
          t_j = param_j['title']
          if HEL_parameters.index(param_i) < HEL_parameters.index(param_j):
            if( p_i in ['cG','c3G'] )&( p_j in ['cG','c3G'] ):

              #Squared terms: only add once
              if t_i not in bij_final:
                if 'divide_by' in param_i:
                  bij_tmp[p_i] = bij_tmp[p_i]/(param_i['divide_by']*param_i['divide_by'])
                  u_bij_tmp[p_i] = u_bij_tmp[p_i]/(param_i['divide_by']*param_i['divide_by'])
                # Add squared term to dict
                bij_final[t_i] = bij_tmp[p_i]
                u_bij_final[t_i] = u_bij_tmp[p_i]
              if t_j not in bij_final:
                if 'divide_by' in param_j:
                  bij_tmp[p_j] = bij_tmp[p_j]/(param_j['divide_by']*param_j['divide_by'])
                  u_bij_tmp[p_j] = u_bij_tmp[p_j]/(param_j['divide_by']*param_j['divide_by'])
                # Add squared term to dict
                bij_final[t_j] = bij_tmp[p_j]
                u_bij_final[t_j] = u_bij_tmp[p_j]

              # Mixed term
              f = 1
              if 'divide_by' in param_i: f*=param_i['divide_by']
              if 'divide_by' in param_j: f*=param_j['divide_by']
              bij_tmp["%s%s"%(p_i,p_j)] = bij_tmp["%s%s"%(p_i,p_j)]/f
              u_bij_tmp["%s%s"%(p_i,p_j)] = u_bij_tmp["%s%s"%(p_i,p_j)]/f
              # Add mixed term to dict
              bij_final["%s%s"%(t_i,t_j)] = bij_tmp["%s%s"%(p_i,p_j)]
              u_bij_final["%s%s"%(t_i,t_j)] = u_bij_tmp["%s%s"%(p_i,p_j)]
                

      # Add final Bij to overall dict for each STXS process
      Bij[ STXS_bins[s][stxs_idx] ] = bij_final      
      u_Bij[ STXS_bins[s][stxs_idx] ] = u_bij_final      

  #Return Bij and stat uncertainty
  return Bij, u_Bij


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR DISPLAYING SCALING FUNCTIONS TO SCREEN
def sf2text( stage, process, ai_matrix, bij_matrix, linearOnly=True ):
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
      # Loop over HEL parameters and extract Ai for specific bin
      for param in HEL_parameters:
        t = param['title']
        if t in ai_matrix[process][stxs_bin]:
          ai = ai_matrix[process][stxs_bin][t]
          sign = "+" if ai>=0 else "-"
          line += ' %s %.3g*%s'%(sign,abs(ai),t)

      if not linearOnly:

        # Loop over parameter pairs and extract Bij for specific bin
        squares = []
        for param_i in HEL_parameters:
          t_i = param_i['title']
          for param_j in HEL_parameters:
            t_j = param_j['title']
            if HEL_parameters.index(param_i) < HEL_parameters.index(param_j):
              if( t_i in ['cG\'','c3G'] )&( t_j in ['cG\'','c3G'] ):

                # Squared terms
                if( t_i in bij_matrix[process][stxs_bin] )&( t_i not in squares ):
                  bij = bij_matrix[process][stxs_bin][t_i]
                  sign = "+" if bij>=0 else "-"
                  line += ' %s %.3g*%s*%s'%(sign,abs(bij),t_i,t_i)
                  squares.append( t_i )
                if( t_j in bij_matrix[process][stxs_bin] )&( t_j not in squares ):
                  bij = bij_matrix[process][stxs_bin][t_j]
                  sign = "+" if bij>=0 else "-"
                  line += ' %s %.3g*%s*%s'%(sign,abs(bij),t_j,t_j)
                  squares.append( t_j )

                # Cross term
                bij = bij_matrix[process][stxs_bin]["%s%s"%(t_i,t_j)]
                sign = "+" if bij>=0 else "-"
                line += ' %s %.3g*%s*%s'%(sign,abs(bij),t_i,t_j)
                
      # Print to screen
      print "   --> %s = %s"%(stxs_bin,line)

  print "~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
  print ""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN PROGRAM
if __name__ == '__main__':

  print "~~~~~~~~~~~~~~~~~~~~~~~~~ STXS2EFT: (extract scale functions) ~~~~~~~~~~~~~~~~~~~~~~~~~"

  # Loop over processes and store Ai(+unc) and Bij(+unc)
  Ai_matrix, u_Ai_matrix = {}, {}
  Bij_matrix, u_Bij_matrix = {}, {}
  for proc in opt.processes.split(","): 

    # Ai
    fin = "../../Events/%s/yoda/%s.yoda"%(proc,proc)
    Ai_matrix[proc], u_Ai_matrix[proc] = extract_Ai( opt.stage, proc, fin )

    # Bij
    fin_bsm = "../../Events/%s_bsm/yoda/%s_bsm.yoda"%(proc,proc)
    Bij_matrix[proc], u_Bij_matrix[proc] = extract_Bij( opt.stage, proc, fin, fin_bsm, ci=0.0001 )

    # Display scaling functions to screen
    if opt.textOutput: sf2text( opt.stage, proc, Ai_matrix, Bij_matrix, linearOnly=False )

  print " --> [DEBUG] Bij = %s"%Bij_matrix
  print ""
  print " --> [DEBUG] u_Bij = %s"%u_Bij_matrix

  # Plotting: if user has set outputDir then plot
  if opt.outputDir != '': 
    for proc in opt.processes.split(","):
      if opt.plotAi: plot_Ai_comparison( opt.outputDir, opt.stage, proc, Ai_matrix_wg1, Ai_matrix, u_Ai_matrix, STXS_bins, HEL_parameters, proc_to_STXS, verbose=opt.verbose )
      if opt.plotBij: plot_Bij_comparison( opt.outputDir, opt.stage, proc, Bij_matrix_wg1, Bij_matrix, u_Bij_matrix, STXS_bins, HEL_parameters, proc_to_STXS, verbose=opt.verbose )

  # Finished
  leave( exit=False )
