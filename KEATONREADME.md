Again, this code is laborious and annoying to work with. I've made custom files that make the original ones more general. They can be run from psu_tmm.py.

## Installation

Follow the README instructions on all the stuff you'll need to download. I would also suggest running the example_kinetics.py script to see it on their data.

## Running our data

I've put a small snippet of subject 7 take 2's taiji in Data. You can run their pipeline with:

```
python psu_tmm.py --data_path Data/PSUTMM/Subject7/Take_2 --session_id Take_2_segment_4 --start_time 192 --stop_time 198 --multiple_contacts --use_marker_contact --torque_driven_model 
```

There is also subject 7 take 2's data downsampled to 10hz.

```
python psu_tmm.py --data_path Data/PSUTMM/Subject7/Take_2 --session_id Take_2_10hz --multiple_contacts --use_marker_contact --start_time x --stop_time y --torque_driven_model
```

See the arguments in the file to see some of the options I've included. its mostly hardcoded now.

## Extracting GRF results

```python
dict_keys(['coordinate_values_toTrack', 'coordinate_values', 'coordinate_speeds_toTrack', 'coordinate_speeds', 'coordinate_accelerations_toTrack', 'coordinate_accelerations', 'torques', 'torques_BWht', 'powers', 'GRF', 'GRF_BW', 'GRM', 'GRM_BWht', 'COP', 'freeM', 'coordinates', 'coordinates_power', 'rotationalCoordinates', 'GRF_labels', 'GRM_labels', 'COP_labels', 'time', 'muscles', 'passive_limit_torques', 'muscle_driven_joints', 'limit_torques_joints', 'KAM', 'KAM_BWht', 'KAM_labels', 'MCF', 'MCF_BW', 'MCF_labels', 'iter', 'muscle_activations', 'muscle_forces', 'passive_muscle_torques'])
```