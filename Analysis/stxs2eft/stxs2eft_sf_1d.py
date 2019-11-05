import ROOT
import os, sys
import re
import math
from optparse import OptionParser
import pickle
import numpy as np

from STXS import STXS_bins

def get_options():
  parser = OptionParser()
  parser.add_option('--stage', dest='stage', default='stage1', help="STXS Stage")
  parser.add_option('--process', dest='process', default='vbf', help="Signal process")
  parser.add_option('--extension', dest='extension', default='pure', help="Extension")
  parser.add_option('--poi', dest='poi', default='cHW', help="Parameter of interest")
  parser.add_option('--stxsBin', dest='stxsBin', default='', help="Plot for single STXS bin")
  parser.add_option('--poiRange', dest='poiRange', default=0.1, type='float',help="Range of Parameter of interest")
  parser.add_option('--plotLHCHXSWG', dest='plotLHCHXSWG', type='int', default=0, help="Plot LHCHXSWG scaling")
  parser.add_option('--plotUncertainties', dest='plotUncertainties', type='int', default=0, help="Plot uncertainties in scaling function")
  parser.add_option('--setLogY', dest='setLogY', type='int', default=1, help="Set log scale on y-axis")
  parser.add_option('--savePlots', dest='savePlots', type='int', default=0, help="Save plots")
  parser.add_option('--outputDir', dest='outputDir', default='', help='Directory to store output plots')
  return parser.parse_args()
(opt,args) = get_options()

# Global settings
ROOT.gStyle.SetOptStat(0)
if opt.savePlots: ROOT.gROOT.SetBatch(ROOT.kTRUE)
procColorMap = {"ggh":862,"vbf":806,"wh":418,"zh":413,"tth":616}
if "wh_had" in opt.extension: stxsColorMap = {"QQ2HQQ_VBFTOPO_JET3VETO":632,"QQ2HQQ_VBFTOPO_JET3":634,"QQ2HQQ_VH2JET":623,"QQ2HQQ_REST":635,"QQ2HQQ_PTJET1_GT200":624}
elif "zh_had" in opt.extension: stxsColorMap = {"QQ2HQQ_VBFTOPO_JET3VETO":616,"QQ2HQQ_VBFTOPO_JET3":619,"QQ2HQQ_VH2JET":894,"QQ2HQQ_REST":874,"QQ2HQQ_PTJET1_GT200":890}
else: stxsColorMap = {"QQ2HQQ_VBFTOPO_JET3VETO":807,"QQ2HQQ_VBFTOPO_JET3":804,"QQ2HQQ_VH2JET":803,"QQ2HQQ_REST":632,"QQ2HQQ_PTJET1_GT200":800}
procToSTXSProductionModeMap = {'ggh':'GG2H','vbf':'QQ2HQQ', 'wh':'QQ2HLNU','zh':'QQ2HLL','tth':'TTH'}

s = opt.stage
if(opt.plotLHCHXSWG)&(opt.stage!="stage1"):
  print " --> [ERROR] Only have LHCHXSWG numbers for STXS stage1, will plot without comparison"
  opt.plotLHCHXSWG = 0
process = opt.process
ext = opt.extension
extStr = "_%s"%ext
poi = opt.poi
if "Minus" in poi: poiIsMinus = True
else: poiIsMinus = False
if poiIsMinus: 
  [p1,p2]=poi.split("Minus")
  poiLatex = "c_{%s}-c_{%s}"%(p1.split("c")[-1],p2.split("c")[-1])
else: poiLatex = "c_{%s}"%poi.split("c")[-1]
if opt.stxsBin != "":
  binFound = True
  for stxs_bin in STXS_bins[opt.stage]:
    if stxs_bin.split("_")[0] == procToSTXSProductionModeMap[process]:
      if opt.stxsBin in stxs_bin: binFound = True 
  if not binFound:
    print " --> [ERROR] STXS bin %s does not exist for process: %s, stage: %s"%(opt.stxsBin,process,s)
    sys.exit(1)

# Standard poi ranges
poiRangeMap = {"cHW":[-0.12,0.16],"cWWMinuscB":[-0.15,0.15],"cA":[-0.0008,0.0008],"cG":[-0.0001,0.0001],"cu":[-2.,1.],"cd":[-2.,0.5],"cl":[-2.,1.]}

