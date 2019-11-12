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
  #'vbf':{
  # 'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-1.0,"cT":-1.0,"cWW":1.3,"cB":-0.023,"cHW":-4.3,"cHB":-0.29,"cHQ":0.092,"cpHQ":-5.3,"cHu":-0.33,"cHd":0.12},
  # 'QQ2HQQ_VBFTOPO_JET3':{"cH":-1.0,"cT":-1.1,"cWW":1.2,"cB":-0.027,"cHW":-5.8,"cHB":-0.41,"cHQ":0.13,"cpHQ":-6.9,"cHu":-0.45,"cHd":0.15},
  # 'QQ2HQQ_VH2JET':{"cH":-0.99,"cT":-1.2,"cWW":7.8,"cB":-0.19,"cHW":-31,"cHB":-2.4,"cHQ":0.9,"cpHQ":-38,"cHu":-2.8,"cHd":0.9},
  # 'QQ2HQQ_REST':{"cH":-1.0,"cT":-1.0,"cWW":1.4,"cB":-0.028,"cHW":-6.2,"cHB":-0.42,"cHQ":0.14,"cpHQ":-6.9,"cHu":-0.42,"cHd":0.16},
  # 'QQ2HQQ_PTJET1_GT200':{"cH":-1.0,"cT":-0.95,"cWW":1.5,"cB":-0.025,"cHW":-3.6,"cHB":-0.24,"cHQ":0.084,"cpHQ":-4.5,"cHu":-0.25,"cHd":0.1},
  # 'QQ2HQQ_VH2JET':{"cH":-1.0,"cT":-1.0,"cWW":1.4,"cB":-0.028,"cHW":-6.2,"cHB":-0.42,"cHQ":0.14,"cpHQ":-6.9,"cHu":-0.42,"cHd":0.16},
  # 'QQ2HQQ_REST':{"cH":-1.0,"cT":-0.95,"cWW":1.5,"cB":-0.025,"cHW":-3.6,"cHB":-0.24,"cHQ":0.084,"cpHQ":-4.5,"cHu":-0.25,"cHd":0.1},
  # 'QQ2HQQ_PTJET1_GT200':{"cH":-0.99,"cT":-1.2,"cWW":7.8,"cB":-0.19,"cHW":-31,"cHB":-2.4,"cHQ":0.9,"cpHQ":-38,"cHu":-2.8,"cHd":0.9},
  # },

  # Purely VBF terms: from twiki
  'vbf':{
   'QQ2HQQ_VBFTOPO_JET3VETO':{"cWW":1.256,"cB":-0.02319,"cHW":-4.31,"cHB":-0.2907},
   'QQ2HQQ_VBFTOPO_JET3':{"cWW":1.204,"cB":-0.02692,"cHW":-5.76,"cHB":-0.4058},
   'QQ2HQQ_VH2JET':{"cWW":1.389,"cB":-0.0284,"cHW":-6.23,"cHB":-0.417},
   'QQ2HQQ_REST':{"cWW":1.546,"cB":-0.02509,"cHW":-3.631,"cHB":-0.2361},
   'QQ2HQQ_PTJET1_GT200':{"cWW":7.82,"cB":-0.1868,"cHW":-30.65,"cHB":-2.371}
   },

  'wh_had':{
   'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-0.94,"cWW":39.5,"cHW":13.8,"cpHQ":32.1},
   'QQ2HQQ_VBFTOPO_JET3':{"cH":-1.04,"cWW":44.9,"cHW":20.3,"cpHQ":36.8},
   'QQ2HQQ_VH2JET':{"cH":-0.996,"cWW":45.57,"cHW":23.66,"cpHQ":37.55},
   'QQ2HQQ_REST':{"cH":-1.002,"cWW":34.29,"cHW":11.56,"cpHQ":26.27},
   'QQ2HQQ_PTJET1_GT200':{"cH":-1.003,"cWW":181.2,"cHW":152.3,"cpHQ":173.7}
  },

  'zh_had':{ 
   'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-0.94,"cT":-4.0,"cWW":34.8,"cB":10.0,"cHW":9.9,"cHB":3.04,"cHQ":-2.14,"cpHQ":31.1,"cHu":7.6,"cHd":-2.59},
   'QQ2HQQ_VBFTOPO_JET3':{"cH":-0.97,"cT":-3.98,"cWW":38.1,"cB":10.5,"cHW":14.2,"cHB":4.15,"cHQ":-2.36,"cpHQ":34.5,"cHu":8.4,"cHd":-2.79},
   'QQ2HQQ_VH2JET':{"cH":-0.998,"cT":-4.002,"cWW":37.99,"cB":10.47,"cHW":16.45,"cHB":4.927,"cHQ":-2.401,"cpHQ":34.45,"cHu":7.94,"cHd":-2.993},
   'QQ2HQQ_REST':{"cH":-1.001,"cT":-3.998,"cWW":30.89,"cB":8.35,"cHW":8.71,"cHB":2.616,"cHQ":-1.782,"cpHQ":26.1,"cHu":5.942,"cHd":-2.305},
   'QQ2HQQ_PTJET1_GT200':{"cH":-1.003,"cT":-4.03,"cWW":141.5,"cB":41.6,"cHW":112.5,"cHB":33.6,"cHQ":-11.52,"cpHQ":156.2,"cHu":38.9,"cHd":-12.53}
  },

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
   'TTH':{'cH': -0.98, 'c3G': 27.0, "cG'": 0.93, 'cuG': 310.0, 'c2G': -13.0, 'cu': 2.9}
   }
}

