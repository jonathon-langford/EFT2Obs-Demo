mode = "int"
w = "0.0001"

eft_params = ["cH","cT","c6","cu","cd","cl","cWW","cB","cHW","cHB","cA","cG","cHQ","cpHQ","cHu","cHd","cHud","cHL","cpHL","cHe","cuB","cuW","cuG","cdB","cdW","cdG","clB","clW","c3W","c3G","c2W","c2B","c2G","tcHW","tcHB","tcG","tcA","tc3W","tc3G"]

pois = ["cu","cd","cl","cWW","cB","cHW","cHB","cA","cG"]

f = open("./reweight_card_%s_subset.dat"%mode,"w")

# LINEAR/SQUARED TERMS
for poi in pois:
  f.write("launch --rwgt_name=%s_%s\n"%(mode,poi))
  for i in range(len(eft_params)):
    if i == eft_params.index(poi): f.write("set NEWCOUP %g %s\n"%((i+1),w))
    else: f.write("set NEWCOUP %g 0\n"%(i+1))

# CROSS TERMS IF BSM
if mode == "bsm":
  for poi_i in pois:
    for poi_j in pois:
      if pois.index(poi_j)>pois.index(poi_i):
        f.write("launch --rwgt_name=bsm_%s_%s\n"%(poi_i,poi_j))
        for i in range(len(eft_params)):
          if i == eft_params.index(poi_i): f.write("set NEWCOUP %g %s\n"%((i+1),w))
          elif i == eft_params.index(poi_j): f.write("set NEWCOUP %g %s\n"%((i+1),w))
          else: f.write("set NEWCOUP %g 0\n"%(i+1))

f.close()
