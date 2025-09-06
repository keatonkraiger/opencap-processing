import pickle
import sys
import os

baseDir = os.getcwd()
opensimADDir = os.path.join(baseDir, 'UtilsDynamicSimulations', 'OpenSimAD')
sys.path.append(baseDir)
sys.path.append(opensimADDir)

data_folder = 'Data/PSUTMM/Subject7/Take_2'
base_dir = '/mnt/e/Research/Bio/Code_bases/opencap-processing'
session_id = 'Take_2_segment_0_ik'
case = ['0']
solve_problem = True
analyze_results = True
trial_name = 'STS'


from utilsOpenSimAD import plotResultsOpenSimAD_custom

with open('settings_test.pkl', 'rb') as f:
    settings = pickle.load(f)

plotResultsOpenSimAD_custom(dataDir=data_folder, motion_filename=trial_name,
                            settings=settings, cases=case)
