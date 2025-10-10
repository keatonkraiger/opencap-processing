# %% Directories, paths, and imports. You should not need to change anything.
import os
import pickle
import sys
import argparse
import time
import shutil as sh

baseDir = os.getcwd()
opensimADDir = os.path.join(baseDir, 'UtilsDynamicSimulations', 'OpenSimAD')
sys.path.append(baseDir)
sys.path.append(opensimADDir)


from utilsOpenSimAD import plotResultsOpenSimAD_custom
from custom_functions import processInputsOpenSimAD_custom, load_trc
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
    session_id = args.session_id
    case =  '0'
    motion_type = 'other'
    trial_name = args.session_id
    time_window = [args.start_time, args.stop_time]
    data_path = args.data_path
    overwrite = not args.no_overwrite
    input_hz = args.input_hz
     
    if args.use_marker_contact:
        # Load the trc file
        trc_file = os.path.join(data_path, 'MarkerData', f'{trial_name}.trc')
        if not os.path.exists(trc_file):
            raise FileNotFoundError(f"TRC file not found at {trc_file}. Please provide a valid path if using mocap for contact placement.")
        marker_times, markers = load_trc(trc_file, scale=1)
        if marker_times[0] > time_window[0] or marker_times[-1] < time_window[1]:
            raise ValueError(f"TRC file time range ({marker_times[0]} to {marker_times[-1]}) does not cover the specified time_window ({time_window[0]} to {time_window[1]}). Please provide a TRC file that covers the full time window.")
       
        indices = (marker_times >= time_window[0]) & (marker_times <= time_window[1])
        marker_data = {}
        for marker in markers:
            marker_data[marker] = markers[marker][indices, :]
    else:
        marker_data = None
        
    
    solveProblem = True
    analyzeResults = True
    repetition = None
    treadmill_speed = 0
    contact_side = 'all'
        
    session_details = {
        "session_id": session_id,
        "trial_name": trial_name,
        "motion_type": motion_type,
        "time_window": time_window,
        "repetition": repetition,
        "treadmill_speed": treadmill_speed,
        "contact_side": contact_side,
        "multiple_contacts": args.multiple_contacts,
    }
    for key, value in session_details.items():
        print(f"{key}: {value}")

    # Create output directory
    output_dir = os.path.join('Results', data_path)
    if time_window:
        output_dir += f'/{int(time_window[0])}-{int(time_window[1])}s'
    os.makedirs(output_dir, exist_ok=True)
    
    start_time = time.time() 
    settings = processInputsOpenSimAD_custom(baseDir, data_path, session_id, trial_name, 
                                    motion_type, time_window, repetition, 
                                    treadmill_speed, contact_side, overwrite=overwrite, multiple_contacts=args.multiple_contacts, marker_data=marker_data)

    settings['session_details'] = session_details
    settings['start_time'] = start_time
    # N = time elapsed * data hz
    settings['N'] = int(round((time_window[1]-time_window[0]) * input_hz, 2))
    settings['torque_driven_model'] = args.torque_driven_model
    # Save settings 
    with open(os.path.join(output_dir, 'settings.pkl'), 'wb') as f:
        pickle.dump(settings, f)
    
    run_tracking_custom(baseDir, data_path, session_id, settings, case=case, 
                solveProblem=solveProblem, analyzeResults=analyzeResults, output_dir=output_dir)
       
    # Copy the OpenSimData to the output folder
    osim_dir = os.path.join(baseDir, data_path, session_id, 'OpenSimData')
    sh.copytree(osim_dir, os.path.join(output_dir, 'OpenSimData'), dirs_exist_ok=True)
     
    # To compare different cases, add to the cases list, eg cases=['0','1'].
    plotResultsOpenSimAD_custom(data_path, session_id, settings, output_path=output_dir, cases=['0'])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run OpenSimAD simulations.')
    parser.add_argument('--data_path', type=str, default='',
                        help="Path to the session folder. If empty, will use session_id.")
    parser.add_argument('--session_id', type=str, required=True,
                            help="Session ID")
    parser.add_argument('--start_time', type=float, default=0.0, help="Time of the 20s clippet to run. Start with a few seconds.")
    parser.add_argument('--stop_time', type=float, default=5.0, help="Time of the 20s clippet to run. Start with a few seconds.")
    parser.add_argument('--multiple_contacts', action='store_true', help="Use multiple contact planes under feet")
    parser.add_argument('--use_marker_contact', action='store_true',
                        help="Use marker data to position contact planes")
    parser.add_argument('--no_overwrite', action='store_true',
                        help="Do not overwrite existing results") 
    parser.add_argument('--input_hz', type=float, default=50.0,
                        help="Hz of input data. Default is 50Hz")
    parser.add_argument('--torque_driven_model', action='store_true',
                        help="Use a torque driven model instead of muscle driven")
    args = parser.parse_args()
    main(args)
