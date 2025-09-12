# %% Directories, paths, and imports. You should not need to change anything.
import os
import sys
import argparse
import time

baseDir = os.getcwd()
opensimADDir = os.path.join(baseDir, 'UtilsDynamicSimulations', 'OpenSimAD')
sys.path.append(baseDir)
sys.path.append(opensimADDir)


from utilsOpenSimAD import plotResultsOpenSimAD, plotResultsOpenSimAD_custom
from custom_functions import processInputsOpenSimAD_custom
from custom_run import run_tracking_custom

# %% User inputs.
'''
Please provide:
    
    session_id:     This is a 36 character-long string. You can find the ID of
                    all your sessions at https://app.opencap.ai/sessions.
                    
    trial_name:     This is the name of the trial you want to simulate. You can
                    find all trial names after loading a session.
                    
    motion_type:    This is the type of activity you want to simulate. Options
                    are 'running', 'walking', 'drop_jump', 'sit-to-stand', and
                    'squats'. We provide pre-defined settings that worked well
                    for this set of activities. If your activity is different,
                    select 'other' to use generic settings or set your own
                    settings in settingsOpenSimAD. See for example how we tuned
                    the 'running' settings to include periodic constraints in
                    the 'my_periodic_running' settings.
                    
    time_window:    This is the time interval you want to simulate. It is
                    recommended to simulate trials shorter than 2s. Set to []
                    to simulate full trial. For 'squats' or 'sit_to_stand', we
                    built segmenters to separate the different repetitions. In
                    such case, instead of providing the time_window, you can
                    provide the index of the repetition (see below) and the
                    time_window will be automatically computed.
                    
    repetition:     Only if motion_type is 'sit_to_stand' or 'squats'. This
                    is the index of the repetition you want to simulate (0 is 
                    first). There is no need to set the time_window. 
                    
    case:           This is a string that will be appended to the file names
                    of the results. Dynamic simulations are optimization
                    problems, and it is common to have to play with some
                    settings to get the problem to converge or converge to a
                    meaningful solution. It is useful to keep track of which
                    solution corresponds to which settings; you can then easily
                    compare results generated with different settings.
                    
    (optional)
    treadmill_speed:This an optional parameter that indicates the speed of
                    the treadmill in m/s. A positive value indicates that the
                    subject is moving forward. You should ignore this parameter
                    or set it to 0 if the trial was not measured on a
                    treadmill. By default, treadmill_speed is set to 0.
    (optional)
    contact_side:   This an optional parameter that indicates on which foot to
                    add contact spheres to model foot-ground contact. It might
                    be useful to only add contact spheres on one foot if only
                    that foot is in contact with the ground. We found this to
                    be helpful for simulating for instance single leg dropjump
                    as it might prevent the optimizer to cheat by using the
                    other foot to stabilize the model. Options are 'all', 
                    'left', and 'right'. By default, contact_side is set to
                    'all', meaning that contact spheres are added to both feet.
    
See example inputs below for different activities. Please note that we did not
verify the biomechanical validity of the results; we only made sure the
simulations converged to kinematic solutions that were visually reasonable.

Please contact us for any questions: https://www.opencap.ai/#contact
'''

