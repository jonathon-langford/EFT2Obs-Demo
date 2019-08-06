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

  'vbf':{
   'QQ2HQQ_VBFTOPO_JET3VETO':{'cHB': -0.29, 'cH': -1.0, 'cHd': 0.12, 'cB': -0.023, 'cWW': 1.3, 'cHQ': 0.092, 'cHu': -0.33, 'cHW': -4.3, 'cpHQ': -5.3, 'cT': -1.0},
   'QQ2HQQ_VBFTOPO_JET3':{'cHB': -0.41, 'cH': -1.0, 'cHd': 0.15, 'cB': -0.027, 'cWW': 1.2, 'cHQ': 0.13, 'cHu': -0.45, 'cHW': -5.8, 'cpHQ': -6.9, 'cT': -1.1},
   'QQ2HQQ_VH2JET':{'cHB': -0.42, 'cH': -1.0, 'cHd': 0.16, 'cB': -0.028, 'cWW': 1.4, 'cHQ': 0.14, 'cHu': -0.42, 'cHW': -6.2, 'cpHQ': -6.9, 'cT': -1.0},
   'QQ2HQQ_REST':{'cHB': -0.24, 'cH': -1.0, 'cHd': 0.1, 'cB': -0.025, 'cWW': 1.5, 'cHQ': 0.084, 'cHu': -0.25, 'cHW': -3.6, 'cpHQ': -4.5, 'cT': -0.95},
   'QQ2HQQ_PTJET1_GT200':{'cHB': -2.4, 'cH': -0.99, 'cHd': 0.9, 'cB': -0.19, 'cWW': 7.8, 'cHQ': 0.9, 'cHu': -2.8, 'cHW': -31.0, 'cpHQ': -38.0, 'cT': -1.2}
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
   'TTH':{'cH': -0.98, 'c3G': 27.0, 'cG': 0.93, 'cuG': 310.0, 'c2G': -13.0, 'cu': 2.9}
   }
}