# Import coefficients from pkl files
with open("./Ai/Ai_matrix_%s_%s%s.pkl"%(opt.stage,process,extStr),'rb') as f_Ai: Ai_matrix = pickle.load(f_Ai)
with open("./Ai/u_Ai_matrix_%s_%s%s.pkl"%(opt.stage,process,extStr),'rb') as f_u_Ai: u_Ai_matrix = pickle.load(f_u_Ai)
with open("./Bij/Bij_matrix_%s_%s%s.pkl"%(opt.stage,process,extStr),'rb') as f_Bij: Bij_matrix = pickle.load(f_Bij)
with open("./Bij/u_Bij_matrix_%s_%s%s.pkl"%(opt.stage,process,extStr),'rb') as f_u_Bij: u_Bij_matrix = pickle.load(f_u_Bij)
 
# LHCHXSWG: Aj and Bjk matrices
if opt.plotLHCHXSWG:
  from wg1_note.stage1_Ai import Ai_matrix_wg1
  from wg1_note.stage1_Bij import Bij_matrix_wg1
  if "wh_had" in opt.extension:
    from wg1_note.stage1_Ai import Ai_matrix_wg1_wh_had
    from wg1_note.stage1_Bij import Bij_matrix_wg1_wh_had
    Ai_matrix_wg1['vbf'] = Ai_matrix_wg1_wh_had 
    Bij_matrix_wg1['vbf'] = Bij_matrix_wg1_wh_had 
  elif "zh_had" in opt.extension:
    from wg1_note.stage1_Ai import Ai_matrix_wg1_zh_had
    from wg1_note.stage1_Bij import Bij_matrix_wg1_zh_had
    Ai_matrix_wg1['vbf'] = Ai_matrix_wg1_zh_had 
    Bij_matrix_wg1['vbf'] = Bij_matrix_wg1_zh_had 

# Create TCanvas and pads
canv = ROOT.TCanvas("canv","canv",1100,600)
canv.SetRightMargin(0.25)
if opt.plotLHCHXSWG:
  pad1 = ROOT.TPad("pad1","",0,0.4,1,0.9)
  pad1.SetTopMargin(0)
  pad1.SetBottomMargin(0.01)
  pad1.SetRightMargin(0.25)
  if opt.setLogY: pad1.SetLogy()
  pad2 = ROOT.TPad("pad2","",0,0,1,0.38)
  pad2.SetTopMargin(0.01)
  pad2.SetBottomMargin(0.2)
  pad2.SetRightMargin(0.25)
  pad1.Draw()
  pad2.Draw()
else:
  if opt.setLogY: canv.SetLogy()

# POI
if poi in poiRangeMap: min_cj, max_cj = poiRangeMap[poi][0], poiRangeMap[poi][1]
else: min_cj, max_cj = -1*opt.poiRange, opt.poiRange
step = (max_cj-min_cj)/1000

# Define axes in histogram
if opt.plotLHCHXSWG: pad1.cd()
h_axes = ROOT.TH1F("h_axes","",10,min_cj,max_cj)
#h_axes.GetXaxis().SetTitle("c_{HW}")
#h_axes.GetXaxis().SetTitleSize(0.08)
#h_axes.GetXaxis().SetTitleOffset(0.5)
h_axes.GetXaxis().SetLabelSize(0)
h_axes.GetYaxis().SetTitle("#mu_{i}(%s)"%poiLatex)
h_axes.GetYaxis().SetTitleSize(0.11)
h_axes.GetYaxis().SetTitleOffset(0.3)
h_axes.GetYaxis().SetLabelSize(0.05)
h_axes.GetYaxis().CenterTitle()

# Define maximum mu
max_mu = 1.4
min_mu = 0.8

# Define a graph for each STXS bin relevant to process:
gr_mu = {}
if opt.plotLHCHXSWG: gr_mu_xs = {}

