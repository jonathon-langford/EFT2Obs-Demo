import os, sys
import math
from optparse import OptionParser
import yoda
import re

# Import dicts storing STXS processes and EFT coeff.
from STXS import STXS_bins
from EFT import HEL_parameters, HEL_parameters_subset

# Import Ai matrix and Bij matrix from WG1 note
from wg1_note.stage1_Ai import Ai_matrix_wg1
from wg1_note.stage1_Bij import Bij_matrix_wg1

# Import plotting scripts
from plotting.stxs2eft_plotting_scripts import plot_Ai, plot_Bij, plot_Ai_comparison, plot_Bij_comparison

proc_to_STXS = {'ggh':'GG2H','vbf':'QQ2HQQ','wh':'QQ2HLNU','zh':'QQ2HLL','tth':'TTH'}
offset = {'stage0':2, 'stage1':1, 'stage1_1':1}

def leave( exit=True ):
  print "~~~~~~~~~~~~~~~~~~~~~~~ STXS2EFT: (extract scale functions) END ~~~~~~~~~~~~~~~~~~~~~~~"
  if exit: sys.exit(1)


def get_options():
  parser = OptionParser()
  parser.add_option('--stage', dest='stage', default='0', help="STXS stage [0,1,1_1]")
  parser.add_option('--processes', dest='processes', default='ggh', help="Comma separated list of signal process")
  parser.add_option('--freezeOtherParameters', dest='freezeOtherParameters', default=0, type='int', help="Freeze all but [cG,cA,cu,cHW,cWW,cB]")
  parser.add_option('--linearOnly', dest='linearOnly', default=0, type='int', help="Only calculate linear terms (Ai)")
  parser.add_option('--combineOutput', dest='combineOutput', default=0, type='int', help="Write scaling functions in format to be read by combine [1=yes,0=no]")
  parser.add_option('--textOutput', dest='textOutput', default=0, type='int', help="Display scaling functions on screen [1=yes,0=no]")
  parser.add_option('--plotAi', dest='plotAi', default=0, type='int', help='Plot Ai terms')
  parser.add_option('--plotBij', dest='plotBij', default=0, type='int', help='Plot Bij terms')
  parser.add_option('--plotAiValidation', dest='plotAiValidation', default=0, type='int', help='Plot Ai terms comparison to WG1 note')
  parser.add_option('--plotBijValidation', dest='plotBijValidation', default=0, type='int', help='Plot Bij terms comparison to WG1 note')
  parser.add_option('--outputDir', dest='outputDir', default='', help='Directory to store output plots')
  parser.add_option('--verbose', dest='verbose', default=0, type='int', help='Verbose output to screen [1=yes,0=no]')
  return parser.parse_args()
