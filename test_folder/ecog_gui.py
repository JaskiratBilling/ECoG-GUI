#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
import h5py
from typing import List, Dict, Tuple
import threading
import os

class FileSelectionDialog:
    def __init__(self, root):
        self.root = root
        self.root.title("ECoG GUI - File Selection")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Center the window
        self.center_window()
        
        # Selected file path
        self.selected_file = None
        
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
        
        # Title
        title_label = ttk.Label(main_frame, text="ECoG GUI", 
                               font=("Arial", 24, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Select a MATLAB (.mat) file to automatically start analysis", 
                                  font=("Arial", 12))
        subtitle_label.pack(pady=(0, 30))
        
        # File selection frame
        file_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="20")
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
        if os.path.exists('8_PM14Ecog_20231217_101228.mat'):
            default_frame = ttk.Frame(file_frame)
            default_frame.pack(fill=tk.X, pady=(10, 0))
            
            ttk.Label(default_frame, text="Or use the default file:").pack()
            
            default_button = ttk.Button(default_frame, 
                                      text="Use Default File (8_PM14Ecog_20231217_101228.mat)", 
                                      command=self.use_default_file)
            default_button.pack(pady=(5, 0))
        
        # Recent files (placeholder for future enhancement)
        recent_frame = ttk.LabelFrame(main_frame, text="Recent Files", padding="10")
        recent_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(recent_frame, text="No recent files", 
                 font=("Arial", 10, "italic")).pack()
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        quit_button = ttk.Button(button_frame, text="Quit", command=self.root.quit)
        quit_button.pack(side=tk.RIGHT)
    
    def browse_file(self):
        """Open file dialog to select a .mat file"""
        file_path = filedialog.askopenfilename(
            title="Select MATLAB (.mat) file",
            filetypes=[("MATLAB files", "*.mat"), ("All files", "*.*")]
        )
        
        if file_path:
            self.selected_file = file_path
            self.file_path_var.set(f"Selected: {os.path.basename(file_path)}")
            # Automatically start analysis when file is selected
            self.analyze_file()
    
    def use_default_file(self):
        """Use the default file"""
        default_file = '8_PM14Ecog_20231217_101228.mat'
        if os.path.exists(default_file):
            self.selected_file = default_file
            self.file_path_var.set(f"Selected: {default_file}")
            # Automatically start analysis when default file is selected
            self.analyze_file()
        else:
            messagebox.showerror("Error", f"Default file '{default_file}' not found!")
    
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
        self.trial_starts = None
        self.sampling_rate = 1000
        self.trials = []
        self.current_trial = 0
        self.selected_channels = [0, 1, 2]  # Default to first 3 channels
        
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
                
                # Load trial start events
                if 'Events' not in data_group:
                    raise ValueError("File does not contain 'Events' data")
                
                events_group = data_group['Events']
                print(f"Events group keys: {list(events_group.keys())}")
                
                if 'trialStart' not in events_group:
                    raise ValueError("File does not contain 'trialStart' events")
                
                self.trial_starts = events_group['trialStart'][:].flatten()
                print(f"Trial starts loaded: {self.trial_starts.shape}")
                
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

        # Plot area (top)
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Create matplotlib figure with reduced margins
        self.fig = Figure(figsize=(12, 6))
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.07, right=0.98, top=0.95, bottom=0.13)

        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.fig, plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Control panel (bottom) with fixed height
        control_frame = ttk.Frame(main_frame, height=200)
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        control_frame.pack_propagate(False)  # Prevent frame from shrinking

        # Trial selection with fixed width
        trial_frame = ttk.LabelFrame(control_frame, text="Trial Selection", padding=10, width=400)
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
        print("Next button created and packed")  # Debug line

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
        

        # Channel selection with fixed width
        channel_frame = ttk.LabelFrame(control_frame, text="Channel Selection", padding=10, width=200)
        channel_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        channel_frame.pack_propagate(False)  # Prevent frame from shrinking

        self.channel_vars = []
        for i in range(10):
            var = tk.BooleanVar(value=i < 3)  # First 3 channels selected by default
            self.channel_vars.append(var)
            cb = ttk.Checkbutton(channel_frame, text=f"Channel {i+1}", variable=var, 
                               command=self.update_plot)
            cb.pack(anchor=tk.W)

        # Time window selection with fixed width
        time_frame = ttk.LabelFrame(control_frame, text="Time Window", padding=10, width=150)
        time_frame.pack(side=tk.LEFT, fill=tk.Y)
        time_frame.pack_propagate(False)  # Prevent frame from shrinking

        self.time_window = tk.StringVar(value="5")
        time_options = [("2 seconds", "2"), ("5 seconds", "5"), ("10 seconds", "10"), ("20 seconds", "20")]
        for text, value in time_options:
            ttk.Radiobutton(time_frame, text=text, variable=self.time_window, 
                           value=value, command=self.update_plot).pack(anchor=tk.W)

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
    
    def update_plot(self):
        """Update the voltage plot"""
        if not self.trials or self.current_trial >= len(self.trials):
            return
        
        # Clear previous plot
        self.ax.clear()
        
        # Get current trial
        trial = self.trials[self.current_trial]
        start_sample = trial['startSample']
        end_sample = trial['endSample']
        
        # Get time window
        time_window = int(self.time_window.get())
        max_samples = time_window * self.sampling_rate
        
        # Limit the display window
        display_end = min(start_sample + max_samples, end_sample)
        
        # Create time axis
        time_points = np.arange(start_sample, display_end) / self.sampling_rate
        
        # Plot selected channels
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for i, var in enumerate(self.channel_vars):
            if var.get():
                channel_data = self.raw_voltage[start_sample:display_end, i]
                self.ax.plot(time_points, channel_data, 
                           label=f'Channel {i+1}', color=colors[i], linewidth=1)
        
        # Configure plot
        self.ax.set_xlabel('Time (seconds)')
        self.ax.set_ylabel('Voltage (μV)')
        self.ax.set_title(f'ECoG GUI - Trial {trial["id"] + 1}')
        self.ax.legend()
        self.ax.grid(True, alpha=0.3)
        
        # Update canvas
        self.canvas.draw()
    


def main():
    """Main function"""
    root = tk.Tk()
    app = FileSelectionDialog(root)
    root.mainloop()

if __name__ == "__main__":
    main() 