Ai_matrix_wg1_note = {
   'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-1.0,"cT":-1.0,"cWW":1.3,"cB":-0.023,"cHW":-4.3,"cHB":-0.29,"cHQ":0.092,"cpHQ":-5.3,"cHu":-0.33,"cHd":0.12},
   'QQ2HQQ_VBFTOPO_JET3':{"cH":-1.0,"cT":-1.1,"cWW":1.2,"cB":-0.027,"cHW":-5.8,"cHB":-0.41,"cHQ":0.13,"cpHQ":-6.9,"cHu":-0.45,"cHd":0.15},
   'QQ2HQQ_VH2JET':{"cH":-0.99,"cT":-1.2,"cWW":7.8,"cB":-0.19,"cHW":-31,"cHB":-2.4,"cHQ":0.9,"cpHQ":-38,"cHu":-2.8,"cHd":0.9},
   'QQ2HQQ_REST':{"cH":-1.0,"cT":-1.0,"cWW":1.4,"cB":-0.028,"cHW":-6.2,"cHB":-0.42,"cHQ":0.14,"cpHQ":-6.9,"cHu":-0.42,"cHd":0.16},
   'QQ2HQQ_PTJET1_GT200':{"cH":-1.0,"cT":-0.95,"cWW":1.5,"cB":-0.025,"cHW":-3.6,"cHB":-0.24,"cHQ":0.084,"cpHQ":-4.5,"cHu":-0.25,"cHd":0.1}
}

Ai_matrix_wg1_stxs = {
  'QQ2HQQ_VBFTOPO_JET3VETO':{"cWW":2.439423,"cB":0.080395,"cHW":-3.766823,"cHB":-0.250074},
  'QQ2HQQ_VBFTOPO_JET3':{"cWW":1.355322,"cB":-0.014338,"cHW":-5.672183,"cHB":-0.399386},
  'QQ2HQQ_VH2JET':{"cWW":34.230110,"cB":2.791937,"cHW":15.431824,"cHB":1.228743},
  'QQ2HQQ_REST':{"cWW":6.289227,"cB":0.390137,"cHW":-1.493175,"cHB":-0.071782},
  'QQ2HQQ_PTJET1_GT200':{"cWW":31.174274,"cB":1.502787,"cHW":-5.923059,"cHB":-0.686964},
}

Ai_matrix_wg1_wh_had = {
  'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-0.94,"cWW":39.5,"cHW":13.8,"cpHQ":32.1},
  'QQ2HQQ_VBFTOPO_JET3':{"cH":-1.04,"cWW":44.9,"cHW":20.3,"cpHQ":36.8},
  'QQ2HQQ_VH2JET':{"cH":-0.996,"cWW":45.57,"cHW":23.66,"cpHQ":37.55},
  'QQ2HQQ_REST':{"cH":-1.002,"cWW":34.29,"cHW":11.56,"cpHQ":26.27},
  'QQ2HQQ_PTJET1_GT200':{"cH":-1.003,"cWW":181.2,"cHW":152.3,"cpHQ":173.7} 
}

Ai_matrix_wg1_zh_had = {
  'QQ2HQQ_VBFTOPO_JET3VETO':{"cH":-0.94,"cT":-4.0,"cWW":34.8,"cB":10.0,"cHW":9.9,"cHB":3.04,"cHQ":-2.14,"cpHQ":31.1,"cHu":7.6,"cHd":-2.59},
  'QQ2HQQ_VBFTOPO_JET3':{"cH":-0.97,"cT":-3.98,"cWW":38.1,"cB":10.5,"cHW":14.2,"cHB":4.15,"cHQ":-2.36,"cpHQ":34.5,"cHu":8.4,"cHd":-2.79},
  'QQ2HQQ_VH2JET':{"cH":-0.998,"cT":-4.002,"cWW":37.99,"cB":10.47,"cHW":16.45,"cHB":4.927,"cHQ":-2.401,"cpHQ":34.45,"cHu":7.94,"cHd":-2.993},
  'QQ2HQQ_REST':{"cH":-1.001,"cT":-3.998,"cWW":30.89,"cB":8.35,"cHW":8.71,"cHB":2.616,"cHQ":-1.782,"cpHQ":26.1,"cHu":5.942,"cHd":-2.305},
  'QQ2HQQ_PTJET1_GT200':{"cH":-1.003,"cT":-4.03,"cWW":141.5,"cB":41.6,"cHW":112.5,"cHB":33.6,"cHQ":-11.52,"cpHQ":156.2,"cHu":38.9,"cHd":-12.53}
}
