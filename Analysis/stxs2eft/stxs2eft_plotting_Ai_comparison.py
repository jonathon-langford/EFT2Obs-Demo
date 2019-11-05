import ROOT
import os
import math
from optparse import OptionParser
import glob
import pickle

# Import dicts storing STXS processes and EFT coeff.
from STXS import STXS_bins
from EFT import HEL_parameters, HEL_parameters_subset

# Import Ai matrix and Bij matrix from WG1 note
from wg1_note.stage1_Ai import Ai_matrix_wg1

def get_options():
  parser = OptionParser()
  parser.add_option('--process', dest='process', default='ggh', help="Signal process")
  parser.add_option('--extensions', dest='extensions', default='', help="Extensions")
  parser.add_option('--freezeOtherParameters', dest='freezeOtherParameters', default=0, type='int', help="Freeze all but [cG,cA,cu,cHW,cWW,cB]")
  parser.add_option('--outputDir', dest='outputDir', default='', help='Directory to store output plots')
  return parser.parse_args()
(opt,args) = get_options()

# Global settings
ROOT.gStyle.SetOptStat(0)
ROOT.gROOT.SetBatch(ROOT.kTRUE)
procColorMap = {"ggh":862,"vbf":807,"wh":418,"zh":413,"tth":616}
process = opt.process
stxs_bins = STXS_bins
if opt.freezeOtherParameters: eft_parameters = HEL_parameters_subset
else: eft_parameters = HEL_parameters
Ai_matrix_lhchxswg = Ai_matrix_wg1
procToSTXSProductionModeMap = {'ggh':'GG2H','vbf':'QQ2HQQ', 'wh':'QQ2HLNU','zh':'QQ2HLL','tth':'TTH'}
#legendText = {"pure":"Floating M_{Z}","pure_fixedZmass":"Fixed M_{Z}"}
#legendText = {"pure_NP2eq1_fixedZmass":"Fixed M_{Z}, NP^{2}==1","pure_fixedZmass":"Fixed M_{Z}"}
#legendText = {"pure":"NN23LO1","pure_both":"CTEQ6L (Gabija)"}
#legendText = {"pure":"Default","pure_altpy":"HXSWG Pythia options"}
legendText = {"pure":"Bugged vbfTopology()","pure_rivetv2":"Debugged"}

# Load Ai matrices into dict
Ai_matrices = {}
u_Ai_matrices = {}
for ext in opt.extensions.split(","):
  if ext == "none": extStr = ""
  else: extStr = "_%s"%ext
  with open("./Ai/Ai_matrix_stage1_%s%s.pkl"%(opt.process,extStr),'rb') as f_Ai: Ai_matrices[ext] = pickle.load(f_Ai)
  with open("./Ai/u_Ai_matrix_stage1_%s%s.pkl"%(opt.process,extStr),'rb') as f_Ai: u_Ai_matrices[ext] = pickle.load(f_Ai)

