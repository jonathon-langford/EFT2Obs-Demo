import os, sys
import math
from optparse import OptionParser
import yoda 
import re

# Import dict for EFT coeff.
from EFT import HEL_parameters, HEL_parameters_subset
from Differential import Differential_bins

def leave( exit=True ):
  print "~~~~~~~~~~~~~~~~~~~~~~~ OBS2EFT: (extract scale functions) END ~~~~~~~~~~~~~~~~~~~~~~~"
  if exit: sys.exit(1)

def get_options():
  parser = OptionParser()
  parser.add_option('--processes', dest='processes', default='hww_leptonic', help="Comma separated list of signal process")
  parser.add_option('--variable', dest='variable', default='pTH', help="Variable (mapping to histogram defined in VariableToHistogramDict)")
  parser.add_option('--freezeOtherParameters', dest='freezeOtherParameters', default=0, type='int', help="Freeze all but subset defined in EFT.py")
  parser.add_option('--linearOnly', dest='linearOnly', default=0, type='int', help="Only calculate linear terms (Ai)")
  parser.add_option('--combineOutput', dest='combineOutput', default=0, type='int', help="Write scaling functions in format to be read by combine [1=yes,0=no]")
  parser.add_option('--textOutput', dest='textOutput', default=0, type='int', help="Display scaling functions on screen [1=yes,0=no]")
  return parser.parse_args()
(opt,args) = get_options()

VariableToHistogramDict = {"pTH":"pT_Higgs_hww_differential","Njets30":"Njets_30_hww_differential"}

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR EXTRACTING INT TERMS
def extract_Ai( process, pois, var, inputFile_sm, inputFile_int, ci=0.0001 ):
  
  # Check input yoda files exists
  for f in [inputFile_sm,inputFile_int]: 
    if not os.path.exists( f ):
      print " --> [ERROR] input file %s does not exist. Leaving..."%f
      leave()

  # Extract all opbjects from yoda files
  aos_sm = yoda.read( inputFile_sm )
  aos_int = yoda.read( inputFile_int )

  # Dictionary to store relevant histograms
  histDict = {}

  # Loop over EFT params and extract reweighted
  for param in pois: histDict["int_%s"%param['param']] = aos_int[u'/RAW/HiggsTemplateCrossSections/%s[int_%s]'%(VariableToHistogramDict[var],param['param'])]
  # Also add SM
  histDict['sm'] = aos_sm[u'/RAW/HiggsTemplateCrossSections/%s[Weight_MERGING=0.000]'%VariableToHistogramDict[var]]

  # Calculate scaling factor: numEntries different in diff samples
  nEntries_int = float(histDict['int_cHW'].numEntries())
  nEntries_sm  = float(histDict['sm'].numEntries())
  sf = nEntries_sm/nEntries_int

  # Define Dicts to store Ai + unc
  Ai, u_Ai = {}, {}
  # Loop over bins in variable
  for bin_idx in range( len( Differential_bins[var] ) ):
  
    # Extract sm bin value
    x_sm = histDict['sm'].bins[bin_idx].sumW
    u_sm = math.sqrt( histDict['sm'].bins[bin_idx].sumW2 )

    # Define tmp dicts to store Ai terms (+stat unc)
    ai_tmp = {}
    u_ai_tmp = {}
 
    # Loop over params
    for param in pois:
      p = param['param']
      # Calculate Ai terms and add to dict
      x_int = histDict['int_%s'%p].bins[bin_idx].sumW
      u_int = math.sqrt( histDict['int_%s'%p].bins[bin_idx].sumW2 )
      ai_tmp[p] = sf*(x_int/(ci*x_sm))
      if ai_tmp[p] == 0: u_ai_tmp[p] = 0
      else: u_ai_tmp[p] = abs(ai_tmp[p])*math.sqrt( (u_int/x_int)*(u_int/x_int) + (u_sm/x_sm)*(u_sm/x_sm) )

    # Pruning: only save HEL params which have Ai > 0.001*max_Ai
    ai_pruned, u_ai_pruned = {}, {}
    max_ai = -1
    for p,ai in ai_tmp.iteritems():
      if abs(ai) > max_ai: max_ai = abs(ai)
    for p,ai in ai_tmp.iteritems():
      if abs(ai) > 0.0001*max_ai:
        ai_pruned[p] = ai
        u_ai_pruned[p] = u_ai_tmp[p]

    # Scaling: scale params which should be scaled and then add to final dict
    ai_final = {}
    u_ai_final = {}
    for param in pois:
      p, t = param['param'], param['title']
      # Check: term in pruned dictionary
      if p in ai_pruned:
        a = 1
        if 'divide_by' in param: a *= param['divide_by']
        ai_final[t] = ai_pruned[p]/a
        u_ai_final[t] = u_ai_pruned[p]/a
 
    # Add final Ai to overall dict for each bin
    Ai[ "%s_%s"%(var,Differential_bins[var][bin_idx]) ] = ai_final
    u_Ai[ "%s_%s"%(var,Differential_bins[var][bin_idx]) ] = u_ai_final

  #Return Ai and stat uncertainty
  return Ai, u_Ai 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR EXTRACTING BSM TERMS
