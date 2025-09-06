import numpy as np
import os
import matplotlib
import matplotlib.pyplot as plt
if os.environ.get("DISPLAY","") == "":
    print("No display found. Using non-interactive Agg backend.")
    matplotlib.use("Agg")  # headless backend
    
# Plot styling constants
LINEWIDTH = 2
FONTSIZE_LABEL = 14
FONTSIZE_TITLE = 14
FONTSIZE_TICKS = 14
FONTSIZE_LEGEND = 14
FONTSIZE_SUBTITLE = 16

def setup_plot_style(ax):
    """Apply consistent styling to plots"""
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='both', which='major', labelsize=FONTSIZE_TICKS)

def plot_grfs(time, grfs, grf_labels, experimental_grfs=None, save_path=None, display_plot=True):
    """
    Plot Ground Reaction Forces
    
    Parameters:
    -----------
    time : array
        Time vector
    grfs : array
        Ground reaction forces (6 x time_points)
    grf_labels : list
        Labels for each GRF component
    experimental_grfs : array, optional
        Experimental GRF data for comparison
    save_path : str, optional
        Path to save the figure
    """
    fig, axs = plt.subplots(2, 3, figsize=(15, 8))
    fig.suptitle('Ground Reaction Forces', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    for i, ax in enumerate(axs.flat):
        if i < len(grf_labels):
            # Plot experimental data if available
            if experimental_grfs is not None:
                ax.plot(time, experimental_grfs[i, :], 
                       c='black', linestyle='--', 
                       label='Experimental', linewidth=LINEWIDTH)
            
            # Plot simulation data
            ax.plot(time, grfs[i, :], 
                   c='tab:blue', label='Simulation', linewidth=LINEWIDTH)
            
            ax.set_title(grf_labels[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
            setup_plot_style(ax)
            
            # Add units
            ax.set_ylabel('Force (N)', fontsize=FONTSIZE_LABEL, fontweight='bold')
    
    # Add x-axis labels to bottom row
    for ax in axs[-1, :]:
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
    
    # Add legend
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', fontsize=FONTSIZE_LEGEND)
    
    # Adjust layout
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
   
    if os.environ.get("DISPLAY","") != "" and display_plot:  # Check if display is available
        plt.show() 
    return fig

def plot_muscle_activations(time, activations, muscle_names, emg_data=None, save_path=None):
    """
    Plot muscle activations
    
    Parameters:
    -----------
    time : array
        Time vector
    activations : array
        Muscle activations (n_muscles x time_points)
    muscle_names : list
        Names of muscles
    emg_data : array, optional
        EMG data for comparison
    save_path : str, optional
        Path to save the figure
    """
    n_muscles = len(muscle_names)
    n_cols = int(np.ceil(np.sqrt(n_muscles)))
    n_rows = int(np.ceil(n_muscles / n_cols))
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows))
    fig.suptitle('Muscle Activations', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    # Ensure axs is always 2D array
    if n_muscles == 1:
        axs = np.array([[axs]])
    elif axs.ndim == 1:
        axs = axs.reshape(1, -1)
    
    for i, ax in enumerate(axs.flat):
        if i < n_muscles:
            # Plot EMG data if available and not all NaN
            if emg_data is not None and not np.isnan(emg_data[i, :]).all():
                ax.plot(time, emg_data[i, :], 
                       c='black', linestyle='--', 
                       label='EMG', linewidth=LINEWIDTH)
            
            # Plot simulation data (remove last time point to match)
            ax.plot(time, activations[i, :-1], 
                   c='tab:red', label='Simulation', linewidth=LINEWIDTH)
            
            ax.set_title(muscle_names[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
            ax.set_ylim(0, 1)
            setup_plot_style(ax)
        else:
            # Remove empty subplots
            fig.delaxes(ax)
    
    # Add labels to bottom row and left column
    for i in range(n_muscles):
        row, col = divmod(i, n_cols)
        if row == n_rows - 1 or i >= n_muscles - n_cols:  # Bottom row
            axs[row, col].set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
        if col == 0:  # Left column
            axs[row, col].set_ylabel('Activation', fontsize=FONTSIZE_LABEL, fontweight='bold')
    
    # Clean up x-tick labels for non-bottom plots
    for i in range(n_muscles):
        row, col = divmod(i, n_cols)
        if row < n_rows - 1 and i < n_muscles - n_cols:
            axs[row, col].set_xticklabels([])
    
    # Add legend
    handles, labels = [], []
    for ax in axs.flat:
        if ax.get_legend_handles_labels()[0]:  # If there are handles
            handles, labels = ax.get_legend_handles_labels()
            break
    if handles:
        fig.legend(handles, labels, loc='upper right', fontsize=FONTSIZE_LEGEND)
    
    # Adjust layout
    fig.tight_layout()
    fig.subplots_adjust(top=0.9, hspace=0.4, wspace=0.4)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show()
    return fig

def plot_joint_coordinates(time, coordinates, coord_names, tracked_coords=None, 
                          rotational_coords=None, save_path=None):
    """
    Plot joint coordinate values (angles and positions)
    
    Parameters:
    -----------
    time : array
        Time vector
    coordinates : array
        Joint coordinate values
    coord_names : list
        Names of coordinates
    tracked_coords : array, optional
        Ground truth tracked data for comparison
    rotational_coords : list, optional
        List of rotational coordinate names (for degree conversion)
    save_path : str, optional
        Path to save the figure
    """
    n_coords = len(coord_names)
    n_cols = int(np.ceil(np.sqrt(n_coords)))
    n_rows = int(np.ceil(n_coords / n_cols))
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows))
    fig.suptitle('Joint Coordinates', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    # Ensure axs is always 2D array
    if n_coords == 1:
        axs = np.array([[axs]])
    elif axs.ndim == 1:
        axs = axs.reshape(1, -1)
    
    for i, ax in enumerate(axs.flat):
        if i < n_coords:
            # Determine if this is a rotational coordinate (convert to degrees)
            if rotational_coords and coord_names[i] in rotational_coords:
                scale = 180 / np.pi
                unit = '(deg)'
            else:
                scale = 1
                unit = '(m)'
            
            # Plot tracked data if available
            if tracked_coords is not None:
                ax.plot(time, tracked_coords[i, :] * scale, 
                       c='black', linestyle=':', 
                       label='Tracked (OpenCap)', linewidth=LINEWIDTH)
            
            # Plot simulation data (remove last time point to match)
            ax.plot(time, coordinates[i, :-1] * scale, 
                   c='tab:blue', label='Dynamic Simulation', linewidth=LINEWIDTH)
            
            ax.set_title(coord_names[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
            ax.set_ylabel(unit, fontsize=FONTSIZE_LABEL, fontweight='bold')
            setup_plot_style(ax)
        else:
            fig.delaxes(ax)
    
    # Add labels and clean up
    for i in range(n_coords):
        row, col = divmod(i, n_cols)
        if row == n_rows - 1 or i >= n_coords - n_cols:
            axs[row, col].set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
        if row < n_rows - 1 and i < n_coords - n_cols:
            axs[row, col].set_xticklabels([])
    
    # Add legend
    handles, labels = [], []
    for ax in axs.flat:
        if ax.get_legend_handles_labels()[0]:
            handles, labels = ax.get_legend_handles_labels()
            break
    if handles:
        fig.legend(handles, labels, loc='upper right', fontsize=FONTSIZE_LEGEND)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.9, hspace=0.4, wspace=0.4)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show()
    return fig

def plot_joint_speeds(time, speeds, coord_names, tracked_speeds=None, 
                     rotational_coords=None, save_path=None):
    """
    Plot joint coordinate speeds (angular velocities and linear velocities)
    """
    n_coords = len(coord_names)
    n_cols = int(np.ceil(np.sqrt(n_coords)))
    n_rows = int(np.ceil(n_coords / n_cols))
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows))
    fig.suptitle('Joint Coordinate Speeds', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    if n_coords == 1:
        axs = np.array([[axs]])
    elif axs.ndim == 1:
        axs = axs.reshape(1, -1)
    
    for i, ax in enumerate(axs.flat):
        if i < n_coords:
            if rotational_coords and coord_names[i] in rotational_coords:
                scale = 180 / np.pi
                unit = '(deg/s)'
            else:
                scale = 1
                unit = '(m/s)'
            
            if tracked_speeds is not None:
                ax.plot(time, tracked_speeds[i, :] * scale, 
                       c='black', linestyle=':', 
                       label='Tracked (OpenCap)', linewidth=LINEWIDTH)
            
            ax.plot(time, speeds[i, :-1] * scale, 
                   c='tab:orange', label='Dynamic Simulation', linewidth=LINEWIDTH)
            
            ax.set_title(coord_names[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
            ax.set_ylabel(unit, fontsize=FONTSIZE_LABEL, fontweight='bold')
            setup_plot_style(ax)
        else:
            fig.delaxes(ax)
    
    # Add labels and clean up
    for i in range(n_coords):
        row, col = divmod(i, n_cols)
        if row == n_rows - 1 or i >= n_coords - n_cols:
            axs[row, col].set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
        if row < n_rows - 1 and i < n_coords - n_cols:
            axs[row, col].set_xticklabels([])
    
    # Add legend
    handles, labels = [], []
    for ax in axs.flat:
        if ax.get_legend_handles_labels()[0]:
            handles, labels = ax.get_legend_handles_labels()
            break
    if handles:
        fig.legend(handles, labels, loc='upper right', fontsize=FONTSIZE_LEGEND)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.9, hspace=0.4, wspace=0.4)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show()
    return fig

def plot_joint_torques(time, torques, coord_names, mocap_torques=None, save_path=None):
    """
    Plot joint torques/moments
    """
    n_coords = len(coord_names)
    n_cols = int(np.ceil(np.sqrt(n_coords)))
    n_rows = int(np.ceil(n_coords / n_cols))
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows))
    fig.suptitle('Joint Torques', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    if n_coords == 1:
        axs = np.array([[axs]])
    elif axs.ndim == 1:
        axs = axs.reshape(1, -1)
    
    for i, ax in enumerate(axs.flat):
        if i < n_coords:
            # Plot mocap-based inverse dynamics if available
            if mocap_torques is not None:
                ax.plot(time, mocap_torques[i, :], 
                       c='black', linestyle='--', 
                       label='Mocap-based ID', linewidth=LINEWIDTH)
            
            ax.plot(time, torques[i, :], 
                   c='tab:red', label='OpenCap Analysis', linewidth=LINEWIDTH)
            
            ax.set_title(coord_names[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
            ax.set_ylabel('(N⋅m)', fontsize=FONTSIZE_LABEL, fontweight='bold')
            setup_plot_style(ax)
        else:
            fig.delaxes(ax)
    
    # Add labels
    for i in range(n_coords):
        row, col = divmod(i, n_cols)
        if row == n_rows - 1 or i >= n_coords - n_cols:
            axs[row, col].set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
        if row < n_rows - 1 and i < n_coords - n_cols:
            axs[row, col].set_xticklabels([])
    
    # Add legend if there are comparison data
    if mocap_torques is not None:
        handles, labels = [], []
        for ax in axs.flat:
            if ax.get_legend_handles_labels()[0]:
                handles, labels = ax.get_legend_handles_labels()
                break
        if handles:
            fig.legend(handles, labels, loc='upper right', fontsize=FONTSIZE_LEGEND)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.9, hspace=0.4, wspace=0.4)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show()
    return fig

def plot_joint_powers(time, powers, coord_names, save_path=None):
    """
    Plot joint powers
    """
    n_coords = len(coord_names)
    n_cols = int(np.ceil(np.sqrt(n_coords)))
    n_rows = int(np.ceil(n_coords / n_cols))
    
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(4*n_cols, 3*n_rows))
    fig.suptitle('Joint Powers', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    if n_coords == 1:
        axs = np.array([[axs]])
    elif axs.ndim == 1:
        axs = axs.reshape(1, -1)
    
    for i, ax in enumerate(axs.flat):
        if i < n_coords:
            ax.plot(time, powers[i, :], 
                   c='tab:green', linewidth=LINEWIDTH)
            ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)  # Zero line
            
            ax.set_title(coord_names[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
            ax.set_ylabel('(W)', fontsize=FONTSIZE_LABEL, fontweight='bold')
            setup_plot_style(ax)
        else:
            fig.delaxes(ax)
    
    # Add labels
    for i in range(n_coords):
        row, col = divmod(i, n_cols)
        if row == n_rows - 1 or i >= n_coords - n_cols:
            axs[row, col].set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
        if row < n_rows - 1 and i < n_coords - n_cols:
            axs[row, col].set_xticklabels([])
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.9, hspace=0.4, wspace=0.4)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show()
    return fig

def plot_kam(time, kam, kam_labels, save_path=None):
    """
    Plot Knee Adduction Moments
    """
    fig, axs = plt.subplots(1, len(kam_labels), figsize=(5*len(kam_labels), 4))
    fig.suptitle('Knee Adduction Moments (KAM)', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    if len(kam_labels) == 1:
        axs = [axs]
    
    for i, ax in enumerate(axs):
        ax.plot(time, kam[i, :], 
               c='tab:purple', linewidth=LINEWIDTH)
        ax.axhline(y=0, color='gray', linestyle='-', alpha=0.3)
        
        ax.set_title(kam_labels[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
        ax.set_ylabel('(N⋅m)', fontsize=FONTSIZE_LABEL, fontweight='bold')
        ax.set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
        setup_plot_style(ax)
    
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show()
    return fig

def plot_cops(time, cops, cop_labels, save_path=None):
    """
    Plot Centers of Pressure
    
    Parameters:
    -----------
    time : array
        Time vector
    cops : array
        Center of pressure data
    cop_labels : list
        Labels for COP components
    save_path : str, optional
        Path to save the figure
    """
    n_cops = len(cop_labels)
    
    if n_cops == 6:  # Assuming 6 components (3 per foot)
        fig, axs = plt.subplots(2, 3, figsize=(15, 8))
        fig.suptitle('Centers of Pressure', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    else:
        # Adjust subplot layout based on number of COP components
        n_cols = min(3, n_cops)
        n_rows = int(np.ceil(n_cops / n_cols))
        fig, axs = plt.subplots(n_rows, n_cols, figsize=(5*n_cols, 4*n_rows))
        fig.suptitle('Centers of Pressure', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
    
    # Ensure axs is always iterable
    if n_cops == 1:
        axs = [axs]
    elif axs.ndim == 1 and n_cops > 3:
        axs = axs.reshape(-1, 3) if n_cops > 3 else axs
    
    for i, ax in enumerate(axs.flat if hasattr(axs, 'flat') else axs):
        if i < n_cops:
            ax.plot(time, cops[i, :], 
                   c='tab:green', label='Simulation', linewidth=LINEWIDTH)
            
            ax.set_title(cop_labels[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
            setup_plot_style(ax)
            
            # Add units (assuming meters)
            ax.set_ylabel('Position (m)', fontsize=FONTSIZE_LABEL, fontweight='bold')
    
    # Add x-axis labels
    if hasattr(axs, 'flat'):
        for ax in axs.flat:
            if ax.has_data():
                ax.set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
    else:
        axs[-1].set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
    
    # Adjust layout
    fig.tight_layout()
    fig.subplots_adjust(top=0.9)
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)
    
    plt.show()
    return fig

def clean_labels(labels, data_type='COP'):
    """
    Clean up labels to be more readable
    
    Parameters:
    -----------
    labels : list
        Original labels from OpenCap
    data_type : str
        Type of data ('COP', 'GRF', 'GRM')
    
    Returns:
    --------
    list : Cleaned labels
    """
    cleaned = []
    
    for label in labels:
        if data_type == 'COP':
            # Handle Center of Pressure labels
            # ground_force_left_px -> CoP L_x
            if 'ground_force' in label:
                if 'left' in label:
                    side = 'L'
                elif 'right' in label:
                    side = 'R'
                else:
                    side = ''
                
                if label.endswith('px'):
                    axis = 'x'
                elif label.endswith('py'):
                    axis = 'y'
                elif label.endswith('pz'):
                    axis = 'z'
                else:
                    axis = label.split('_')[-1]
                
                cleaned.append(f'CoP {side}_{axis}')
            else:
                cleaned.append(label)
                
        elif data_type == 'GRF':
            # Handle Ground Reaction Force labels
            # ground_force_right_vx -> GRF R_x
            if 'ground_force' in label:
                if 'left' in label:
                    side = 'L'
                elif 'right' in label:
                    side = 'R'
                else:
                    side = ''
                
                if label.endswith('vx'):
                    axis = 'x'
                elif label.endswith('vy'):
                    axis = 'y'
                elif label.endswith('vz'):
                    axis = 'z'
                else:
                    axis = label.split('_')[-1]
                
                cleaned.append(f'GRF {side}_{axis}')
            else:
                cleaned.append(label)
                
        elif data_type == 'GRM':
            # Handle Ground Reaction Moment labels
            if 'ground_force' in label:
                if 'left' in label:
                    side = 'L'
                elif 'right' in label:
                    side = 'R'
                else:
                    side = ''
                
                # Assuming similar pattern for moments
                axis = label.split('_')[-1][-1]  # Get last character
                cleaned.append(f'GRM {side}_{axis}')
            else:
                cleaned.append(label)
        else:
            cleaned.append(label)
    
    return cleaned

def extract_dynamics(results_path, display_plot=True, save_plots=False, output_dir=None):
    """
    Extract and optionally plot dynamics data from OpenCap results
    
    Parameters:
    -----------
    results_path : str
        Path to the optimaltrajectories.npy file
    plot : bool
        Whether to generate plots
    save_plots : bool
        Whether to save plots to files
    output_dir : str, optional
        Directory to save plots (defaults to same dir as results)
    
    Returns:
    --------
    dict : Extracted data dictionary
    """
    # Load data
    data = np.load(results_path, allow_pickle=True).item()
    
    # Extract the first case (assuming single case analysis)
    results = data[list(data.keys())[0]]  # More robust than assuming '0' key
    
    # Extract time vector (remove last point to match data dimensions)
    time = results['time'][0, :-1]
    
    # Set up output directory for plots
    if save_plots and output_dir is None:
        output_dir = os.path.join(os.path.dirname(results_path), 'plots')
        os.makedirs(output_dir, exist_ok=True)
    
    extracted_data = {
        'time': time,
        'results': results
    }
    
    # Print available data info
    print("Available biomechanics data:")
    print(f"  • Ground Reaction Forces: {'✓' if 'GRF' in results else '✗'}")
    print(f"  • Ground Reaction Moments: {'✓' if 'GRM' in results else '✗'}")
    print(f"  • Centers of Pressure: {'✓' if 'COP' in results else '✗'}")
    print(f"  • Muscle Activations: {'✓' if 'muscle_activations' in results else '✗'}")
    print(f"  • Joint Torques: {'✓' if 'torques' in results else '✗'}")
    print(f"  • Joint Kinematics: {'✓' if 'coordinate_values' in results else '✗'}")
    print(f"  • Knee Adduction Moment (KAM): {'✓' if 'KAM' in results else '✗'}")
    print(f"  • Medial Compartment Force (MCF): {'✓' if 'MCF' in results else '✗'}")
    
    # Plot Ground Reaction Forces
    if 'GRF' in results and 'GRF_labels' in results:
        grf_exp = results.get('GRF_experimental', None)
        save_path = os.path.join(output_dir, 'ground_reaction_forces.png') if save_plots else None
        
        # Clean up GRF labels
        clean_grf_labels = clean_labels(results['GRF_labels'], 'GRF')
        plot_grfs(time, results['GRF'], clean_grf_labels, 
                    experimental_grfs=grf_exp, save_path=save_path, display_plot=display_plot)
        
        print("✓ Plotted Ground Reaction Forces")
    
        # Plot Joint Coordinates (Kinematics)
        if 'coordinate_values' in results and 'coordinates' in results:
            tracked_coords = results.get('coordinate_values_toTrack', None)
            rotational_coords = results.get('rotationalCoordinates', [])
            save_path = os.path.join(output_dir, 'joint_coordinates.png') if save_plots else None
            
            plot_joint_coordinates(time, results['coordinate_values'], 
                                 results['coordinates'], tracked_coords=tracked_coords,
                                 rotational_coords=rotational_coords, save_path=save_path)
            
            print("✓ Plotted Joint Coordinates")
        
        # Plot Joint Speeds
        if 'coordinate_speeds' in results and 'coordinates' in results:
            tracked_speeds = results.get('coordinate_speeds_toTrack', None)
            rotational_coords = results.get('rotationalCoordinates', [])
            save_path = os.path.join(output_dir, 'joint_speeds.png') if save_plots else None
            
            plot_joint_speeds(time, results['coordinate_speeds'], 
                            results['coordinates'], tracked_speeds=tracked_speeds,
                            rotational_coords=rotational_coords, save_path=save_path)
            
            print("✓ Plotted Joint Speeds")
        
        # Plot Joint Torques
        if 'torques' in results and 'coordinates' in results:
            save_path = os.path.join(output_dir, 'joint_torques.png') if save_plots else None
            
            plot_joint_torques(time, results['torques'], results['coordinates'], 
                             save_path=save_path)
            
            print("✓ Plotted Joint Torques")
        
        # Plot Joint Powers
        if 'powers' in results and 'coordinates_power' in results:
            save_path = os.path.join(output_dir, 'joint_powers.png') if save_plots else None
            
            plot_joint_powers(time, results['powers'], results['coordinates_power'], 
                            save_path=save_path)
            
            print("✓ Plotted Joint Powers")
        
        # Plot Knee Adduction Moments (KAM)
        if 'KAM' in results and 'KAM_labels' in results:
            save_path = os.path.join(output_dir, 'knee_adduction_moments.png') if save_plots else None
            
            plot_kam(time, results['KAM'], results['KAM_labels'], save_path=save_path)
            
            print("✓ Plotted Knee Adduction Moments (KAM)")
        
        # Plot Muscle Activations
        if 'muscle_activations' in results and 'muscles' in results:
            emg_data = results.get('muscle_activations_emg', None)
            save_path = os.path.join(output_dir, 'muscle_activations.png') if save_plots else None
            
            plot_muscle_activations(time, results['muscle_activations'], 
                                  results['muscles'], emg_data=emg_data, 
                                  save_path=save_path)
            
            print("✓ Plotted Muscle Activations")
        
        # Plot Centers of Pressure
        if 'COP' in results and 'COP_labels' in results:
            save_path = os.path.join(output_dir, 'centers_of_pressure.png') if save_plots else None
            
            # Clean up COP labels
            clean_cop_labels = clean_labels(results['COP_labels'], 'COP')
            plot_cops(time, results['COP'], clean_cop_labels, 
                     save_path=save_path)
            
            print("✓ Plotted Centers of Pressure")
            
        # Plot Ground Reaction Moments (if available)
        if 'GRM' in results and 'GRM_labels' in results:
            save_path = os.path.join(output_dir, 'ground_reaction_moments.png') if save_plots else None
            clean_grm_labels = clean_labels(results['GRM_labels'], 'GRM')
            
            # Use the same plotting function as GRF but with moment units
            fig, axs = plt.subplots(2, 3, figsize=(15, 8))
            fig.suptitle('Ground Reaction Moments', fontsize=FONTSIZE_SUBTITLE, fontweight='bold')
            
            for i, ax in enumerate(axs.flat):
                if i < len(clean_grm_labels):
                    ax.plot(time, results['GRM'][i, :], 
                           c='tab:purple', label='Simulation', linewidth=LINEWIDTH)
                    ax.set_title(clean_grm_labels[i], fontsize=FONTSIZE_TITLE, fontweight='bold')
                    setup_plot_style(ax)
                    ax.set_ylabel('Moment (N⋅m)', fontsize=FONTSIZE_LABEL, fontweight='bold')
            
            for ax in axs[-1, :]:
                ax.set_xlabel('Time (s)', fontsize=FONTSIZE_LABEL, fontweight='bold')
            
            fig.tight_layout()
            fig.subplots_adjust(top=0.9)
            
            if save_path:
                plt.savefig(save_path, bbox_inches='tight', dpi=300)
            plt.show()
            
            print("✓ Plotted Ground Reaction Moments")
    
    return extracted_data

if __name__ == '__main__':
    results_path = 'Data/Extracted_Data/S7_T2/optimaltrajectories.npy'
    
    # Extract and plot data
    data = extract_dynamics(results_path, display_plot=False, save_plots=True)
    
    # Access extracted data
    print(f"Time range: {data['time'][0]:.2f} - {data['time'][-1]:.2f} seconds")
    print(f"Available data keys: {list(data['results'].keys())}")