for stxs_bin in STXS_bins[s]:
  if stxs_bin.split("_")[0] == procToSTXSProductionModeMap[process]:

    # Ignore FWD bin
    if "FWDH" in stxs_bin: continue
    if opt.stxsBin not in stxs_bin: continue

    # Create graph 
    gr_mu[stxs_bin] = ROOT.TGraphAsymmErrors()
    gr_mu[stxs_bin].SetMarkerSize(1.5)
    gr_mu[stxs_bin].SetMarkerColor(stxsColorMap[stxs_bin])
    gr_mu[stxs_bin].SetLineColor(stxsColorMap[stxs_bin])
    gr_mu[stxs_bin].SetFillColor(stxsColorMap[stxs_bin])
    gr_mu[stxs_bin].SetLineWidth(5)

    # Extract relevant ai and bij
    if poiIsMinus:
      p1,p2 = poi.split("Minus")[0],poi.split("Minus")[1]
      if p1 in Ai_matrix[process][stxs_bin]: ai1, u_ai1 = Ai_matrix[process][stxs_bin][p1], u_Ai_matrix[process][stxs_bin][p1]
      else: ai1, u_ai1 = 0, 0
      if p2 in Ai_matrix[process][stxs_bin]: ai2, u_ai2 = Ai_matrix[process][stxs_bin][p2], u_Ai_matrix[process][stxs_bin][p2]
      else: ai2, u_ai2 = 0, 0
      if p1 in Bij_matrix[process][stxs_bin]: bij1, u_bij1 = Bij_matrix[process][stxs_bin][p1], u_Bij_matrix[process][stxs_bin][p1]
      else: bij1, u_bij1 = 0, 0
      if p2 in Bij_matrix[process][stxs_bin]: bij2, u_bij2 = Bij_matrix[process][stxs_bin][p2], u_Bij_matrix[process][stxs_bin][p2]
      else: bij2, u_bij2 = 0, 0
      if "%s%s"%(p1,p2) in Bij_matrix[process][stxs_bin]: bij12, u_bij12 = Bij_matrix[process][stxs_bin]["%s%s"%(p1,p2)], u_Bij_matrix[process][stxs_bin]["%s%s"%(p1,p2)]
      else: bij12, u_bij12 = 0, 0
    else:
      if poi in Ai_matrix[process][stxs_bin]: ai, u_ai = Ai_matrix[process][stxs_bin][poi], u_Ai_matrix[process][stxs_bin][poi]
      else: ai, u_ai = 0, 0
      if poi in Bij_matrix[process][stxs_bin]: bij, u_bij = Bij_matrix[process][stxs_bin][poi], u_Bij_matrix[process][stxs_bin][poi]
      else: bij, u_bij = 0, 0

    # Fill points in graph
    cj_values = np.arange(min_cj,max_cj,step).tolist()
    p = 0
    
    if poiIsMinus:
      for cj in cj_values:
        mu = 1+0.5*(ai1-ai2)*cj+0.25*(bij1+bij2-bij12)*cj*cj
        u_int = 0.5*math.sqrt(u_ai1*u_ai1+u_ai2*u_ai2)*cj
        u_bsm = 0.25*math.sqrt(u_bij1*u_bij1+u_bij2*u_bij2+u_bij12*u_bij12)*cj*cj
        u_mu = math.sqrt(u_int*u_int+u_bsm*u_bsm)
        gr_mu[stxs_bin].SetPoint(p,cj,mu)
        if opt.plotUncertainties: gr_mu[stxs_bin].SetPointError(p,0,0,u_mu,u_mu) 
        p += 1
        # Set max
        if mu > max_mu: max_mu = mu
        if mu < min_mu: min_mu = mu
    else:
      for cj in cj_values:
        mu = 1+ai*cj+bij*cj*cj
        u_int = u_ai*cj
        u_bsm = u_bij*cj*cj
        u_mu = math.sqrt(u_int*u_int+u_bsm*u_bsm)
        gr_mu[stxs_bin].SetPoint(p,cj,mu)
        if opt.plotUncertainties: gr_mu[stxs_bin].SetPointError(p,0,0,u_mu,u_mu)
        p += 1
        # Set max
        if mu > max_mu: max_mu = mu
        if mu < min_mu: min_mu = mu

    # Plot LHCHXSWG numbers
    if opt.plotLHCHXSWG:
      # Greate graph
      gr_mu_xs[stxs_bin] = ROOT.TGraph()
      gr_mu_xs[stxs_bin].SetLineColor(stxsColorMap[stxs_bin])
      gr_mu_xs[stxs_bin].SetLineStyle(2)
      gr_mu_xs[stxs_bin].SetLineWidth(3)

      #Extract ai and bij
      if poiIsMinus:
        p1,p2 = poi.split("Minus")[0],poi.split("Minus")[1]
        if p1 in Ai_matrix_wg1[process][stxs_bin]: ai1 = Ai_matrix_wg1[process][stxs_bin][p1]
        else: ai1 = 0
        if p2 in Ai_matrix_wg1[process][stxs_bin]: ai2 = Ai_matrix_wg1[process][stxs_bin][p2]
        else: ai2 = 0
        if p1 in Bij_matrix_wg1[process][stxs_bin]: bij1 = Bij_matrix_wg1[process][stxs_bin][p1]
        else: bij1 = 0
        if p2 in Bij_matrix_wg1[process][stxs_bin]: bij2 = Bij_matrix_wg1[process][stxs_bin][p2]
        else: bij2 = 0
        if "%s%s"%(p1,p2) in Bij_matrix_wg1[process][stxs_bin]: bij12 = Bij_matrix_wg1[process][stxs_bin]["%s%s"%(p1,p2)]
        else: bij12 = 0
      else:
        if poi in Ai_matrix_wg1[process][stxs_bin]: ai = Ai_matrix_wg1[process][stxs_bin][poi]
        else: ai = 0
        if poi in Bij_matrix_wg1[process][stxs_bin]: bij = Bij_matrix_wg1[process][stxs_bin][poi]
        else: bij = 0

      # Fill points in graph
      cj_values = np.arange(min_cj,max_cj,0.001).tolist()
      p = 0
      
      if poiIsMinus:
        for cj in cj_values:
          mu = 1+0.5*(ai1-ai2)*cj+0.25*(bij1+bij2-bij12)*cj*cj
          gr_mu_xs[stxs_bin].SetPoint(p,cj,mu)
          p += 1
          # Set max
          if mu > max_mu: max_mu = mu
          if mu < min_mu: min_mu = mu
      else:
        for cj in cj_values:
          mu = 1+ai*cj+bij*cj*cj
          gr_mu_xs[stxs_bin].SetPoint(p,cj,mu)
          p += 1
          # Set max
          if mu > max_mu: max_mu = mu
          if mu < min_mu: min_mu = mu