def extract_Bij( process, pois, var, inputFile_sm, inputFile_bsm, ci=0.0001 ):
  
  # Check input yoda files exists
  for f in [inputFile_sm,inputFile_bsm]: 
    if not os.path.exists( f ):
      print " --> [ERROR] input file %s does not exist. Leaving..."%f
      leave()

  # Extract all opbjects from yoda files
  aos_sm = yoda.read( inputFile_sm )
  aos_bsm = yoda.read( inputFile_bsm )

  # Dictionary to store relevant histograms
  histDict = {}

  # Loop over EFT params and extract reweighted
  for param_i in pois: 
    histDict["bsm_%s"%param_i['param']] = aos_bsm[u'/RAW/HiggsTemplateCrossSections/%s[bsm_%s]'%(VariableToHistogramDict[var],param_i['param'])]
    for param_j in pois:
      if pois.index(param_i) < pois.index(param_j):
        histDict["bsm_%s%s"%(param_i['param'],param_j['param'])] = aos_bsm[u'/RAW/HiggsTemplateCrossSections/%s[bsm_%s%s]'%(VariableToHistogramDict[var],param_i['param'],param_j['param'])]
  # Also add SM
  histDict['sm'] = aos_sm[u'/RAW/HiggsTemplateCrossSections/%s[Weight_MERGING=0.000]'%VariableToHistogramDict[var]]

  # Calculate scaling factor: numEntries different in diff samples
  nEntries_bsm = float(histDict['bsm_cHW'].numEntries())
  nEntries_sm  = float(histDict['sm'].numEntries())
  sf = nEntries_sm/nEntries_bsm

  # Define Dicts to store Ai + unc
  Bij, u_Bij = {}, {}
  # Loop over bins in variable
  for bin_idx in range( len( Differential_bins[var] ) ):
  
    # Extract sm bin value
    x_sm = histDict['sm'].bins[bin_idx].sumW
    u_sm = math.sqrt( histDict['sm'].bins[bin_idx].sumW2 )

    # Define tmp dicts to store Ai terms (+stat unc)
    bij_tmp = {}
    u_bij_tmp = {}
 
    # Loop over params
    for param_i in pois:
      p_i = param_i['param']
      
      # Calculate squared Bij terms and add to dict
      x_bsm = histDict['bsm_%s'%p_i].bins[bin_idx].sumW
      u_bsm = math.sqrt( histDict['bsm_%s'%p_i].bins[bin_idx].sumW2 )
      bij_tmp[p_i] = sf*(x_bsm/(ci*ci*x_sm))
      if bij_tmp[p_i] == 0: u_bij_tmp[p_i] = 0
      else: u_bij_tmp[p_i] = abs(bij_tmp[p_i])*math.sqrt( (u_bsm/x_bsm)*(u_bsm/x_bsm) + (u_sm/x_sm)*(u_sm/x_sm) )

    # Calculate cross terms: for each parameter pair
    for param_i in pois:
      for param_j in pois:
        if pois.index(param_i) < pois.index(param_j):
          p_i, p_j = param_i['param'], param_j['param']
 
          # Calculate cross-term and add to dict
          x_bsm_ij = histDict["bsm_%s%s"%(p_i,p_j)].bins[bin_idx].sumW
          u_bsm_ij = math.sqrt( histDict["bsm_%s%s"%(p_i,p_j)].bins[bin_idx].sumW2 )
          bij_tilda = sf*(x_bsm_ij/(ci*ci*x_sm))
          u_bij_tilda = abs(bij_tilda)*math.sqrt( (u_bsm_ij/x_bsm_ij)*(u_bsm_ij/x_bsm_ij) + (u_sm/x_sm)*(u_sm/x_sm) )
          
          # Check: squared terms exist
          if( p_i in bij_tmp )&( p_j in bij_tmp ):
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

    # Pruning: only save HEL params which have Bij > 0.0000001*max_Bij
    bij_pruned, u_bij_pruned = {}, {}
    max_bij = -1
    for p,bij in bij_tmp.iteritems():
      if abs(bij) > max_bij: max_bij = abs(bij)
    for p,bij in bij_tmp.iteritems():
      if abs(bij) > 0.0000001*max_bij:
        bij_pruned[p] = bij
        u_bij_pruned[p] = u_bij_tmp[p]

    # Scaling: scale params which should be scaled and then add to final dict
    bij_final = {}
    u_bij_final = {}
    # Squared terms
    for param_i in pois:
      p_i, t_i = param_i['param'], param_i['title']
      # Check: term in pruned dictionary
      if p_i in bij_pruned:
        a = 1
        if 'divide_by' in param_i: a *= param_i['divide_by']*param_i['divide_by']
        bij_final[t_i] = bij_pruned[p_i]/a
        u_bij_final[t_i] = u_bij_pruned[p_i]/a

    # Cross terms
    for param_i in pois:
      for param_j in pois:
        if pois.index(param_i) < pois.index(param_j):
          p_i, t_i = param_i['param'], param_i['title']
          p_j, t_j = param_j['param'], param_j['title']
          # Check: term in pruned dict
          if "%s%s"%(p_i,p_j) in bij_pruned:
            a = 1
            if 'divide_by' in param_i: a*=param_i['divide_by']
            if 'divide_by' in param_j: a*=param_j['divide_by']
            bij_final["%s%s"%(t_i,t_j)] = bij_pruned["%s%s"%(p_i,p_j)]/a
            u_bij_final["%s%s"%(t_i,t_j)] = u_bij_pruned["%s%s"%(p_i,p_j)]/a 

    # Add final Bij to overall dict for each bin
    Bij[ "%s_%s"%(var,Differential_bins[var][bin_idx]) ] = bij_final
    u_Bij[ "%s_%s"%(var,Differential_bins[var][bin_idx]) ] = u_bij_final

  #Return Bij and stat uncertabsmy
  return Bij, u_Bij 

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR OUTPUTTING SCALING FUNCTIONS AS TEXT
def sf2text( process, pois, var, ai_matrix, bij_matrix, linearOnly=True ):
  print ""
  print "~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
  print " --> SCALING FUNCTIONS FOR: * process = %s"%process
  print "                            * variable = %s"%var
  print ""

  # Loop over bins in differential dist
  for d_bin in Differential_bins[var]:

    # Construct line
    line = '1'
    # Loop over HEL parameters and extract Ai for specific bin
    for param in pois:
      t = param['title']
      if t in ai_matrix[process]["%s_%s"%(var,d_bin)]:
        ai = ai_matrix[process]["%s_%s"%(var,d_bin)][t]
        sign = "+" if ai>=0 else "-"
        if sign == "-": line += ' %s%.3f * %s'%(sign,abs(ai),t)
        else: line += ' %s %.3f * %s'%(sign,abs(ai),t)

    if not linearOnly:

      # Loop over parameters (and pairs) and extract Bij for specific bin
      for param_i in pois:
        t_i = param_i['title']
        if t_i in bij_matrix[process]["%s_%s"%(var,d_bin)]:
          bij = bij_matrix[process]["%s_%s"%(var,d_bin)][t_i]
          sign = "+" if bij>=0 else "-"
          if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_i)
          else: line += ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_i)

      for param_i in pois:
        for param_j in pois:
          if pois.index(param_i) < pois.index(param_j):
            t_i, t_j = param_i['title'], param_j['title']
            # Ignore CP odd * CP even cross terms
            if((t_i[0]=="t")&(t_j[0]!="t"))|((t_i[0]!="t")&(t_j[0]=="t")): continue
            if "%s%s"%(t_i,t_j) in bij_matrix[process]["%s_%s"%(var,d_bin)]:
              bij = bij_matrix[process]["%s_%s"%(var,d_bin)]["%s%s"%(t_i,t_j)]
              sign = "+" if bij>=0 else "-"
              if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_j)
              else: line += ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_j)

    # Print to screen
    print "   --> %s_%s = %s"%(var,d_bin,line)

  print "~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
  print ""
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# FUNCTION FOR WRITING OUT EQUATIONS IN FORMAT TO BE READ BY COMBINE
def sf2combine( processes, pois, var, ai_matrix, bij_matrix, linearOnly=True ):

  if not os.path.isdir("./output"): os.system("mkdir ./output")

  #Open file to write to
  if linearOnly: f_out = open("output/%s_interference_only.txt"%var,"w")
  else: f_out = open("output/%s.txt"%var,"w")

  equations = []

  # Loop over bins in differental
  for d_bin in Differential_bins[var]:

    key = "%s_%s"%(var,d_bin)

    # Loop over processes
    for process in processes.split(","):

      # Construct line
      line = '1'
      # Loop over HEL parameters and extract Ai for specific bin
      for param in pois:
        t = param['title']
        # Ignore CP conjugate terms
        if t in ai_matrix[process][key]:
          ai = ai_matrix[process][key][t]
          t = re.sub('\'','',t)
          sign = "+" if ai>=0 else "-"
          if sign == "-": line += ' %s%.3f * %s'%(sign,abs(ai),t)
          else: line += ' %s %.3f * %s'%(sign,abs(ai),t)

      if not linearOnly:

        # Loop over parameters (and pairs) and extract Bij for specific bin
        for param_i in pois:
          t_i = param_i['title']
          if t_i in bij_matrix[process][key]:
            bij = bij_matrix[process][key][t_i]
            t_i = re.sub('\'','',t_i)
            sign = "+" if bij>=0 else "-"
            if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_i)
            else: line += ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_i)

        for param_i in pois:
          for param_j in pois:
            if pois.index(param_i) < pois.index(param_j):
              t_i, t_j = param_i['title'], param_j['title']
              # Ignore CP odd * CP even cross terms
              if((t_i[0]=="t")&(t_j[0]!="t"))|((t_i[0]!="t")&(t_j[0]=="t")): continue
              if "%s%s"%(t_i,t_j) in bij_matrix[process][key]:
                bij = bij_matrix[process][key]["%s%s"%(t_i,t_j)]
                t_i = re.sub('\'','',t_i)
                t_j = re.sub('\'','',t_j)
                sign = "+" if bij>=0 else "-"
                if sign == "-": line += ' %s%.4f * %s * %s'%(sign,abs(bij),t_i,t_j)
                else: line += ' %s %.4f * %s * %s'%(sign,abs(bij),t_i,t_j)

      # Write out line to file
      f_out.write("%s_%s:%s\n"%(proc,key,line))

  # Close file
  f_out.close()

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# MAIN PROGRAM
if __name__ == "__main__":
  print "~~~~~~~~~~~~~~~~~~~~~~~~~~ OBS2EFT: (extract scale functions)  ~~~~~~~~~~~~~~~~~~~~~~~~~~"

  print " --> PROCESSES: %s"%opt.processes
  print " --> VARIABLE:  %s"%opt.variable

  if opt.freezeOtherParameters: parametersOfInterest = HEL_parameters_subset
  else: parametersOfInterest = HEL_parameters

  # Loop over proceeses and store Ai(+unc) and Bij(+unc)
  Ai_matrix, u_Ai_matrix = {}, {}
  Bij_matrix, u_Bij_matrix = {}, {}
  for proc in opt.processes.split(","):

    # SM
    f_sm = "../../Events/%s_sm/yoda/%s_sm.yoda"%(proc,proc)
    # Interference (Ai)
    f_int = "../../Events/%s_int/yoda/%s_int.yoda"%(proc,proc)
    # BSM (Bij)
    f_bsm = "../../Events/%s_bsm/yoda/%s_bsm.yoda"%(proc,proc)

    Ai_matrix[proc], u_Ai_matrix[proc] = extract_Ai( proc, parametersOfInterest, opt.variable, f_sm, f_int )
    if not opt.linearOnly: Bij_matrix[proc], u_Bij_matrix[proc] = extract_Bij( proc, parametersOfInterest, opt.variable, f_sm, f_bsm )

    if opt.textOutput: sf2text( proc, parametersOfInterest, opt.variable, Ai_matrix, Bij_matrix, linearOnly=opt.linearOnly )  

  if opt.combineOutput: sf2combine( proc, parametersOfInterest, opt.variable, Ai_matrix, Bij_matrix, linearOnly=opt.linearOnly )  

  # Finished
  leave( exit=False )