(opt,args) = get_options()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR EXTRACT INTERFERENCE TERM
def extract_Ai( stage, process, pois, inputFile ):

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
  for param in pois: histDict[ param['param'] ] = aos[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[int_%s]'%(stage,suffix,param['param'])]
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
      for param in pois:
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
      for param in pois:
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
      print " --> [STATUS] Calculated all Ai for %s"%STXS_bins[s][stxs_idx]
        
  # Return Ai and stat uncertainty dicts 
  return Ai, u_Ai

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR EXTRACTING BSM TERMS: squared + cross terms
def extract_Bij( stage, process, pois, inputFile_sm, inputFile_bsm, w=0.1, f=1., threshold=1e-8 ):
  
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
  for param_i in pois:
    # Squared terms
    histDict["bsm_%s"%param_i['param']] = aos_bsm[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[bsm_%s]'%(stage,suffix,param_i['param'])]
    # Cross terms
    for param_j in pois:
      if pois.index(param_i) < pois.index(param_j):
        histDict["bsm_%s%s"%(param_i['param'],param_j['param'])] = aos_bsm[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[bsm_%s_%s]'%(stage,suffix,param_i['param'],param_j['param'])]
  # Also add SM
  histDict['sm'] = aos_sm[u'/RAW/HiggsTemplateCrossSections/STXS_stage%s%s[sm]'%(stage,suffix)]

  # Calculate scaling factor: numEntries in SM/numEntries in BSM: FIXME change specific to cG
  #                           required as using different sample of events for bsm and sm
  if process in ['wh','zh']: nEntries_BSM = float(histDict['bsm_cHW'].numEntries())
  else: nEntries_BSM = float(histDict['bsm_cG'].numEntries())
  nEntries_SM = histDict['sm'].numEntries()
  #print " --> [DEBUG] SM = %.4f, BSM = %.4f"%(nEntries_SM,nEntries_BSM)
  sf = nEntries_SM/nEntries_BSM
  #print " --> [DEBUG] s.f. = %.4f"%sf

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

      # Define tmp dicts to store Bij terms (+stat unc)
      bij_tmp = {}
      u_bij_tmp = {}

      # For each parameter: determine squared term
      for param_i in pois:
        p_i = param_i['param']
        # Check: rwgted xs above threshold
        if histDict["bsm_%s"%p_i].bins[stxs_idx].sumW < threshold: continue

        # Calculate squared terms and add to dict
        x_bsm_i = histDict["bsm_%s"%p_i].bins[stxs_idx].sumW
        u_bsm_i = math.sqrt( histDict["bsm_%s"%p_i].bins[stxs_idx].sumW2 )
        bij_tmp[p_i] = sf*(x_bsm_i/(w*w*x_sm))
        u_bij_tmp[p_i] = bij_tmp[p_i]*math.sqrt( (u_bsm_i/x_bsm_i)*(u_bsm_i/x_bsm_i) + (u_sm/x_sm)*(u_sm/x_sm) )

      # For each parameter pair: determine cross terms
      for param_i in pois:
        for param_j in pois:
          if pois.index(param_i) < pois.index(param_j):
            p_i = param_i['param']
            p_j = param_j['param']
            # Check: rwgted xs above threshold
            if histDict["bsm_%s%s"%(p_i,p_j)].bins[stxs_idx].sumW < threshold: continue

            # Calculate cross-term and add to dict
            x_bsm_ij = histDict["bsm_%s%s"%(p_i,p_j)].bins[stxs_idx].sumW
            u_bsm_ij = math.sqrt( histDict["bsm_%s%s"%(p_i,p_j)].bins[stxs_idx].sumW2 )
            bij_tilda = sf*((f*f*x_bsm_ij)/(w*w*x_sm))
            u_bij_tilda = bij_tilda*math.sqrt( (u_bsm_ij/x_bsm_ij)*(u_bsm_ij/x_bsm_ij) + (u_sm/x_sm)*(u_sm/x_sm) )
            # Check: squared terms exist
            if(p_i in bij_tmp)&(p_j in bij_tmp): 
              bij_tmp["%s%s"%(p_i,p_j)] = bij_tilda-bij_tmp[p_i]-bij_tmp[p_j]
              u_bij_tmp["%s%s"%(p_i,p_j)] = math.sqrt( u_bij_tilda*u_bij_tilda+u_bij_tmp[p_i]*u_bij_tmp[p_i]+u_bij_tmp[p_j]*u_bij_tmp[p_j] )
            elif(p_i in bij_tmp): 
              bij_tmp["%s%s"%(p_i,p_j)] = bij_tilda-bij_tmp[p_i]
              u_bij_tmp["%s%s"%(p_i,p_j)] = math.sqrt( u_bij_tilda*u_bij_tilda+u_bij_tmp[p_i]*u_bij_tmp[p_i] )
            elif(p_j in bij_tmp): 
              bij_tmp["%s%s"%(p_i,p_j)] = bij_tilda-bij_tmp[p_j]
              u_bij_tmp["%s%s"%(p_i,p_j)] = math.sqrt( u_bij_tilda*u_bij_tilda+u_bij_tmp[p_j]*u_bij_tmp[p_j] )
            else:
              bij_tmp["%s%s"%(p_i,p_j)] = bij_tilda
              u_bij_tmp["%s%s"%(p_i,p_j)] = u_bij_tilda
        
      # Pruning: only save HEL params which have Ai > 0.001*max_Ai
      bij_pruned = {}
      u_bij_pruned = {}
      max_bij = -1
      for p,bij in bij_tmp.iteritems():
        if abs(bij) > max_bij: max_bij = abs(bij)
      for p,bij in bij_tmp.iteritems():
        if abs(bij) > 0.00001*max_bij:
          bij_pruned[p] = bij
          u_bij_pruned[p] = u_bij_tmp[p]

      # Scaling: scale params that should be scaled and then add to final dict        
      bij_final = {}
      u_bij_final = {}
      # Squared terms
      for param_i in pois:
        p_i, t_i = param_i['param'], param_i['title']
        #Check: term in pruned dictionary
        if p_i in bij_pruned:
          a = 1
          if 'divide_by' in param_i: a*=param_i['divide_by']*param_i['divide_by']
          bij_final[t_i] = bij_pruned[p_i]/a
          u_bij_final[t_i] = u_bij_pruned[p_i]/a

      # Cross terms
      for param_i in pois:
        for param_j in pois:
          if pois.index(param_i) < pois.index(param_j):
            p_i, t_i = param_i['param'], param_i['title']
            p_j, t_j = param_j['param'], param_j['title']
            #Check: term in pruned dictionary
            if "%s%s"%(p_i,p_j) in bij_pruned:
              a = 1
              if 'divide_by' in param_i: a*=param_i['divide_by']
              if 'divide_by' in param_j: a*=param_j['divide_by']
              bij_final["%s%s"%(t_i,t_j)] = bij_pruned["%s%s"%(p_i,p_j)]/a
              u_bij_final["%s%s"%(t_i,t_j)] = u_bij_pruned["%s%s"%(p_i,p_j)]/a

      # Add final Bij to overall dict for each STXS process
      Bij[ STXS_bins[s][stxs_idx] ] = bij_final      
      u_Bij[ STXS_bins[s][stxs_idx] ] = u_bij_final      

      print " --> [STATUS] Calculated all Bij for %s"%STXS_bins[s][stxs_idx]

  #Return Bij and stat uncertainty
  return Bij, u_Bij


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR DISPLAYING SCALING FUNCTIONS TO SCREEN
def sf2text( stage, process, pois, ai_matrix, bij_matrix, linearOnly=True ):
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
      line = '1'
      # Loop over HEL parameters and extract Ai for specific bin
      for param in pois:
        t = param['title']
        # Ignore CP conjugate terms
        #if t[0]=="t": continue
        if t in ai_matrix[process][stxs_bin]:
          ai = ai_matrix[process][stxs_bin][t]
          t = re.sub('\'','',t)
          sign = "+" if ai>=0 else "-"
          if sign == "-": line += ' %s%.3f * %s'%(sign,abs(ai),t)
          else: line += ' %s %.3f * %s'%(sign,abs(ai),t)
          #line += ' %s %.3g*%s'%(sign,abs(ai),t)

      if not linearOnly:

        # Loop over parameters (and pairs) and extract Bij for specific bin
        for param_i in pois:
          t_i = param_i['title']
          if t_i in bij_matrix[process][stxs_bin]:
            bij = bij_matrix[process][stxs_bin][t_i]
            t_i = re.sub('\'','',t_i)
            sign = "+" if bij>=0 else "-"
            if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_i)
            else: line += ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_i)
            #line += ' %s %.4g*%s*%s'%(sign,abs(bij),t_i,t_i)

        for param_i in pois:
          for param_j in pois:
            if pois.index(param_i) < pois.index(param_j):
              t_i, t_j = param_i['title'], param_j['title']
              # Ignore CP odd * CP even cross terms
              if((t_i[0]=="t")&(t_j[0]!="t"))|((t_i[0]!="t")&(t_j[0]=="t")): continue
              if "%s%s"%(t_i,t_j) in bij_matrix[process][stxs_bin]:
                bij = bij_matrix[process][stxs_bin]["%s%s"%(t_i,t_j)]
                t_i = re.sub('\'','',t_i)
                t_j = re.sub('\'','',t_j)
                sign = "+" if bij>=0 else "-"
                if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_j)
                else: ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_j)
                #line += ' %s %.4g*%s*%s'%(sign,abs(bij),t_i,t_j)
                
      # Print to screen
      print "   --> %s = %s"%(stxs_bin,line)

  print "~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
  print ""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR WRITING OUT EQUATION IN FORMAT TO BE READ BY COMBINE
