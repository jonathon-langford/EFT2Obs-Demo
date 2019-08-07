import ROOT
import os
import math

# Function to plot Ai comparison: wg1 note and stxs2eft
def plot_Ai_comparison( outDir, stage, process, ai_matrix_base, ai_matrix_new, u_ai_matrix_new, stxs_bins, eft_parameters, procToSTXSProductionModeMap, verbose=False ):

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # CHECKS
  # Only configured for stage 1: return 0 if not 
  if stage != '1':
    print " --> [WARNING] Comparison plots only configured for stage 1. Will NOT plot for %s"%process
    return 0
  # Check output dir exists:
  if not os.path.isdir( outDir ): 
    print " --> [WARNING] Output directory (%s) does not exist. Will NOT plot for %s"%(outDir,process)
    return 0
  # Make directory for process: if already exists then ask user if they want to overwrite
  if os.path.isdir( "%s/%s"%(outDir,process) ):
    overwrite = input(" --> [INPUT] Output directory for process %s already exists. Do you want to overwrite plots [1=yes,0=no]:"%process)
    if not overwrite:
      print " --> Will NOT plot for %s"%process
      return 0
  else: os.system("mkdir %s/%s"%(outDir,process))
  
  print " --> Plotting Ai comparison plots for %s. Output directory: %s/%s"%(process,outDir,process)

  # Global settings
  ROOT.gStyle.SetOptStat(0)
  ROOT.gROOT.SetBatch(ROOT.kTRUE) #suppress output to screen
  procColorMap = {"ggh":862,"vbf":807,"wh":418,"zh":413,"tth":616}

  #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
  # Loop over STXS bins relevant to process
  s = "stage%s"%stage
  for stxs_bin in stxs_bins[s]:
    if stxs_bin.split("_")[0] == procToSTXSProductionModeMap[process]:

      #IGNORE FWDH bins
      if "FWDH" in stxs_bin: continue

      if verbose:
        print "  ~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
        print "  --> STXS bin: %s"%stxs_bin
        print ""
      
      # Determine set of eft params in Ai matrices
      params = []
      for param in eft_parameters:
        t = param['title']
        # Not interested in CP conjugate coeff for now...
        if t[0] != 't':
          if( t in ai_matrix_base[process][stxs_bin] )|( t in ai_matrix_new[process][stxs_bin] ): params.append(t)

      # Create TCanvas and pads
      canv = ROOT.TCanvas("canv_%s"%stxs_bin,"canv_%s"%stxs_bin) 
      pad1 = ROOT.TPad("pad1_%s"%stxs_bin,"",0,0.4,1,0.9)
      pad1.SetLogy()
      pad1.SetTopMargin(0)
      pad1.SetBottomMargin(0.01)
      pad2 = ROOT.TPad("pad2_%s"%stxs_bin,"",0,0,1,0.38)
      pad2.SetTopMargin(0.01)
      pad2.SetBottomMargin(0.15)
      pad1.Draw()
      pad2.Draw()

      # |Ai distribution|
      pad1.cd()
      # Define histogram for axes: bins = number of params
      h_axes = ROOT.TH1F("h_axes_%s"%stxs_bin,"",len(params),0,len(params))
      for i in range(1,h_axes.GetNbinsX()+1): h_axes.GetXaxis().SetBinLabel(i,params[i-1])
      h_axes.GetXaxis().SetLabelSize(0)
      h_axes.GetYaxis().SetTitle("|A_{i}|")
      h_axes.GetYaxis().SetTitleSize(0.08)
      h_axes.GetYaxis().SetLabelSize(0.07)
      h_axes.GetYaxis().SetTitleOffset(0.5)
      h_axes.GetYaxis().CenterTitle()
      
      # Determine bin centers for base and new
      Xbincentre_base = []
      Xbincentre_new = []
      for _bin in range(1,len(params)+1):
        Xbincentre_base.append(h_axes.GetXaxis().GetBinCenter(_bin)-0.07)
        Xbincentre_new.append(h_axes.GetXaxis().GetBinCenter(_bin)+0.07)

      # Save max/min value of points (A+stat unc for new)
      max_ai = 20
      min_ai = 1

      # Create TGraph for base points
      gr_base = ROOT.TGraph()
      gr_base.SetMarkerStyle(21)
      gr_base.SetMarkerSize(1.5)
      gr_base.SetMarkerColor(1)
      p = 0
      for j in range(len(params)):
        if params[j] in ai_matrix_base[process][stxs_bin]: 
          gr_base.SetPoint(p,Xbincentre_base[j],abs(ai_matrix_base[process][stxs_bin][params[j]]))
          p+=1
          # Set max/min
          if abs(ai_matrix_base[process][stxs_bin][params[j]]) < min_ai: min_ai = abs(ai_matrix_base[process][stxs_bin][params[j]])
          if abs(ai_matrix_base[process][stxs_bin][params[j]]) > max_ai: max_ai = abs(ai_matrix_base[process][stxs_bin][params[j]])

      # Create TGraph with errors for new points
      gr_new = ROOT.TGraphAsymmErrors()
      gr_new.SetMarkerStyle(23)
      gr_new.SetMarkerSize(1.5)
      gr_new.SetMarkerColor(procColorMap[process])
      gr_new.SetLineColor(procColorMap[process])
      gr_new.SetLineWidth(3)
      p = 0
      for j in range(len(params)):
        if params[j] in ai_matrix_new[process][stxs_bin]:
          gr_new.SetPoint(p,Xbincentre_new[j],abs(ai_matrix_new[process][stxs_bin][params[j]]))
          gr_new.SetPointError(p,0,0,u_ai_matrix_new[process][stxs_bin][params[j]],u_ai_matrix_new[process][stxs_bin][params[j]])
          p+=1
          # Set max/min
          if abs(ai_matrix_new[process][stxs_bin][params[j]]) < min_ai: min_ai = abs(ai_matrix_new[process][stxs_bin][params[j]])
          if (abs(ai_matrix_new[process][stxs_bin][params[j]])+u_ai_matrix_new[process][stxs_bin][params[j]]) > max_ai: max_ai = abs(ai_matrix_new[process][stxs_bin][params[j]])+u_ai_matrix_new[process][stxs_bin][params[j]]
        
      # Set minimum and maximum in y-axis
      max_ai = math.pow(10,math.log(5*max_ai,10))
      if math.pow(10,int(math.log(min_ai))-1) < 0.001: min_ai = 0.00101
      else: min_ai = math.pow(10,int(math.log(min_ai))-1)
      h_axes.SetMaximum(max_ai)
      h_axes.SetMinimum(min_ai)

      # Draw in pad1
      h_axes.Draw()
      gr_base.Draw("Same P")
      gr_new.Draw("Same P")

      # Draw a line for each param
      lines = {}
      for j in range(1,len(params)):
        key = "line_%g"%j
        lines[key] = ROOT.TLine(j,min_ai,j,max_ai)
        lines[key].SetLineWidth(1)
        lines[key].SetLineStyle(4)
        lines[key].Draw("Same")

      # Loop over points: if val below minimum then draw an arrow
      arrows = {}
      for p in range(gr_new.GetN()):
        ai = gr_new.GetY()[p]
        x = gr_new.GetX()[p]
        if ai < min_ai:
          key = "arrow_%g"%p
          arrows[key] = ROOT.TArrow(x,0.005,x,0.0011,0.03,"|>")
          arrows[key].SetAngle(40)
          arrows[key].SetLineWidth(2)
          arrows[key].SetFillColor(procColorMap[process])
          arrows[key].Draw()
      for p in range(gr_base.GetN()):
        ai = gr_base.GetY()[p]
        x = gr_base.GetX()[p]
        if ai < min_ai:
          key = "arrow_%g"%p
          arrows[key] = ROOT.TArrow(x,0.005,x,0.0011,0.03,"|>")
          arrows[key].SetAngle(40)
          arrows[key].SetLineWidth(2)
          arrows[key].SetFillColor(1)
          arrows[key].Draw()


      # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      # RATIO PLOT
      pad2.cd()

      # Define histogram for axes: bins = number of params
      h_ratio_axes = ROOT.TH1F("h_ratio_axes_%s"%stxs_bin,"",len(params),0,len(params))
      for i in range(1,h_ratio_axes.GetNbinsX()+1): h_ratio_axes.GetXaxis().SetBinLabel(i,params[i-1])
      h_ratio_axes.GetXaxis().SetLabelSize(0.15)
      h_ratio_axes.GetXaxis().SetLabelOffset(0.01)
      #h_ratio_axes.GetXaxis().SetLabelOffset(0.2)
      h_ratio_axes.GetYaxis().SetTitle("Ratio")
      h_ratio_axes.GetYaxis().SetTitleSize(0.09)
      h_ratio_axes.GetYaxis().SetLabelSize(0.08)
      h_ratio_axes.GetYaxis().SetTitleOffset(0.5)
      h_ratio_axes.GetYaxis().CenterTitle()

      # Get bin centres to plot
      Xbincentre_ratio = []
      for _bin in range(1,len(params)+1): Xbincentre_ratio.append(h_axes.GetXaxis().GetBinCenter(_bin))

      # Save min/max if more extreme than nominal
      max_ratio = 1.1
      min_ratio = 0.9

      # Define lists to save param idx which cannot calc ratio
      base_only = []
      new_only = []
      
      # Create TGraph with errors for ratios
      gr_ratio = ROOT.TGraphAsymmErrors()
      gr_ratio.SetLineColor(procColorMap[process])
      gr_ratio.SetLineWidth(3)
      p = 0
      for j in range(len(params)):
        if( params[j] in ai_matrix_base[process][stxs_bin] )&( params[j] in ai_matrix_new[process][stxs_bin] ):
          r = ai_matrix_new[process][stxs_bin][params[j]]/ai_matrix_base[process][stxs_bin][params[j]]
          u_r = u_ai_matrix_new[process][stxs_bin][params[j]]/abs(ai_matrix_base[process][stxs_bin][params[j]])
          gr_ratio.SetPoint(p,Xbincentre_ratio[j],r)
          gr_ratio.SetPointError(p,0,0,u_r,u_r)
          p+=1

          # if verbose option, print ratios
          if verbose: print "     * %s : ratio = %5.4f +- %5.4f"%(params[j],r,u_r)

          # Set max/min
          if r+u_r > max_ratio: max_ratio = 1.1*(r+u_r)
          if r-u_r < min_ratio: 
            if r-u_r < 0: min_ratio = 1.1*(r-u_r)
            else: min_ratio = r-u_r-0.2

        # Else add bin to lists
        elif ( params[j] in ai_matrix_base[process][stxs_bin] ):
          base_only.append(j)
          if verbose: print "     * %s : ratio = N/A (no value in WG1 note)"%params[j]
        else: 
          new_only.append(j)
          if verbose: print "     * %s : ratio = N/A (no value in WG1 note)"%params[j]

      # Set minimum and maximum in y-axis: symmetric
      if (max_ratio-1) > abs(min_ratio-1): min_ratio = 1-(max_ratio-1)
      else: max_ratio = 1+abs(min_ratio-1)
      # Maximum allowed [-.5 to 2.5]
      if max_ratio > 2.5: max_ratio = 2.49
      if min_ratio < -0.5: min_ratio = -0.5
      h_ratio_axes.SetMaximum(max_ratio)
      h_ratio_axes.SetMinimum(min_ratio)
 
      h_ratio_axes.Draw()
      gr_ratio.Draw("Same P")

      #Draw lines on the ratio plot
      line_1 = ROOT.TLine(0,1,h_ratio_axes.GetXaxis().GetXmax(),1)
      line_1.SetLineWidth(3)
      line_1.SetLineStyle(2)
      line_1.Draw()
      if min_ratio < 0:
        line_2 = ROOT.TLine(0,0,h_ratio_axes.GetXaxis().GetXmax(),0)
        line_2.SetLineWidth(2)
        line_2.Draw()

      #Draw shaded boxes for when cannot calculate ratio
      empty_bins = {}
      for j in base_only:
        key = "base_%g"%j
        empty_bins[key] = ROOT.TBox( Xbincentre_ratio[j]-0.15, min_ratio, Xbincentre_ratio[j]+0.15, max_ratio)
        empty_bins[key].SetFillColor(1)
        empty_bins[key].SetFillStyle(3344)
        empty_bins[key].Draw("Same")
      for j in new_only:
        key = "new_%g"%j
        empty_bins[key] = ROOT.TBox( Xbincentre_ratio[j]-0.15, min_ratio, Xbincentre_ratio[j]+0.15, max_ratio)
        empty_bins[key].SetFillColor(procColorMap[process])
        empty_bins[key].SetFillStyle(3344)
        empty_bins[key].Draw("Same")

      # Draw a line for each param
      lines_ratio = {}
      for j in range(1,len(params)):
        key = "line_r%g"%j
        lines_ratio[key] = ROOT.TLine(j,min_ratio,j,max_ratio)
        lines_ratio[key].SetLineWidth(1)
        lines_ratio[key].SetLineStyle(4)
        lines_ratio[key].Draw("Same")

      # Loop over points: if ratio outside of range then draw an arrow
      arrows_ratio = {}
      for p in range(gr_ratio.GetN()):
        r = gr_ratio.GetY()[p]
        x = gr_ratio.GetX()[p]
        if r > max_ratio:
          key = "arrow_r%g"%p
          arrows_ratio[key] = ROOT.TArrow(x,0.75*max_ratio,x,0.98*max_ratio,0.03,"|>")
          arrows_ratio[key].SetAngle(40)
          arrows_ratio[key].SetLineWidth(2)
          arrows_ratio[key].SetFillColor(procColorMap[process])
          arrows_ratio[key].Draw()
        elif r < min_ratio:
          key = "arrow_r%g"%p
          arrows_ratio[key] = ROOT.TArrow(x,min_ratio+0.2*(max_ratio-min_ratio),x,min_ratio+0.01,0.03,"|>")
          arrows_ratio[key].SetAngle(40)
          arrows_ratio[key].SetLineWidth(2)
          arrows_ratio[key].SetFillColor(procColorMap[process])
          arrows_ratio[key].Draw()
          
      # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
      # Add text to canvas and update
      canv.cd() 

      lat = ROOT.TLatex()
      lat.SetTextFont(42)
      lat.SetLineWidth(2)
      lat.SetTextAlign(11)
      lat.SetNDC()
      lat.SetTextSize(0.042)
      #lat.DrawLatex(0.1,0.92,"#bf{STXStoEFT} #scale[0.75]{#it{Working progress}}")
      lat.DrawLatex(0.1,0.92,"#scale[0.75]{#bf{%s}}"%stxs_bin)
      #lat.DrawLatex(0.6,0.5,"#scale[0.75]{%s}"%stxs_bin)

      # Add legend to plot
      leg = ROOT.TLegend(0.5,0.91,0.9,0.97)
      leg.SetFillColor(0)
      leg.SetLineColor(0)
      leg.SetNColumns(2)
      leg.AddEntry(gr_base,"LHCHXSWG-INT-2017-001","P")
      leg.AddEntry(gr_new,"STXStoEFT","P")
      leg.Draw("Same")

      # Save canvas and close
      canv.Update()
      canv.SaveAs("%s/%s/%s_Ai_cmp.png"%(outDir,process,stxs_bin))
      canv.SaveAs("%s/%s/%s_Ai_cmp.pdf"%(outDir,process,stxs_bin))
      canv.Close() 

      if verbose:
        print "  ~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~@~"
        print ""


  #END OF LOOP OVER STXS BINS

#END OF FUNCTION 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
   
