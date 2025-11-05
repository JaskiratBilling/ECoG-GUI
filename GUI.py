#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import h5py
from scipy import signal as sig
import os
import json

class FileSelectionDialog:
    RECENT_FILES_FILE = 'recent_files.json'
    MAX_RECENT_FILES = 3
    
    def __init__(self, root):
        self.root = root
        self.root.title("ECoG GUI - File Selection")
        self.root.geometry("600x475")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Selected file path
        self.selected_file = None
        
        # Load recent files
        self.recent_files = self.load_recent_files()
        
        # Create GUI
        self.create_gui()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_gui(self):
        """Create the file selection GUI"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a container that allows vertical expansion
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(content_frame, text="ECoG GUI", 
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(content_frame, text="Select a MATLAB (.mat) file to automatically start analysis", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 30))
        
        # File selection frame
        file_frame = ttk.LabelFrame(content_frame, text="File Selection", padding="20")
        file_frame.pack(fill=tk.X, pady=(0, 20))
        
        # File path display
        self.file_path_var = tk.StringVar(value="No file selected")
        path_label = ttk.Label(file_frame, textvariable=self.file_path_var, 
                              font=("Arial", 10), wraplength=500)
        path_label.pack(pady=(0, 15))
        
        # Browse button
        browse_button = ttk.Button(file_frame, text="Browse for .mat file", 
                                  command=self.browse_file, style="Accent.TButton")
        browse_button.pack(pady=(0, 10))
        
        # Quick access to default file
        default_file_path = 'Data/8_PM14Ecog_20231217_101228.mat'
        if os.path.exists(default_file_path):
            default_frame = ttk.Frame(file_frame)
            default_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(default_frame, text="Or use the default file:").pack()
            
            default_button = ttk.Button(default_frame, 
                                      text="Use Default File (8_PM14Ecog_20231217_101228.mat)", 
                                      command=self.use_default_file)
            default_button.pack(pady=(5, 0))
        
        # Recent files - give it a minimum height to accommodate multiple files
        recent_frame = ttk.LabelFrame(content_frame, text="Recent Files", padding="10")
        recent_frame.pack(fill=tk.X, pady=(0, 0))
        
        self.recent_files_frame = ttk.Frame(recent_frame)
        self.recent_files_frame.pack(fill=tk.X)
        
        self.update_recent_files_display()
    
    def browse_file(self):
        """Open file dialog to select a .mat file"""
        file_path = filedialog.askopenfilename(
            title="Select MATLAB (.mat) file",
            initialdir="Data",
            filetypes=[("MATLAB files", "*.mat"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path_var.set(f"Selected: {os.path.basename(file_path)}")
            # Add to recent files
            self.add_to_recent_files(file_path)
            # Automatically start analysis when file is selected
            self.analyze_file()
    
    def use_default_file(self):
        """Use the default file"""
        default_file = 'Data/8_PM14Ecog_20231217_101228.mat'
        if os.path.exists(default_file):
            self.selected_file = default_file
            self.file_path_var.set(f"Selected: {default_file}")
            # Add to recent files
            self.add_to_recent_files(default_file)
            # Automatically start analysis when default file is selected
            self.analyze_file()
        else:
            messagebox.showerror("Error", f"Default file '{default_file}' not found!")
    
    def load_recent_files(self):
        """Load recent files from persistent storage"""
        if os.path.exists(self.RECENT_FILES_FILE):
            try:
                with open(self.RECENT_FILES_FILE, 'r') as f:
                    files = json.load(f)
                    # Filter out files that no longer exist
                    return [f for f in files if os.path.exists(f)]
            except (json.JSONDecodeError, IOError):
                return []
        return []
    
    def save_recent_files(self):
        """Save recent files to persistent storage"""
        try:
            with open(self.RECENT_FILES_FILE, 'w') as f:
                json.dump(self.recent_files, f, indent=2)
        except IOError:
            pass  # Silently fail if can't write
    
    def add_to_recent_files(self, file_path):
        """Add a file to recent files list"""
        # Remove if already exists (to move to top)
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        # Add to beginning
        self.recent_files.insert(0, file_path)
        
        # Limit to MAX_RECENT_FILES
        self.recent_files = self.recent_files[:self.MAX_RECENT_FILES]
        
        # Save to file
        self.save_recent_files()
    
    def update_recent_files_display(self):
        """Update the recent files display in the GUI"""
        # Clear existing widgets
        for widget in self.recent_files_frame.winfo_children():
            widget.destroy()
        
        if not self.recent_files:
            ttk.Label(self.recent_files_frame, text="No recent files", 
                     font=("Arial", 10, "italic")).pack()
        else:
            for file_path in self.recent_files:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    # Truncate long file names to fit better
                    max_length = 50
                    if len(file_name) > max_length:
                        file_name = file_name[:max_length-3] + "..."
                    
                    # Create button for each recent file
                    btn = ttk.Button(self.recent_files_frame, 
                                    text=file_name,
                                    command=lambda path=file_path: self.open_recent_file(path))
                    btn.pack(fill=tk.X, pady=2, padx=2)
    
    def open_recent_file(self, file_path):
        """Open a file from the recent files list"""
        if os.path.exists(file_path):
            self.selected_file = file_path
            self.file_path_var.set(f"Selected: {os.path.basename(file_path)}")
            # Move to top of recent files
            self.add_to_recent_files(file_path)
            self.update_recent_files_display()
            # Automatically start analysis
            self.analyze_file()
        else:
            # Remove from recent files if file doesn't exist
            if file_path in self.recent_files:
                self.recent_files.remove(file_path)
                self.save_recent_files()
                self.update_recent_files_display()
            messagebox.showerror("Error", f"File '{file_path}' no longer exists!")
    
    def analyze_file(self):
        """Start the analysis with the selected file"""
        if self.selected_file and os.path.exists(self.selected_file):
            print(f"Starting analysis of: {self.selected_file}")
            
            # Store the file path and close the selection dialog
            selected_file = self.selected_file
            self.root.destroy()
            
            # Create the main application window
            main_root = tk.Tk()
            main_root.title("ECoG GUI")
            main_root.geometry("1200x800")
            
            # Create the ECoG viewer with the selected file
            app = ECoGViewer(main_root, selected_file)
            main_root.mainloop()
        else:
            messagebox.showerror("Error", "Please select a valid .mat file!")

class ECoGViewer:
    def __init__(self, root, mat_file_path):
        self.root = root
        self.root.title("ECoG GUI")
        self.root.geometry("1200x800")
        
        # Data storage
        self.mat_file_path = mat_file_path
        self.raw_voltage = None
        self.frequency_bands = None
        self.trial_starts = None
        self.licks = None
        self.rewards = None
        self.sampling_rate = 1000
        self.trials = []
        self.current_trial = 0
        
        # Vertical offset for voltage visualization
        self.vertical_offset_enabled = tk.BooleanVar(value=False)
        self.vertical_offset_amount = tk.DoubleVar(value=0.0)
        self.slider_update_timer = None  # For throttling slider updates
        
        # Event markers toggle
        self.show_event_markers = tk.BooleanVar(value=True)
        
        # Load data
        self.load_data()
        
        # Create GUI
        self.create_gui()
        
        # Update display
        self.update_plot()
    
    def load_data(self):
        "Load ECoG data from MATLAB file"
        try:
            print(f"Attempting to load: {self.mat_file_path}")
            
            with h5py.File(self.mat_file_path, 'r') as f:
                print("File opened successfully")
                print(f"Available keys: {list(f.keys())}")
                
                if 'data' not in f:
                    raise ValueError("File does not contain 'data' group")
                
                data_group = f['data']
                print(f"Data group keys: {list(data_group.keys())}")
                
                # Load raw voltage data
                if 'ECoG' not in data_group:
                    raise ValueError("File does not contain 'ECoG' data")
                
                ecog_group = data_group['ECoG']
                print(f"ECoG group keys: {list(ecog_group.keys())}")
                
                if 'rawVoltage' not in ecog_group:
                    raise ValueError("File does not contain 'rawVoltage' data")
                
                self.raw_voltage = ecog_group['rawVoltage'][:]  # Shape: (3068818, 10)
                print(f"Raw voltage loaded: {self.raw_voltage.shape}")
                
                # Load frequency bands data
                if 'frequencyBands' in ecog_group:
                    self.frequency_bands = ecog_group['frequencyBands'][:]  # Shape: (samples, bands, channels)
                    print(f"Frequency bands loaded: {self.frequency_bands.shape}")
                else:
                    print("Warning: No frequency bands data found")
                    self.frequency_bands = None
                
                # Load trial start events
                if 'Events' not in data_group:
                    raise ValueError("File does not contain 'Events' data")
                
                events_group = data_group['Events']
                print(f"Events group keys: {list(events_group.keys())}")
                
                if 'trialStart' not in events_group:
                    raise ValueError("File does not contain 'trialStart' events")
                
                self.trial_starts = events_group['trialStart'][:].flatten()
                print(f"Trial starts loaded: {self.trial_starts.shape}")
                
                # Load lick and reward data
                if 'licks' in events_group:
                    self.licks = events_group['licks'][:].flatten()
                    print(f"Licks loaded: {self.licks.shape}")
                else:
                    print("Warning: No lick data found")
                    self.licks = None
                
                if 'reward' in events_group:
                    self.rewards = events_group['reward'][:].flatten()
                    print(f"Rewards loaded: {self.rewards.shape}")
                else:
                    print("Warning: No reward data found")
                    self.rewards = None
                
                # Get sampling rate
                if 'Metadata' not in data_group:
                    print("Warning: No metadata found, using default sampling rate")
                    self.sampling_rate = 1000
                else:
                    metadata_group = data_group['Metadata']
                    print(f"Metadata group keys: {list(metadata_group.keys())}")
                    
                    if 'samplingRate' in metadata_group:
                        self.sampling_rate = int(metadata_group['samplingRate'][0, 0])
                    else:
                        print("Warning: No sampling rate found, using default")
                        self.sampling_rate = 1000
                
                # Extract trials
                self.extract_trials()
                
                print(f"Loaded data: {self.raw_voltage.shape[0]:,} samples, {self.raw_voltage.shape[1]} channels")
                print(f"Found {len(self.trials)} trials")
                
        except Exception as e:
            print(f"Error loading data: {e}")
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.root.destroy()
    
    def extract_trials(self):
        "Extract trial information from trial start events"
        trial_start_indices = [i for i, event in enumerate(self.trial_starts) if event == 1]
        
        for i, start_sample in enumerate(trial_start_indices):
            # For the last trial, use the end of the data
            if i == len(trial_start_indices) - 1:
                end_sample = len(self.trial_starts)
            else:
                # Use the next trial start as the end of this trial
                end_sample = trial_start_indices[i + 1]
            
            duration = (end_sample - start_sample) / self.sampling_rate
            self.trials.append({
                'id': i,
                'startSample': start_sample,
                'endSample': end_sample,
                'duration': duration
            })
    
    def create_gui(self):
        """Create the GUI layout"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Back to Home button (top-left aligned)
        back_button = ttk.Button(main_frame, text="← Return to Home", command=self.back_to_home, width=13)
        back_button.pack(side=tk.TOP, anchor=tk.W, padx=2, pady=(0, 10))

        # Plot area (top)
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create matplotlib figure with reduced margins
        self.fig = Figure(figsize=(12, 6))
        self.fig.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.13)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Control panel (bottom) with fixed height
        control_frame = ttk.Frame(main_frame, height=200)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        control_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Container to center the control frames
        center_container = ttk.Frame(control_frame)
        center_container.pack(expand=True)

        # Trial selection with fixed width
        trial_frame = ttk.LabelFrame(center_container, text="Trial Selection", padding=10, width=400)
        trial_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        trial_frame.pack_propagate(False)  # Prevent frame from shrinking

        ttk.Label(trial_frame, text=f"Total Trials: {len(self.trials)}").pack()

        # Trial navigation
        nav_frame = ttk.Frame(trial_frame)
        nav_frame.pack(fill=tk.X, pady=5, padx=5)

        self.prev_button = ttk.Button(nav_frame, text="← Prev", command=self.prev_trial, width=6)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 10))

        self.trial_label = ttk.Label(nav_frame, text="Trial 1", width=15, anchor="center")
        self.trial_label.pack(side=tk.LEFT, padx=10)

        self.next_button = ttk.Button(nav_frame, text="Next →", command=self.next_trial, width=6)
        self.next_button.pack(side=tk.LEFT, padx=(10, 0))

        # Manual trial input
        input_frame = ttk.Frame(trial_frame)
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Go to trial:").pack(side=tk.LEFT)

        self.trial_entry = ttk.Entry(input_frame, width=8)
        self.trial_entry.pack(side=tk.LEFT, padx=(5, 5))
        self.trial_entry.bind('<Return>', self.go_to_trial)

        self.go_button = ttk.Button(input_frame, text="Go", command=self.go_to_trial)
        self.go_button.pack(side=tk.LEFT)

        # Trial info with fixed width to prevent shifting
        self.trial_info = ttk.Label(trial_frame, text="", width=40, anchor="w")
        self.trial_info.pack(pady=5, fill=tk.X)
        

        # Channel selection with two columns and select/deselect buttons
        channel_frame = ttk.LabelFrame(center_container, text="Channel Selection", padding=10, width=260, height=250)
        channel_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        channel_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Create two columns for channels
        channel_columns_frame = ttk.Frame(channel_frame)
        channel_columns_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Select/Deselect all buttons
        button_frame = ttk.Frame(channel_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Container to center the buttons
        button_container = ttk.Frame(button_frame)
        button_container.pack(expand=True)
        
        select_all_btn = ttk.Button(button_container, text="Select All", command=self.select_all_channels, width=8)
        select_all_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        deselect_all_btn = ttk.Button(button_container, text="Deselect All", command=self.deselect_all_channels, width=8)
        deselect_all_btn.pack(side=tk.LEFT)
        
        # Left column (channels 1-5)
        left_column = ttk.Frame(channel_columns_frame)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Right column (channels 6-10)
        right_column = ttk.Frame(channel_columns_frame)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        self.channel_vars = []
        for i in range(10):
            var = tk.BooleanVar(value=i < 3)  # First 3 channels selected by default
            self.channel_vars.append(var)
            
            # Choose which column to put the checkbox in
            if i < 5:
                parent_frame = left_column
            else:
                parent_frame = right_column
                
            cb = ttk.Checkbutton(parent_frame, text=f"Channel {i+1}", variable=var, 
                               command=self.update_plot)
            cb.pack(anchor=tk.W, pady=2)

        # Plot mode selection with fixed width
        plot_mode_frame = ttk.LabelFrame(center_container, text="Plot Mode", padding=10, width=150)
        plot_mode_frame.pack(side=tk.LEFT, fill=tk.Y)
        plot_mode_frame.pack_propagate(False)  # Prevent frame from shrinking

        self.plot_mode_var = tk.StringVar(value="raw")
        plot_mode_options = [("Raw Voltage", "raw"), ("Frequency Bands", "freq"), ("Power Spectrum", "spectrum")]
        for text, value in plot_mode_options:
            ttk.Radiobutton(plot_mode_frame, text=text, variable=self.plot_mode_var, 
                           value=value, command=self.update_plot).pack(anchor=tk.W, pady=2)

        # Other Features frame with fixed width
        other_features_frame = ttk.LabelFrame(center_container, text="Other Features", padding=10, width=180)
        other_features_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        other_features_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Vertical Offset toggle button (aligned with channel checkboxes)
        offset_toggle = ttk.Checkbutton(other_features_frame, text="Vertical Offset", 
                                       variable=self.vertical_offset_enabled,
                                       command=self.toggle_vertical_offset)
        offset_toggle.pack(anchor=tk.W, pady=2)

        # Vertical Offset slider (initially disabled)
        self.offset_slider = ttk.Scale(other_features_frame, from_=0, to=50, 
                                      orient=tk.HORIZONTAL,
                                      variable=self.vertical_offset_amount,
                                      command=self.on_offset_slider_change,
                                      state='disabled')
        self.offset_slider.pack(fill=tk.X, padx=5, pady=(2, 5))

        # Event markers toggle button
        event_markers_toggle = ttk.Checkbutton(other_features_frame, text="Event Markers", 
                                              variable=self.show_event_markers,
                                              command=self.update_plot)
        event_markers_toggle.pack(anchor=tk.W, pady=(5, 2))

        # Update trial info
        self.update_trial_info()
        
        # Bind arrow keys for trial navigation
        self.root.bind('<Left>', lambda event: self.prev_trial())
        self.root.bind('<Right>', lambda event: self.next_trial())
    
    def update_trial_info(self):
        """Update trial information display"""
        if self.trials:
            trial = self.trials[self.current_trial]
            self.trial_label.config(text=f"Trial {trial['id'] + 1}")
            self.trial_info.config(text=f"Duration: {trial['duration']:.1f}s\n"
                                      f"Samples: {trial['startSample']:,} - {trial['endSample']:,}")
    
    def prev_trial(self):
        """Go to previous trial"""
        if self.current_trial > 0:
            self.current_trial -= 1
            self.update_trial_info()
            self.update_plot()
    
    def next_trial(self):
        """Go to next trial"""
        if self.current_trial < len(self.trials) - 1:
            self.current_trial += 1
            self.update_trial_info()
            self.update_plot()
    

    
    def select_all_channels(self):
        """Select all channels"""
        for var in self.channel_vars:
            var.set(True)
        self.update_plot()
    
    def deselect_all_channels(self):
        """Deselect all channels"""
        for var in self.channel_vars:
            var.set(False)
        self.update_plot()
    
    def go_to_trial(self, event=None):
        """Go to a specific trial number"""
        try:
            # Get the input value
            trial_input = self.trial_entry.get().strip()
            
            # Check if input is empty
            if not trial_input:
                return
            
            # Try to convert to integer
            trial_number = int(trial_input)
            
            # Validate trial number is within range (1-based to 0-based conversion)
            if 1 <= trial_number <= len(self.trials):
                self.current_trial = trial_number - 1  # Convert to 0-based index
                self.update_trial_info()
                self.update_plot()
                self.trial_entry.delete(0, tk.END)  # Clear the entry
            else:
                # Invalid trial number - reset to current trial
                self.trial_entry.delete(0, tk.END)  # Clear the entry
                return
                
        except ValueError:
            # Not an integer - reset to current trial
            self.trial_entry.delete(0, tk.END)  # Clear the entry
            return
    
    def toggle_vertical_offset(self):
        """Enable or disable the vertical offset slider based on toggle state"""
        if self.vertical_offset_enabled.get():
            self.offset_slider.config(state='normal')
        else:
            self.offset_slider.config(state='disabled')
        self.update_plot()
    
    def on_offset_slider_change(self, value):
        """Callback when slider value changes - throttled to reduce lag"""
        # Round the value to nearest 2.0 for larger increments (reduces lag)
        rounded_value = round(float(value) / 2.0) * 2.0
        self.vertical_offset_amount.set(rounded_value)
        
        # Cancel any pending update
        if self.slider_update_timer is not None:
            self.root.after_cancel(self.slider_update_timer)
        
        # Schedule update after a short delay (throttling)
        # This prevents updating on every tiny slider movement
        self.slider_update_timer = self.root.after(50, self.update_plot)
    
    def get_trial_events(self, start_sample, end_sample):
        """Get lick and reward events for a specific trial window"""
        lick_times = []
        reward_times = []
        
        if self.licks is not None:
            # Find licks within the trial window
            lick_indices = np.where((self.licks != 0) & 
                                  (np.arange(len(self.licks)) >= start_sample) & 
                                  (np.arange(len(self.licks)) < end_sample))[0]
            lick_times = lick_indices / self.sampling_rate
        
        if self.rewards is not None:
            # Find rewards within the trial window
            reward_indices = np.where((self.rewards != 0) & 
                                    (np.arange(len(self.rewards)) >= start_sample) & 
                                    (np.arange(len(self.rewards)) < end_sample))[0]
            reward_times = reward_indices / self.sampling_rate
        
        return lick_times, reward_times
    
    def calculate_power_spectrum(self, signal, sampling_rate):
        """Calculate power spectrum using Welch's method for smoother, more reliable spectra"""
        # Use Welch's method for better spectral estimation
        # This uses overlapping windowed segments to reduce variance and spectral leakage
        frequencies, power = sig.welch(
            signal,
            fs=sampling_rate,
            window='hann',
            nperseg=min(256, len(signal)),  # Segment length, adapt to signal length
            noverlap=None,  # 50% overlap by default
            scaling='density'  # Returns Power Spectral Density (PSD)
        )
        
        return frequencies, power
    
    def update_plot(self):
        """Update the plot based on selected mode"""
        if not self.trials or self.current_trial >= len(self.trials):
            return
        
        # Get current trial
        trial = self.trials[self.current_trial]
        start_sample = trial['startSample']
        end_sample = trial['endSample']
        
        # Use full trial length (no time window limitation)
        display_end = end_sample
        
        # Create time axis for full trial
        time_points = np.arange(start_sample, display_end) / self.sampling_rate
        
        # Get plot mode
        plot_mode = self.plot_mode_var.get()
        
        # Clear previous plot
        self.fig.clear()
        
        # Colors for channels
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        if plot_mode == "raw":
            # Create subplot for raw voltage
            ax = self.fig.add_subplot(111)
            ax.set_title(f'Trial {trial["id"] + 1} -- Raw Voltage')
            
            # Check if vertical offset is enabled
            offset_enabled = self.vertical_offset_enabled.get()
            offset_amount = self.vertical_offset_amount.get() if offset_enabled else 0.0
            
            # Track which selected channel we're on (for cumulative offset)
            selected_channel_index = 0
            
            # Plot raw voltage for selected channels
            for i, var in enumerate(self.channel_vars):
                if var.get():
                    channel_data = self.raw_voltage[start_sample:display_end, i]
                    
                    # Apply cumulative vertical offset if enabled
                    if offset_enabled:
                        cumulative_offset = selected_channel_index * offset_amount
                        channel_data = channel_data + cumulative_offset
                    
                    ax.plot(time_points, channel_data, 
                           label=f'Channel {i+1}', color=colors[i], linewidth=1)
                    
                    # Increment selected channel index for cumulative offset
                    selected_channel_index += 1
            
            # Add lick and reward markers (if enabled)
            if self.show_event_markers.get():
                lick_times, reward_times = self.get_trial_events(start_sample, display_end)
                
                if len(lick_times) > 0:
                    # Get y-axis limits for positioning markers
                    y_min, y_max = ax.get_ylim()
                    lick_y = y_max + (y_max - y_min) * 0.05  # Position above the plot
                    ax.scatter(lick_times, [lick_y] * len(lick_times), 
                               color='blue', marker='v', s=50, alpha=0.8, label='Licks', zorder=5)
                
                if len(reward_times) > 0:
                    # Get y-axis limits for positioning markers
                    y_min, y_max = ax.get_ylim()
                    reward_y = y_max + (y_max - y_min) * 0.15  # Position above licks
                    ax.scatter(reward_times, [reward_y] * len(reward_times), 
                               color='red', marker='^', s=60, alpha=0.8, label='Rewards', zorder=5)
            
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Voltage (μV)')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        elif plot_mode == "freq":
            # Create subplot for frequency bands
            ax = self.fig.add_subplot(111)
            ax.set_title(f'Frequency Bands -- Trial {trial["id"] + 1}')
            
            # Check if vertical offset is enabled
            offset_enabled = self.vertical_offset_enabled.get()
            offset_amount = self.vertical_offset_amount.get() if offset_enabled else 0.0
            
            # Track which selected channel we're on (for cumulative offset)
            selected_channel_index = 0
            
            # Plot frequency bands for selected channels
            if self.frequency_bands is not None:
                for i, var in enumerate(self.channel_vars):
                    if var.get():
                        # Plot each frequency band for this channel
                        for band in range(self.frequency_bands.shape[1]):
                            band_data = self.frequency_bands[start_sample:display_end, band, i]
                            
                            # Apply cumulative vertical offset if enabled
                            if offset_enabled:
                                cumulative_offset = selected_channel_index * offset_amount
                                band_data = band_data + cumulative_offset
                            
                            ax.plot(time_points, band_data, 
                                   label=f'Channel {i+1} Band {band+1}', 
                                   color=colors[i], alpha=0.7, linewidth=1)
                        
                        # Increment selected channel index for cumulative offset
                        selected_channel_index += 1
            
            # Add lick and reward markers (if enabled)
            if self.show_event_markers.get():
                lick_times, reward_times = self.get_trial_events(start_sample, display_end)
                
                if len(lick_times) > 0:
                    # Get y-axis limits for positioning markers
                    y_min, y_max = ax.get_ylim()
                    lick_y = y_max + (y_max - y_min) * 0.05  # Position above the plot
                    ax.scatter(lick_times, [lick_y] * len(lick_times), 
                               color='blue', marker='v', s=50, alpha=0.8, label='Licks', zorder=5)
                
                if len(reward_times) > 0:
                    # Get y-axis limits for positioning markers
                    y_min, y_max = ax.get_ylim()
                    reward_y = y_max + (y_max - y_min) * 0.15  # Position above licks
                    ax.scatter(reward_times, [reward_y] * len(reward_times), 
                               color='red', marker='^', s=60, alpha=0.8, label='Rewards', zorder=5)
            
            ax.set_xlabel('Time (seconds)')
            ax.set_ylabel('Power')
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        elif plot_mode == "spectrum":
            # Create subplot for power spectrum
            ax = self.fig.add_subplot(111)
            ax.set_title(f'Power Spectrum -- Trial {trial["id"] + 1}')
            
            # Calculate and plot power spectrum for selected channels
            for i, var in enumerate(self.channel_vars):
                if var.get():
                    # Get the signal data for this channel
                    channel_data = self.raw_voltage[start_sample:display_end, i]
                    
                    # Calculate power spectrum
                    frequencies, power = self.calculate_power_spectrum(channel_data, self.sampling_rate)
                    
                    # Plot power spectrum
                    ax.plot(frequencies, power, 
                           label=f'Channel {i+1}', color=colors[i], linewidth=1.5)
            
            ax.set_xlabel('Frequency (Hz)')
            ax.set_ylabel('Power')
            ax.set_xscale('log')
            ax.set_yscale('log')
            ax.legend()
            ax.grid(True, alpha=0.3, which='both')
        
        # Adjust layout
        self.fig.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.13)
        
        # Update canvas
        self.canvas.draw()
    
    def back_to_home(self):
        """Return to the file selection dialog"""
        # Store reference to root before destroying
        root = self.root
        
        # Destroy the current window
        self.root.destroy()
        
        # Create new root for file selection dialog
        new_root = tk.Tk()
        FileSelectionDialog(new_root)
        new_root.mainloop()
    


def main():
    """Main function"""
    root = tk.Tk()
    app = FileSelectionDialog(root)
    root.mainloop()

if __name__ == "__main__":
    main() 