def sf2combine( stage, processes, pois, ai_matrix, bij_matrix, linearOnly=True ):

  if not os.path.isdir("./output"): os.system("mkdir ./output")

  #Open file to write to
  if linearOnly: f_out = open("output/stage%s_xs_Aionly.txt"%stage,"w")
  else: f_out = open("output/stage%s_xs.txt"%stage,"w")

  equations = []

  # Loop over processes
  for process in processes.split(","):

    # Loop over STXS bins relevant to process
    s = "stage%s"%stage
    for stxs_bin in STXS_bins[s]:

      if stxs_bin.split("_")[0] == proc_to_STXS[process]:

        # Construct line
        line = '1'
        # Loop over HEL parameters and extract Ai for specific bin
        for param in pois:
          t = param['title']
          # Ignore CP conjugate terms
          #if t[0]=="t": continue
          if t in ai_matrix[process][stxs_bin]:
            ai = ai_matrix[process][stxs_bin][t]
            t = re.sub('\'','',t)
            sign = "+" if ai>=0 else "-"
            if sign == "-": line += ' %s%.3f * %s'%(sign,abs(ai),t)
            else: line += ' %s %.3f * %s'%(sign,abs(ai),t)
            #line += ' %s %.3g*%s'%(sign,abs(ai),t)

        if not linearOnly:

          # Loop over parameters (and pairs) and extract Bij for specific bin
          for param_i in pois:
            t_i = param_i['title']
            if t_i in bij_matrix[process][stxs_bin]:
              bij = bij_matrix[process][stxs_bin][t_i]
              t_i = re.sub('\'','',t_i)
              sign = "+" if bij>=0 else "-"
              if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_i)
              else: line += ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_i)
              #line += ' %s %.4g*%s*%s'%(sign,abs(bij),t_i,t_i)

          for param_i in pois:
            for param_j in pois:
              if pois.index(param_i) < pois.index(param_j):
                t_i, t_j = param_i['title'], param_j['title']
                # Ignore CP odd * CP even cross terms
                if((t_i[0]=="t")&(t_j[0]!="t"))|((t_i[0]!="t")&(t_j[0]=="t")): continue
                if "%s%s"%(t_i,t_j) in bij_matrix[process][stxs_bin]:
                  bij = bij_matrix[process][stxs_bin]["%s%s"%(t_i,t_j)]
                  t_i = re.sub('\'','',t_i)
                  t_j = re.sub('\'','',t_j)
                  sign = "+" if bij>=0 else "-"
                  if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_j)
                  else: ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_j)
                  #line += ' %s %.4g*%s*%s'%(sign,abs(bij),t_i,t_j)
                  
        # Print to screen
        equations.append( [stxs_bin,line] )

  for e in equations:
    stxs_bin, eq = e[0], e[1]
    stxs_bin = re.sub("GG2H","ggH",stxs_bin)
    stxs_bin = re.sub("QQ2HQQ","qqH",stxs_bin)
    stxs_bin = re.sub("QQ2HLNU","WH_lep",stxs_bin)
    stxs_bin = re.sub("QQ2HLL","ZH_lep",stxs_bin)
    stxs_bin = re.sub("TTH","ttH",stxs_bin)
    if "FWDH" in stxs_bin: continue
    else: f_out.write("%s:%s\n"%(stxs_bin,eq))

  # Repeat VBF equations for WH_had and ZH_had
  for mode in ['WH_had','ZH_had']:
    for e in equations:
      stxs_bin, eq = e[0], e[1]
      if "QQ2HQQ" in stxs_bin: 
        stxs_bin = re.sub("QQ2HQQ",mode,stxs_bin)
        if "FWDH" in stxs_bin: continue
        else: f_out.write("%s:%s\n"%(stxs_bin,eq))

  # Close file
  f_out.close()
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# MAIN PROGRAM
if __name__ == '__main__':

  print "~~~~~~~~~~~~~~~~~~~~~~~~~ STXS2EFT: (extract scale functions) ~~~~~~~~~~~~~~~~~~~~~~~~~"

  if opt.freezeOtherParameters: parametersOfInterest = HEL_parameters_subset
  else: parametersOfInterest = HEL_parameters

  # Loop over processes and store Ai(+unc) and Bij(+unc)
  Ai_matrix, u_Ai_matrix = {}, {}
  Bij_matrix, u_Bij_matrix = {}, {}
  for proc in opt.processes.split(","): 

    # Ai
    fin = "../../Events/%s/yoda/%s.yoda"%(proc,proc)
    Ai_matrix[proc], u_Ai_matrix[proc] = extract_Ai( opt.stage, proc, parametersOfInterest, fin )

    if not opt.linearOnly:
      # Bij
      fin_bsm = "../../Events/%s_bsm/yoda/%s_bsm.yoda"%(proc,proc)
      Bij_matrix[proc], u_Bij_matrix[proc] = extract_Bij( opt.stage, proc, parametersOfInterest, fin, fin_bsm, w=0.0001 )

    # Display full scaling functions to screen
    if opt.textOutput: sf2text( opt.stage, proc, parametersOfInterest, Ai_matrix, Bij_matrix, linearOnly=opt.linearOnly )

  if opt.combineOutput: sf2combine( opt.stage, opt.processes, parametersOfInterest, Ai_matrix, Bij_matrix, linearOnly=opt.linearOnly )

  # Plotting: if user has set outputDir then plot
  if opt.outputDir != '': 
    for proc in opt.processes.split(","):
      if opt.plotAi: plot_Ai( opt.outputDir, opt.stage, proc, Ai_matrix, u_Ai_matrix, STXS_bins, parametersOfInterest, proc_to_STXS )
      if opt.plotAiValidation: plot_Ai_comparison( opt.outputDir, opt.stage, proc, Ai_matrix_wg1, Ai_matrix, u_Ai_matrix, STXS_bins, parametersOfInterest, proc_to_STXS, verbose=opt.verbose )
      if not opt.linearOnly:
        if opt.plotBij: plot_Bij( opt.outputDir, opt.stage, proc, Bij_matrix, u_Bij_matrix, STXS_bins, parametersOfInterest, proc_to_STXS )
        if opt.plotBijValidation: plot_Bij_comparison( opt.outputDir, opt.stage, proc, Bij_matrix_wg1, Bij_matrix, u_Bij_matrix, STXS_bins, parametersOfInterest, proc_to_STXS, verbose=opt.verbose )

  # Finished
  leave( exit=False )