# Loop over STXS bins relevant to process
s = "stage1"
for stxs_bin in stxs_bins[s]:
  if stxs_bin.split("_")[0] == procToSTXSProductionModeMap[process]:

    #IGNORE FWDH bins
    if "FWDH" in stxs_bin: continue

    # Determine set of eft params in Ai matrices
    params = []
    for param in eft_parameters:
      storeParam = False
      t = param['title']
      # Not interested in CP conjugate coeff for now...
      if( t[0] != 't' ):
        if( t in Ai_matrix_lhchxswg[process][stxs_bin] ): storeParam = True
        for Ai_matrix in Ai_matrices.itervalues(): 
          if t in Ai_matrix[process][stxs_bin]: storeParam = True
      if storeParam: params.append(t)

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
    h_axes.GetYaxis().SetTitle("|A_{j}|")
    h_axes.GetYaxis().SetTitleSize(0.08)
    h_axes.GetYaxis().SetLabelSize(0.07)
    h_axes.GetYaxis().SetTitleOffset(0.5)
    h_axes.GetYaxis().CenterTitle()

    # Determine bin centers for lhchxswg and new
    Xbincentre_lhchxswg = []
    Xbincentre_new = []
    for _bin in range(1,len(params)+1):
      Xbincentre_lhchxswg.append(h_axes.GetXaxis().GetBinCenter(_bin)-0.07)
      Xbincentre_new.append(h_axes.GetXaxis().GetBinCenter(_bin)+0.07)

    #Save max/min value of points (A+stat unc for new)
    max_ai = 20
    min_ai = 1

    # Create TGraph for lhchxswg points
    gr_lhchxswg = ROOT.TGraph()
    gr_lhchxswg.SetMarkerStyle(21)
    gr_lhchxswg.SetMarkerSize(1.5)
    gr_lhchxswg.SetMarkerColor(1)
    p = 0
    for j in range(len(params)):
      if params[j] in Ai_matrix_lhchxswg[process][stxs_bin]:
        gr_lhchxswg.SetPoint(p,Xbincentre_lhchxswg[j],abs(Ai_matrix_lhchxswg[process][stxs_bin][params[j]]))
        p+=1
        # Set max/min
        if abs(Ai_matrix_lhchxswg[process][stxs_bin][params[j]]) < min_ai: min_ai = abs(Ai_matrix_lhchxswg[process][stxs_bin][params[j]])
        if abs(Ai_matrix_lhchxswg[process][stxs_bin][params[j]]) > max_ai: max_ai = abs(Ai_matrix_lhchxswg[process][stxs_bin][params[j]])

    # Create TGraphs for different extensions
    grs = {}
    gr_counter = 0
    for ext in opt.extensions.split(","):
      Ai_matrix = Ai_matrices[ext]
      u_Ai_matrix = u_Ai_matrices[ext]
      grs[ext] = ROOT.TGraphAsymmErrors()
      grs[ext].SetMarkerStyle(23-3*gr_counter)
      grs[ext].SetMarkerSize(1.5)
      grs[ext].SetMarkerColor(procColorMap[process]-9*gr_counter)
      grs[ext].SetLineColor(procColorMap[process]-9*gr_counter)
      grs[ext].SetLineWidth(3)
      p = 0
      for j in range(len(params)):
        if params[j] in Ai_matrix[process][stxs_bin]:
          grs[ext].SetPoint(p,Xbincentre_new[j]+0.12*gr_counter,abs(Ai_matrix[process][stxs_bin][params[j]]))
          grs[ext].SetPointError(p,0,0,u_Ai_matrix[process][stxs_bin][params[j]],u_Ai_matrix[process][stxs_bin][params[j]])
          p+=1
          # Set max/min
          if abs(Ai_matrix[process][stxs_bin][params[j]]) < min_ai: min_ai = abs(Ai_matrix[process][stxs_bin][params[j]])
          if (abs(Ai_matrix[process][stxs_bin][params[j]])) > max_ai: max_ai = abs(Ai_matrix[process][stxs_bin][params[j]])
      gr_counter += 1

    # Set minimum and maximum in y-axis
    max_ai = math.pow(10,math.log(5*max_ai,10))
    if math.pow(10,int(math.log(min_ai))-1) < 0.001: min_ai = 0.00101
    else: min_ai = math.pow(10,int(math.log(min_ai))-1)
    h_axes.SetMaximum(max_ai)
    h_axes.SetMinimum(min_ai)

    # Draw in PAD1
    h_axes.Draw()
    gr_lhchxswg.Draw("Same P")
    for ext in opt.extensions.split(","): grs[ext].Draw("Same P")

    # Draw a line for each param
    lines = {}
    for j in range(1,len(params)):
      key = "line_%g"%j
      lines[key] = ROOT.TLine(j,min_ai,j,max_ai)
      lines[key].SetLineWidth(1)
      lines[key].SetLineStyle(4)
      lines[key].Draw("Same")

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

    # Save bins that do not have
    lhchxswg_only = []
    new_only = []

    # Create TGraph with errors for ratios
    grs_ratio = {}
    gr_counter = 0
    for ext in opt.extensions.split(","):
      Ai_matrix = Ai_matrices[ext]
      u_Ai_matrix = u_Ai_matrices[ext]
      grs_ratio[ext] = ROOT.TGraphAsymmErrors()
      grs_ratio[ext].SetLineColor(procColorMap[process]-9*gr_counter)
      grs_ratio[ext].SetLineWidth(3)
      p = 0
      for j in range(len(params)):
        if( params[j] in Ai_matrix_lhchxswg[process][stxs_bin] )&( params[j] in Ai_matrix[process][stxs_bin] ):
          r = Ai_matrix[process][stxs_bin][params[j]]/Ai_matrix_lhchxswg[process][stxs_bin][params[j]]
          u_r = u_Ai_matrix[process][stxs_bin][params[j]]/abs(Ai_matrix_lhchxswg[process][stxs_bin][params[j]])
          grs_ratio[ext].SetPoint(p,Xbincentre_ratio[j]+0.12*gr_counter,r)
          grs_ratio[ext].SetPointError(p,0,0,u_r,u_r)
          p+=1
        
          # Set max/min
          if r+u_r > max_ratio: max_ratio = 1.1*(r+u_r)
          if r-u_r < min_ratio:
            if r-u_r < 0: min_ratio = 1.1*(r-u_r)
            else: min_ratio = r-u_r-0.2

        # Else add bin to lists
        elif ( params[j] in Ai_matrix_lhchxswg[process][stxs_bin] ):
          if j not in lhchxswg_only: lhchxswg_only.append(j)
        else:
          if j not in new_only: new_only.append(j)
      gr_counter += 1
    
    # Set minimum and maximum in y-axis: symmetric
    if (max_ratio-1) > abs(min_ratio-1): min_ratio = 1-(max_ratio-1)
    else: max_ratio = 1+abs(min_ratio-1)
    # Maximum allowed [-.5 to 2.5]
    if max_ratio > 2.5: max_ratio = 2.49
    if min_ratio < -0.5: min_ratio = -0.5
    h_ratio_axes.SetMaximum(max_ratio)
    h_ratio_axes.SetMinimum(min_ratio)

    h_ratio_axes.Draw()
    for ext in opt.extensions.split(","): grs_ratio[ext].Draw("Same P")

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
    for j in lhchxswg_only:
      key = "lhchxswg_%g"%j
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
    gr_counter = 0
    for ext in opt.extensions.split(","):
      for p in range(grs_ratio[ext].GetN()):
        r = grs_ratio[ext].GetY()[p]
        x = grs_ratio[ext].GetX()[p]
        if r > max_ratio:
          key = "arrow_r%g_%s"%(p,ext)
          arrows_ratio[key] = ROOT.TArrow(x+0.12*gr_counter,0.75*max_ratio,x+0.12*gr_counter,0.98*max_ratio,0.03,"|>")
          arrows_ratio[key].SetAngle(40)
          arrows_ratio[key].SetLineWidth(2)
          arrows_ratio[key].SetFillColor(procColorMap[process]-9*gr_counter)
          arrows_ratio[key].Draw()
        elif r < min_ratio:
          key = "arrow_r%g_%s"%(p,ext)
          arrows_ratio[key] = ROOT.TArrow(x+0.12*gr_counter,min_ratio+0.2*(max_ratio-min_ratio),x+0.12*gr_counter,min_ratio+0.01,0.03,"|>")
          arrows_ratio[key].SetAngle(40)
          arrows_ratio[key].SetLineWidth(2)
          arrows_ratio[key].SetFillColor(procColorMap[process]-9*gr_counter)
          arrows_ratio[key].Draw()
      gr_counter += 1

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
    leg.AddEntry(gr_lhchxswg,"LHCHXSWG","P")
    entry_counter = 0
    for ext in opt.extensions.split(","): 
      if entry_counter == 1: leg.AddEntry(0,"","")
      leg.AddEntry(grs[ext],legendText[ext],"P")
      entry_counter += 1
    leg.Draw("Same")

    canv.Update()
    canv.SaveAs("%s/%s_Ai_comparison.png"%(opt.outputDir,stxs_bin))
    canv.SaveAs("%s/%s_Ai_comparison.pdf"%(opt.outputDir,stxs_bin))
    canv.Close()