# Set maximum of hist
h_axes.SetMaximum(max_mu)
h_axes.SetMinimum(min_mu)

# Draw
h_axes.Draw()
if opt.plotUncertainties:
  for gr in gr_mu.itervalues(): gr.Draw("Same 3")
else: 
  for gr in gr_mu.itervalues(): gr.Draw("Same L")
if opt.plotLHCHXSWG: 
  for gr in gr_mu_xs.itervalues(): gr.Draw("Same L")

#Ratio plot
if opt.plotLHCHXSWG:
  # Ratio plot
  pad2.cd()
  # Define axes in histogram
  h_axes_r = ROOT.TH1F("h_axes_ratio","",10,min_cj,max_cj)
  h_axes_r.GetXaxis().SetTitle(poiLatex)
  h_axes_r.GetXaxis().SetTitleSize(0.12)
  h_axes_r.GetXaxis().SetLabelSize(0.08)
  h_axes_r.GetXaxis().SetTitleOffset(0.7)
  h_axes_r.GetYaxis().SetTitle("Ratio")
  h_axes_r.GetYaxis().SetTitleSize(0.12)
  h_axes_r.GetYaxis().SetTitleOffset(0.3)
  h_axes_r.GetYaxis().SetLabelSize(0.08)
  h_axes_r.GetYaxis().CenterTitle()
  h_axes_r.SetMinimum(0)
  h_axes_r.SetMaximum(2)

  # Define histogram for ratio graphs
  gr_mu_r = {}
  max_r = 1.12
  min_r = 0.88
  for stxs_bin in STXS_bins[s]:
    if stxs_bin.split("_")[0] == procToSTXSProductionModeMap[process]:

      # Ignore FWD bin
      if "FWDH" in stxs_bin: continue
      if opt.stxsBin not in stxs_bin: continue

      # Create graph 
      gr_mu_r[stxs_bin] = ROOT.TGraphAsymmErrors()
      gr_mu_r[stxs_bin].SetMarkerSize(1.5)
      gr_mu_r[stxs_bin].SetMarkerColor(stxsColorMap[stxs_bin])
      gr_mu_r[stxs_bin].SetLineColor(stxsColorMap[stxs_bin])
      gr_mu_r[stxs_bin].SetFillColor(stxsColorMap[stxs_bin])
      gr_mu_r[stxs_bin].SetLineWidth(3)

      # Extract relevant ai and bij
      if poiIsMinus:
        p1,p2 = poi.split("Minus")[0],poi.split("Minus")[1]
        if p1 in Ai_matrix[process][stxs_bin]: ai1, u_ai1 = Ai_matrix[process][stxs_bin][p1], u_Ai_matrix[process][stxs_bin][p1]
        else: ai1, u_ai1 = 0, 0
        if p2 in Ai_matrix[process][stxs_bin]: ai2, u_ai2 = Ai_matrix[process][stxs_bin][p2], u_Ai_matrix[process][stxs_bin][p2]
        else: ai2, u_ai2 = 0, 0
        if p1 in Bij_matrix[process][stxs_bin]: bij1, u_bij1 = Bij_matrix[process][stxs_bin][p1], u_Bij_matrix[process][stxs_bin][p1]
        else: bij1, u_bij1 = 0, 0
        if p2 in Bij_matrix[process][stxs_bin]: bij2, u_bij2 = Bij_matrix[process][stxs_bin][p2], u_Bij_matrix[process][stxs_bin][p2]
        else: bij2, u_bij2 = 0, 0
        if "%s%s"%(p1,p2) in Bij_matrix[process][stxs_bin]: bij12, u_bij12 = Bij_matrix[process][stxs_bin]["%s%s"%(p1,p2)], u_Bij_matrix[process][stxs_bin]["%s%s"%(p1,p2)]
        else: bij12, u_bij12 = 0, 0
      else:
        if poi in Ai_matrix[process][stxs_bin]: ai, u_ai = Ai_matrix[process][stxs_bin][poi], u_Ai_matrix[process][stxs_bin][poi]
        else: ai, u_ai = 0, 0
        if poi in Bij_matrix[process][stxs_bin]: bij, u_bij = Bij_matrix[process][stxs_bin][poi], u_Bij_matrix[process][stxs_bin][poi]
        else: bij, u_bij = 0, 0
      # LHCHXSWG
      if poiIsMinus:
        p1,p2 = poi.split("Minus")[0],poi.split("Minus")[1]
        if p1 in Ai_matrix_wg1[process][stxs_bin]: ai1_xs = Ai_matrix_wg1[process][stxs_bin][p1]
        else: ai1_xs = 0
        if p2 in Ai_matrix_wg1[process][stxs_bin]: ai2_xs = Ai_matrix_wg1[process][stxs_bin][p2]
        else: ai2_xs = 0
        if p1 in Bij_matrix_wg1[process][stxs_bin]: bij1_xs = Bij_matrix_wg1[process][stxs_bin][p1]
        else: bij1_xs = 0
        if p2 in Bij_matrix_wg1[process][stxs_bin]: bij2_xs = Bij_matrix_wg1[process][stxs_bin][p2]
        else: bij2_xs = 0
        if "%s%s"%(p1,p2) in Bij_matrix_wg1[process][stxs_bin]: bij12_xs = Bij_matrix_wg1[process][stxs_bin]["%s%s"%(p1,p2)]
        else: bij12_xs = 0
      else:
        if poi in Ai_matrix_wg1[process][stxs_bin]: ai_xs = Ai_matrix_wg1[process][stxs_bin][poi]
        else: ai_xs = 0
        if poi in Bij_matrix_wg1[process][stxs_bin]: bij_xs = Bij_matrix_wg1[process][stxs_bin][poi]
        else: bij_xs = 0

      # Fill points in graph
      cj_values = np.arange(min_cj,max_cj,step).tolist()
      p = 0
      if poiIsMinus:
        for cj in cj_values:
          mu = 1+0.5*(ai1-ai2)*cj+0.25*(bij1+bij2-bij12)*cj*cj
          mu_xs = 1+0.5*(ai1_xs-ai2_xs)*cj+0.25*(bij1_xs+bij2_xs-bij12_xs)*cj*cj
          r = mu/mu_xs
          u_int = 0.5*math.sqrt(u_ai1*u_ai1+u_ai2*u_ai2)*cj
          u_bsm = 0.25*math.sqrt(u_bij1*u_bij1+u_bij2*u_bij2+u_bij12*u_bij12)*cj*cj
          u_mu = math.sqrt(u_int*u_int+u_bsm*u_bsm)
          u_r = u_mu/mu_xs
          gr_mu_r[stxs_bin].SetPoint(p,cj,r)
          if opt.plotUncertainties: gr_mu_r[stxs_bin].SetPointError(p,0,0,u_r,u_r) 
          p += 1
          # Set max
          if r > max_r: max_r = r
          if r < min_r: min_r = r
      else:
        for cj in cj_values:
          mu = 1+ai*cj+bij*cj*cj
          mu_xs = 1+ai_xs*cj+bij_xs*cj*cj
          r = mu/mu_xs
          u_int = u_ai*cj
          u_bsm = u_bij*cj*cj
          u_mu = math.sqrt(u_int*u_int+u_bsm*u_bsm)
          u_r = u_mu/mu_xs
          gr_mu_r[stxs_bin].SetPoint(p,cj,r)
          if opt.plotUncertainties: gr_mu_r[stxs_bin].SetPointError(p,0,0,u_r,u_r)
          p += 1
          # Set max
          if r > max_r: max_r = r
          if r < min_r: min_r = r

  # Set maximum of hist
  if max_r > 2: max_r = 2
  if min_r < -1: min_r = -1
  h_axes_r.SetMaximum(max_r)
  h_axes_r.SetMinimum(min_r)

  # Draw
  h_axes_r.Draw()
  for gr in gr_mu_r.itervalues(): gr.Draw("Same 3")

  # Draw lines in ratio plot
  if (max_r-min_r)>0.5: step = 0.2
  else: step = 0.1
  l_pos = np.arange(-1,2,step).tolist()
  l_r = {}
  litr = 0
  for l in l_pos:
    if(l>min_r)&(l<max_r):
      key = "line_%s"%litr
      l_r[key] = ROOT.TLine(min_cj,l,max_cj,l)
      l_r[key].SetLineWidth(2)
      l_r[key].SetLineStyle(2)
      l_r[key].Draw("Same")
      litr += 1 

