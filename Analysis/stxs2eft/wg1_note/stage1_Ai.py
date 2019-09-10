# Script to hold the Ai terms for each STXS bin for stage 1 (taken directly from LHCHXSWG-INT-2017-001)

Ai_matrix_wg1 = {
  'ggh':{
   'GG2H_VBFTOPO_JET3VETO':{"cG'": 56.0},
   'GG2H_VBFTOPO_JET3':{'c3G': 9.0, 'c2G': 8.0, "cG'": 56.0},
   'GG2H_0J':{"cG'": 56.0},
   'GG2H_1J_PTH_0_60':{"cG'": 56.0},
   'GG2H_1J_PTH_60_120':{"cG'": 56.0},
   'GG2H_1J_PTH_120_200':{'c3G': 18.0, 'c2G': 11.0, "cG'": 56.0},
   'GG2H_1J_PTH_GT200':{'c3G': 52.0, 'c2G': 34.0, "cG'": 56.0},
   'GG2H_GE2J_PTH_0_60':{"cG'": 56.0},
   'GG2H_GE2J_PTH_60_120':{'c3G': 8.0, 'c2G': 7.0, "cG'": 56.0},
   'GG2H_GE2J_PTH_120_200':{'c3G': 23.0, 'c2G': 18.0, "cG'": 56.0},
   'GG2H_GE2J_PTH_GT200':{'c3G': 90.0, 'c2G': 68.0, "cG'": 56.0}
   },

  # QQ2HQQ terms: from note
  'vbf':{
   'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-1.0,"cT":-1.0,"cWW":1.3,"cB":-0.023,"cHW":-4.3,"cHB":-0.29,"cHQ":0.092,"cpHQ":-5.3,"cHu":-0.33,"cHd":0.12},
   'QQ2HQQ_VBFTOPO_JET3':{"cH":-1.0,"cT":-1.1,"cWW":1.2,"cB":-0.027,"cHW":-5.8,"cHB":-0.41,"cHQ":0.13,"cpHQ":-6.9,"cHu":-0.45,"cHd":0.15},
   'QQ2HQQ_VH2JET':{"cH":-0.99,"cT":-1.2,"cWW":7.8,"cB":-0.19,"cHW":-31,"cHB":-2.4,"cHQ":0.9,"cpHQ":-38,"cHu":-2.8,"cHd":0.9},
   'QQ2HQQ_REST':{"cH":-1.0,"cT":-1.0,"cWW":1.4,"cB":-0.028,"cHW":-6.2,"cHB":-0.42,"cHQ":0.14,"cpHQ":-6.9,"cHu":-0.42,"cHd":0.16},
   'QQ2HQQ_PTJET1_GT200':{"cH":-1.0,"cT":-0.95,"cWW":1.5,"cB":-0.025,"cHW":-3.6,"cHB":-0.24,"cHQ":0.084,"cpHQ":-4.5,"cHu":-0.25,"cHd":0.1},
   },

  # Weighted terms: VBF + WH_had + ZH_had
  #'vbf':{
  # 'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-0.0047,"cT":-0.0080,"cWW":1.4378,"cB":-0.0031,"cHW":-4.2272,"cHB":-0.2832,"cHQ":-0.0043,"cpHQ":0.1585,"cHu":0.0152,"cHd":-0.0052},
  # 'QQ2HQQ_VBFTOPO_JET3':{"cH":-0.0627,"cT":-0.0995,"cWW":3.7432,"cB":0.2372,"cHW":-4.2968,"cHB":-0.2769,"cHQ":-0.0590,"cpHQ":2.2241,"cHu":0.2100,"cHd":-0.0698},
  # 'QQ2HQQ_VH2JET':{"cH":-0.8931,"cT":-1.4367,"cWW":38.2540,"cB":3.7558,"cHW":17.9631,"cHB":1.7254,"cHQ":-0.8620,"cpHQ":32.5319,"cHu":2.8505,"cHd":-1.0745},
  # 'QQ2HQQ_REST':{"cH":-0.3626,"cT":-0.5797,"cWW":12.9063,"cB":1.1947,"cHW":1.4549,"cHB":0.2287,"cHQ":-0.2584,"cpHQ":9.4851,"cHu":0.8616,"cHd":-0.3342},
  # 'QQ2HQQ_PTJET1_GT200':{"cH":-0.3410,"cT":-0.5521,"cWW":61.3381,"cB":5.5757,"cHW":26.0698,"cHB":3.0360,"cHQ":-1.5782,"cpHQ":56.6605,"cHu":5.3293,"cHd":-1.7166}
  # },

  # Purely VBF terms: from twiki
  #'vbf':{
  # 'QQ2HQQ_VBFTOPO_JET3VETO':{'cHB': -0.29, 'cH': -1.0, 'cHd': 0.12, 'cB': -0.023, 'cWW': 1.3, 'cHQ': 0.092, 'cHu': -0.33, 'cHW': -4.3, 'cpHQ': -5.3, 'cT': -1.0},
  # 'QQ2HQQ_VBFTOPO_JET3':{'cHB': -0.41, 'cH': -1.0, 'cHd': 0.15, 'cB': -0.027, 'cWW': 1.2, 'cHQ': 0.13, 'cHu': -0.45, 'cHW': -5.8, 'cpHQ': -6.9, 'cT': -1.1},
  # 'QQ2HQQ_VH2JET':{'cHB': -0.42, 'cH': -1.0, 'cHd': 0.16, 'cB': -0.028, 'cWW': 1.4, 'cHQ': 0.14, 'cHu': -0.42, 'cHW': -6.2, 'cpHQ': -6.9, 'cT': -1.0},
  # 'QQ2HQQ_REST':{'cHB': -0.24, 'cH': -1.0, 'cHd': 0.1, 'cB': -0.025, 'cWW': 1.5, 'cHQ': 0.084, 'cHu': -0.25, 'cHW': -3.6, 'cpHQ': -4.5, 'cT': -0.95},
  # 'QQ2HQQ_PTJET1_GT200':{'cHB': -2.4, 'cH': -0.99, 'cHd': 0.9, 'cB': -0.19, 'cWW': 7.8, 'cHQ': 0.9, 'cHu': -2.8, 'cHW': -31.0, 'cpHQ': -38.0, 'cT': -1.2}
  # },

  'wh':{
   'QQ2HLNU_PTV_0_150':{'cpHL': 2.0, 'cH': -1.0, 'cpHQ': 24.0, 'cWW': 34.0, 'cHW': 11.0},
   'QQ2HLNU_PTV_150_250_0J':{'cpHL': 2.0, 'cH': -1.0, 'cpHQ': 67.0, 'cWW': 76.0, 'cHW': 51.0},
   'QQ2HLNU_PTV_150_250_GE1J':{'cpHL': 2.0, 'cH': -1.0, 'cpHQ': 61.0, 'cWW': 71.0, 'cHW': 46.0},
   'QQ2HLNU_PTV_GT250':{'cpHL': 2.0, 'cH': -1.0, 'cpHQ': 190.0, 'cWW': 200.0, 'cHW': 170.0}
   },

  'zh':{
   'QQ2HLL_PTV_0_150':{'cpHQ': 23.0, 'cpHL': 2.0, 'cHB': 2.5, 'cH': -1.0, 'cHd': -2.0, 'cHe': -0.23, 'cB': 8.4, 'cHL': -0.96, 'cWW': 30.0, 'cHQ': -1.9, 'cHu': 5.2, 'cHW': 8.5, "cA'": 0.032, 'cT': -4.0},
   'QQ2HLL_PTV_150_250_0J':{'cpHL': 2.1, 'cHB': 11.0, 'cH': -1.0, 'cHd': -5.2, 'cHe': -0.23, 'cB': 18.0, 'cHL': -0.98, 'cWW': 62.0, 'cHQ': -5.0, 'cHu': 14.0, 'cHW': 38.0, 'cpHQ': 61.0, 'cT': -4.0},
   'QQ2HLL_PTV_150_250_GE1J':{'cpHL': 2.1, 'cHB': 9.9, 'cH': -1.0, 'cHd': -4.6, 'cHe': -0.24, 'cB': 17.0, 'cHL': -0.99, 'cWW': 58.0, 'cHQ': -4.6, 'cHu': 14.0, 'cHW': 33.0, 'cpHQ': 56.0, 'cT': -4.0},
   'QQ2HLL_PTV_GT250':{'cpHL': 2.1, 'cHB': 38.0, 'cH': -1.0, 'cHd': -14.0, 'cHe': -0.24, 'cB': 46.0, 'cHL': -0.98, 'cWW': 150.0, 'cHQ': -14.0, 'cHu': 42.0, 'cHW': 130.0, 'cpHQ': 170.0, 'cT': -4.0}
   },

  'tth':{
   'TTH':{'cH': -0.98, 'c3G': 27.0, 'cG': 0.93, 'cuG': 310.0, 'c2G': -13.0, 'cu': 2.9}
   }
}