def main(args):
    session_type = args.session_type
    session_id = args.session_id
    case = args.case if 'case' in args else '0'
    
    # Options are 'squat', 'STS', and 'jump'.
    if session_type == 'overground': 
        trial_name = args.trial_name
        if trial_name == 'squat': # Squat
            motion_type = 'squats'
            repetition = 1
        elif trial_name == 'STS': # Sit-to-stand        
            motion_type = 'sit_to_stand'
            time_window = [0.0,args.time]
        elif trial_name == 'jump': # Jump  
            motion_type = 'jumping'
            time_window = [1.3, 2.2]
        else:
            motion_type = 'other'
            time_window = [args.start_time, args.stop_time]
    # Options are 'walk_1_25ms', 'run_2_5ms', and 'run_4ms'.
    elif session_type == 'treadmill': 
        #trial_name = 'walk_1_25ms'
        trial_name = 'Take_2_segment_0_ik'
        torque_driven_model = False # Example with torque-driven model.
        if trial_name == 'walk_1_25ms': # Walking, 1.25 m/s
            motion_type = 'walking'
            time_window = [1.0, 2.5]
            treadmill_speed = 1.25
        elif 'Take' in trial_name: # Walking, 1.25 m/s
            motion_type = 'walking'
            time_window = [4.0, 5.0]
            treadmill_speed = 1.25   
        elif trial_name == 'run_2_5ms': # Running, 2.5 m/s
            if torque_driven_model:
                motion_type = 'running_torque_driven'
            else:
                motion_type = 'running'
            time_window = [1.4, 2.6]
            treadmill_speed = 2.5
        elif trial_name == 'run_4ms': # Running with periodic constraints, 4.0 m/s
            motion_type = 'my_periodic_running'
            time_window = [3.1833333, 3.85]
            treadmill_speed = 4.0
        
    # Set to True to solve the optimal control problem.
    solveProblem = True
    # Set to True to analyze the results of the optimal control problem. If you
    # solved the problem already, and only want to analyze/process the results, you
    # can set solveProblem to False and run this script with analyzeResults set to
    # True. This is useful if you do additional post-processing but do not want to
    # re-run the problem.
    analyzeResults = True

    # Path to where you want the data to be downloaded.

    # %% Setup. 
    if not 'time_window' in locals():
        time_window = None
    if not 'repetition' in locals():
        repetition = None
    if not 'treadmill_speed' in locals():
        treadmill_speed = 0
    if not 'contact_side' in locals():
        contact_side = 'all'
        
    dataFolder = args.session_path
    session_details = {
        "session_id": session_id,
        "trial_name": trial_name,
        "motion_type": motion_type,
        "time_window": time_window,
        "repetition": repetition,
        "treadmill_speed": treadmill_speed,
        "contact_side": contact_side,
        "multiple_contacts": args.multiple_contacts
    }
    for key, value in session_details.items():
        print(f"{key}: {value}")
     
    start_time = time.time() 
    settings = processInputsOpenSimAD_custom(baseDir, dataFolder, session_id, trial_name, 
                                    motion_type, time_window, repetition,
                                    treadmill_speed, contact_side, overwrite=True, subject=args.subject, multiple_contacts=args.multiple_contacts)
    
    settings['session_details'] = session_details
    settings['start_time'] = start_time
    
    run_tracking_custom(baseDir, dataFolder, session_id, settings, case=case, 
                solveProblem=solveProblem, analyzeResults=analyzeResults)

    # Save settings 
    import pickle
    with open('settings_test.pkl', 'wb') as f:
        pickle.dump(settings, f)
        
    # To compare different cases, add to the cases list, eg cases=['0','1'].
    plotResultsOpenSimAD_custom(dataFolder, session_id, trial_name, settings, cases=[case])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run OpenSimAD simulations.')
    parser.add_argument('--session_type', type=str, default='overground', 
                        choices=['overground', 'treadmill'], help="Overground or treadmill")
    parser.add_argument('--session_path', type=str, default='',
                        help="Path to the session folder. If empty, will use session_id.")
    parser.add_argument('--session_id', type=str, required=True,
                            help="Session ID")
    parser.add_argument('--case', type=str, default='0',help="Case ID")
    parser.add_argument('--start_time', type=float, default=0.0, help="Time of the 20s clippet to run. Start with a few seconds.")
    parser.add_argument('--trial_name', type=str, default='STS', help="Trial name")
    parser.add_argument('--stop_time', type=float, default=5.0, help="Time of the 20s clippet to run. Start with a few seconds.")
    parser.add_argument('--subject', type=str, default='1', help="Subject ID")
    parser.add_argument('--multiple_contacts', action='store_true', help="Use multiple contact planes under feet")
    args = parser.parse_args()
    main(args)