# Draw legend and text on plot
if opt.plotLHCHXSWG: pad1.cd()
leg = ROOT.TLegend(0.77,0.1,0.99,0.9)
leg.SetFillColor(0)
leg.SetLineColor(0)
for stxs_bin in STXS_bins[s]:
  if stxs_bin.split("_")[0] == procToSTXSProductionModeMap[process]:
    # Ignore FWD bin
    if "FWDH" in stxs_bin: continue
    if opt.stxsBin not in stxs_bin: continue
    leg.AddEntry(gr_mu[stxs_bin],"_".join(stxs_bin.split("_")[1:]),"L")
leg.Draw("Same")

if opt.plotLHCHXSWG:
  pad2.cd()
  # Dummy graphs
  gr_dummy_stxs2eft = ROOT.TGraph()
  gr_dummy_stxs2eft.SetLineStyle(2)
  gr_dummy_stxs2eft.SetLineWidth(3)
  leg2 = ROOT.TLegend(0.77,0.8,0.99,0.9)
  leg2.SetFillColor(0)
  leg2.SetLineColor(0)
  leg2.AddEntry(gr_dummy_stxs2eft,"LHCHXSWG","L")
  leg2.Draw("Same")

canv.cd()
lat = ROOT.TLatex()
lat.SetTextFont(42)
lat.SetLineWidth(2)
lat.SetTextAlign(11)
lat.SetNDC()
lat.SetTextSize(0.042)
lat.DrawLatex(0.1,0.92,"HEL UFO")

canv.Update()
if opt.savePlots:
  if opt.stxsBin:
    canv.SaveAs("%s/%s_%s_%s_vs_%s.pdf"%(opt.outputDir,opt.stage,process,opt.stxsBin,opt.poi))
    canv.SaveAs("%s/%s_%s_%s_vs_%s.png"%(opt.outputDir,opt.stage,process,opt.stxsBin,opt.poi))
  else:
    canv.SaveAs("%s/%s_%s_vs_%s.pdf"%(opt.outputDir,opt.stage,process,opt.poi))
    canv.SaveAs("%s/%s_%s_vs_%s.png"%(opt.outputDir,opt.stage,process,opt.poi))
