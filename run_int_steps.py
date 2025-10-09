import os
import sys
import numpy as np
import subprocess

# --- Setup paths ---
baseDir = os.getcwd()
opensimADDir = os.path.join(baseDir, 'UtilsDynamicSimulations', 'OpenSimAD')
sys.path.append(baseDir)
sys.path.append(opensimADDir)

from custom_functions import load_trc

# --- TRC segment files ---
trc_files = [
    '/scratch/kbk5531/Research/Bio/opencap-processing/Data/PSUTMM/Subject7/Take_2/MarkerData/Take_2_10hz_segment_0.trc',
    '/scratch/kbk5531/Research/Bio/opencap-processing/Data/PSUTMM/Subject7/Take_2/MarkerData/Take_2_10hz_segment_1.trc'
]

# --- Command template ---
command_template = (
    "python psu_tmm.py "
    "--data_path Data/PSUTMM/Subject7/Take_2 "
    "--session_id {session_id} "
    "--multiple_contacts "
    "--use_marker_contact "
    "--start_time {start} "
    "--stop_time {stop} "
    "--torque_driven_model"
)

# --- Parameters ---
session_base = "Take_2_10hz"
step = 10.0  # seconds

for idx, trc_file in enumerate(trc_files):
    print(f"\n=== Processing segment {idx}: {trc_file} ===")
    times, _ = load_trc(trc_file, scale=1)

    start_time = times[0]
    stop_time = times[-1]

    # Build 10-second chunks
    segments = np.arange(start_time, stop_time, step)
    if segments[-1] < stop_time:
        segments = np.append(segments, stop_time)

    # Build session ID (so outputs don’t overwrite)
    session_id = f"{session_base}_segment_{idx}"

    # Run command per chunk
    for i in range(len(segments) - 1):
        start = segments[i]
        stop = segments[i + 1]

        cmd = command_template.format(
            session_id=session_id,
            start=start,
            stop=stop
        )
        print(f"\n>>> Running: {cmd}")
        subprocess.run(cmd, shell=True, check=True)
