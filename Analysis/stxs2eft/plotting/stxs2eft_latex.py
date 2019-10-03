import os
import re
import math

vbf_stage1_1_set1 = ["QQ2HQQ_FWDH","QQ2HQQ_0J","QQ2HQQ_1J","QQ2HQQ_GE2J_MJJ_0_60","QQ2HQQ_GE2J_MJJ_60_120","QQ2HQQ_GE2J_MJJ_120_350","QQ2HQQ_GE2J_MJJ_GT350_PTH_GT200"]
vbf_stage1_1_set2 = ["QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_0_25","QQ2HQQ_GE2J_MJJ_350_700_PTH_0_200_PTHJJ_GT25","QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_0_25","QQ2HQQ_GE2J_MJJ_GT700_PTH_0_200_PTHJJ_GT25"]

# Function to convert Ai terms to latex format
def sf2latex( stage, processes, ai_matrix, bij_matrix, stxs_bins, eft_parameters, procToSTXSProductionModeMap, mode="Ai", vbf_split="", verbose=False ):

  # Open file to write to
  if not os.path.isdir("./latex"): os.system("mkdir latex")
  proc_str = "_".join(processes.split(","))
  fout = open("latex/tab_%s_stage%s_%s%s.txt"%(mode,stage,proc_str,vbf_split),"w")

  # Size of column box
  if stage == "0": colbox = "0.7"
  elif stage == "1": colbox = "0.5"
  elif stage == "1_1": 
    colbox = "0.45"
    if "ggh" in processes: colbox = "0.3"
    if "vbf" in processes: colbox = "0.4"
    elif "zh" in processes: colbox = "0.6"

  stage_str = stage
  if stage_str == "1_1": stage_str = "1.1"

  # Determine caption string
  caption_str = ""
  if mode == "Ai": caption_str += "$A_j$ coefficients for the "
  elif mode == "Bij": caption_str += "$B_{jk}$ coefficients for the "
  if stage != "0":
    Nprocs = len(processes.split(","))
    if Nprocs == 1: caption_str += "\\%s "%processes.split(",")[0]
    else:
      for proc_idx in range(Nprocs):
        proc = processes.split(",")[proc_idx]
        if proc_idx == (Nprocs-1): caption_str = caption_str[:-2] +" and \\%s "%proc
        else: caption_str += "\\%s, "%proc
  caption_str += "STXS Stage %s bins."%stage_str

  # Determine label string
  label_str = "stage%s_%s_%s"%(stage,mode,proc_str)


  # Print preamble
  if stage == "1_1": fout.write("\\begin{landscape}\n")
  fout.write("\\begin{table}[htb]\n")
  fout.write("    \\centering\n")
  fout.write("    \\setlength\\extrarowheight{3pt}\n")
  fout.write("    \\setlength\\tabcolsep{10pt}\n")
  fout.write("    \\begin{tabular}{|c|c|}\n")
  fout.write("        \\hline\n")
  if mode == "Ai": fout.write("        STXS region (stage %s) & $A_{j}$ \\\\ \\hline\n"%(stage_str))
  elif mode == "Bij": fout.write("        STXS region (stage %s) & $B_{jk}$ \\\\ \\hline\n"%(stage_str))

  if verbose:
    print "\\begin{table}[htb]"
    print "    \\centering"
    print "    \\setlength\\extrarowheight{3pt}"
    print "    \\setlength\\tabcolsep{10pt}"
    print "    \\begin{tabular}{|c|c|}"
    print "        \\hline"
    if mode == "Ai": print "        STXS region (stage %s) & $A_{j}$ \\\\ \\hline"%(stage_str)
    elif mode == "Bij": print "        STXS region (stage %s) & $B_{jk}$ \\\\ \\hline"%(stage_str)

  for process in processes.split(","):

    if verbose: print "        & \\\\"
    fout.write("        & \\\\\n")
    # Loop over STXS bins relative to process
    s = "stage%s"%stage
    for stxs_bin in stxs_bins[s]:
      if stxs_bin.split("_")[0] == procToSTXSProductionModeMap[process]:

        # For splitting VBF bin (stage 1.1) in separate tables
        skip_vbf = False
        if process == "vbf":
          if vbf_split == "set1":
            if stxs_bin in vbf_stage1_1_set2: skip_vbf = True 
          elif vbf_split == "set2":
            if stxs_bin in vbf_stage1_1_set1: skip_vbf = True
        if skip_vbf: continue

        if "FWDH" in stxs_bin: continue
      
        # Format STXS bin title
        proc = stxs_bin.split("_")[0]
        detail = "_".join(stxs_bin.split("_")[1:])

        # STXS Production mode
        proc = re.sub("GG2H","$\\cPg\\cPg\\Rightarrow\\PH$",proc)
        proc = re.sub("QQ2HQQ","$\\cPq\\cPq\\Rightarrow\\PH\\cPq\\cPq$",proc)
        proc = re.sub("QQ2HLNU","$\\cPq\\cPq\\Rightarrow\\PH\\ell\\NU$",proc)
        proc = re.sub("QQ2HLL","$\\cPq\\cPq\\Rightarrow\\PH\\ell\\ell$",proc)
        proc = re.sub("TTH","$\\cPg\\cPg/\\cPq\\cPq\\Rightarrow\\cPqt\\cPqt\\PH$",proc)

        # Detail
        detail_str = ""
        # First deal with VBFTOPO in stage 1
        if "VBFTOPO" in detail: 
          detail_str += "\\vbf-like, "
          if "JET3VETO" in detail: detail_str += "$p_{\\text{T}}^{\PH jj} < 25$~GeV"
          else: detail_str += "$p_{\\text{T}}^{\PH jj} \\geq 25$~GeV"

        # Now deal with special stage 1 VBF definitions
        elif "VH2JET" in detail: detail_str += "60~$\\leq m_{jj} < 120$~GeV"
        elif "REST" in detail: detail_str += "rest"
        else:
          # Jet multiplicity
          if 'GE2J' in detail:
            detail_str += "$\geq$2-jet, "
            detail = re.sub("_GE2J","",detail)
            detail = re.sub("GE2J_","",detail)
          elif 'GE1J' in detail:
            detail_str += "$\geq$1-jet, "
            detail = re.sub("_GE1J","",detail)
            detail = re.sub("GE1J_","",detail)
          elif '1J' in detail:
            detail_str += "1-jet, "
            detail = re.sub("_1J","",detail)
            detail = re.sub("1J_","",detail)
          elif '0J' in detail:
            detail_str += "0-jet, "
            detail = re.sub("_0J","",detail)
            detail = re.sub("0J_","",detail)

          # Split up remaining elements by "_"
          detail = detail.split("_") 
   
          #Kinematic
          kin2latex = {"PTJET1":"p_{\\text{T}}^{j1}","PTV":"p_{\\text{T}}^{\\rm{V}}","PTH":"p_{\\text{T}}^{\\PH}","MJJ":"m_{jj}","PTHJJ":"p_{\\text{T}}^{\\PH jj}"}
          for kinematic in ['PTJET1','PTV','PTH','MJJ','PTHJJ']:
            if kinematic in detail:
              kin_idx = detail.index(kinematic)
              if "GT" in detail[kin_idx+1]: 
                v = re.sub("GT","",detail[kin_idx+1])
                detail_str += "$%s \\geq %s$~GeV, "%(kin2latex[kinematic],v)
              else:
                lv = detail[kin_idx+1]
                hv = detail[kin_idx+2]
                if lv == "0": detail_str += "$%s < %s$~GeV, "%(kin2latex[kinematic],hv)
                else: detail_str += "%s~$\\leq %s < %s$~GeV, "%(lv,kin2latex[kinematic],hv)

          if detail_str[-2:] == ", ": detail_str = detail_str[:-2]
          
        # Ai terms
        ai_str = "$"
        for param in eft_parameters:
          t = param['title']
          if t in ai_matrix[process][stxs_bin]:
            ai = ai_matrix[process][stxs_bin][t]
            sign = "+" if ai>=0 else "-"
            if "\'" in t:
              t = re.sub("\'","",t)
              ai *= 157.913670416
            i = t.split("c")[-1]
            if abs(ai) > 1e3: 
              ai_exp = int(math.log(abs(ai),10))
              ai_scaled = abs(ai)/math.pow(10,ai_exp)
              ai_str += "%s %.3g\\times10^{%g}\\:c_{%s} "%(sign,abs(ai_scaled),ai_exp,i)
            elif abs(ai) < 1e-2: 
              ai_exp = int(math.log(abs(ai),10))-1
              ai_scaled = abs(ai)/math.pow(10,ai_exp)
              ai_str += "%s %.3g\\times10^{%g}\\:c_{%s} "%(sign,abs(ai_scaled),ai_exp,i)
            else: ai_str += "%s %.3g\\:c_{%s} "%(sign,abs(ai),i)

        #Formatting
        if ai_str[:3] == "$+ ": ai_str = "$"+ai_str[3:]
        if ai_str[:3] == "$- ": ai_str = "$-"+ai_str[3:]
        ai_str = ai_str[:-1]+"$"

        # Bij terms
        bij_str = "$"
        #Squared terms
        for param_i in eft_parameters:
          t_i = param_i['title']
          if t_i in bij_matrix[process][stxs_bin]:
            bij = bij_matrix[process][stxs_bin][t_i]
            sign = "+" if bij>=0 else "-"
            if "\'" in t_i:
              t_i = re.sub("\'","",t_i)
              bij *= 157.913670416*157.913670416
            i = t_i.split("c")[-1]
            if abs(bij) > 1e3:
              bij_exp = int(math.log(abs(bij),10))
              bij_scaled = abs(bij)/math.pow(10,bij_exp)
              bij_str += "%s %.3g\\times10^{%g}\\:c_{%s}\\,\\!^{2} "%(sign,abs(bij_scaled),bij_exp,i)
            elif abs(bij) < 1e-2:
              bij_exp = int(math.log(abs(bij),10))-1
              bij_scaled = abs(bij)/math.pow(10,bij_exp)
              bij_str += "%s %.3g\\times10^{%g}\\:c_{%s}\\,\\!^{2} "%(sign,abs(bij_scaled),bij_exp,i)
            else: bij_str += "%s %.3g\\:c_{%s}\\,\\!^{2} "%(sign,abs(bij),i)

        for param_i in eft_parameters:
          for param_j in eft_parameters:
            if eft_parameters.index(param_i) < eft_parameters.index(param_j):
              t_i, t_j = param_i['title'], param_j['title']
              if "%s%s"%(t_i,t_j) in bij_matrix[process][stxs_bin]:
                bij = bij_matrix[process][stxs_bin]["%s%s"%(t_i,t_j)]
                sign = "+" if bij>=0 else "-"
                if "\'" in t_i:
                  t_i = re.sub("\'","",t_i)
                  bij *= 157.913670416
                if "\'" in t_j:
                  t_j = re.sub("\'","",t_j)
                  bij *= 157.913670416
                i = t_i.split("c")[-1]
                j = t_j.split("c")[-1]
                if abs(bij) > 1e3:
                  bij_exp = int(math.log(abs(bij),10))
                  bij_scaled = abs(bij)/math.pow(10,bij_exp)
                  bij_str += "%s %.3g\\times10^{%g}\\:c_{%s}\\,c_{%s} "%(sign,abs(bij_scaled),bij_exp,i,j)
                elif abs(bij) < 1e-2:
                  bij_exp = int(math.log(abs(bij),10))-1
                  bij_scaled = abs(bij)/math.pow(10,bij_exp)
                  bij_str += "%s %.3g\\times10^{%g}\\:c_{%s}\\,c_{%s} "%(sign,abs(bij_scaled),bij_exp,i,j)
                else: bij_str += "%s %.3g\\:c_{%s}\\,c_{%s} "%(sign,abs(bij),i,j)
   
        # Formatting
        if bij_str[:3] == "$+ ": bij_str = "$"+bij_str[3:]
        if bij_str[:3] == "$- ": bij_str = "$-"+bij_str[3:]
        bij_str = bij_str[:-1]+"$"

        # Print to screen
        if mode == "Ai":
          if detail_str == "": 
            if verbose: print "        %s & \\parbox{%s\\columnwidth}{%s} \\\\"%(proc,colbox,ai_str)
            fout.write("        %s & \\parbox{%s\\columnwidth}{%s} \\\\\n"%(proc,colbox,ai_str))
          else: 
            if verbose: print "        %s (%s) & \\parbox{%s\\columnwidth}{%s} \\\\"%(proc,detail_str,colbox,ai_str)
            fout.write("        %s (%s) & \\parbox{%s\\columnwidth}{%s} \\\\\n"%(proc,detail_str,colbox,ai_str))
        elif mode == "Bij":
          if detail_str == "": 
            if verbose: print "        %s & \\parbox{%s\\columnwidth}{%s} \\\\"%(proc,colbox,bij_str)
            fout.write("        %s & \\parbox{%s\\columnwidth}{%s} \\\\\n"%(proc,colbox,bij_str))
          else: 
            if verbose: print "        %s (%s) & \\parbox{%s\\columnwidth}{%s} \\\\"%(proc,detail_str,colbox,bij_str)
            fout.write("        %s (%s) & \\parbox{%s\\columnwidth}{%s} \\\\\n"%(proc,detail_str,colbox,bij_str))

        if verbose: print "        & \\\\"
        fout.write("        & \\\\\n")

    if verbose: print "        \\hline" 
    fout.write("        \\hline\n" )

  # END OF LOOP OVER PROCESSES
  if verbose:
    print "    \\end{tabular}"
    print "    \\caption{Add caption here}"
    print "    \\label{tab:add_label_here}"
    print "\\end{table}"
  fout.write("    \\end{tabular}\n")
  fout.write("    \\caption{%s}\n"%caption_str)
  fout.write("    \\label{tab:%s}\n"%label_str)
  fout.write("\\end{table}\n")
  if stage == "1_1": fout.write("\\end{landscape}\n")
  fout.write("\n")

  fout.close()

  # REPLACE TROUBLESOME STRINGS IN OUTFILE
  os.system("sed -i \'s/Rightarrow/rightarrow/g\' latex/tab_%s_stage%s_%s%s.txt"%(mode,stage,proc_str,vbf_split))
  os.system("sed -i \'s/NU/nu/g\' latex/tab_%s_stage%s_%s%s.txt"%(mode,stage,proc_str,vbf_split))

