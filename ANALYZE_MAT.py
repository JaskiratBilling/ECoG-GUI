#!/usr/bin/env python3
"""
Detailed analysis of the MATLAB file structure
"""

import h5py
import numpy as np
import sys

def analyze_mat_detailed(filename):
    """Detailed analysis of the MATLAB file structure"""
    print(f"Detailed Analysis of {filename}")
    print("=" * 60)
    
    with h5py.File(filename, 'r') as f:
        data_group = f['data']
        
        # Analyze ECoG data
        print("\n1. ECoG DATA ANALYSIS")
        print("-" * 30)
        
        ecog_group = data_group['ECoG']
        
        # Raw voltage data
        raw_voltage = ecog_group['rawVoltage']
        print(f"Raw Voltage Shape: {raw_voltage.shape}")
        print(f"Raw Voltage Dtype: {raw_voltage.dtype}")
        print(f"Sample data (first 3 samples, first 3 channels):")
        print(raw_voltage[:3, :3])
        
        # Frequency bands data
        freq_bands = ecog_group['frequencyBands']
        print(f"\nFrequency Bands Shape: {freq_bands.shape}")
        print(f"Frequency Bands Dtype: {freq_bands.dtype}")
        print(f"Sample data (first 2 samples, first 2 bands, first 2 channels):")
        print(freq_bands[:2, :2, :2])
        
        # Analyze Events
        print("\n2. EVENTS ANALYSIS")
        print("-" * 30)
        
        events_group = data_group['Events']
        for event_name, event_data in events_group.items():
            print(f"{event_name}: Shape {event_data.shape}, Dtype {event_data.dtype}")
            # Check for non-zero values
            non_zero = np.count_nonzero(event_data[:])
            print(f"  Non-zero values: {non_zero}")
            if non_zero > 0:
                print(f"  Sample non-zero values: {event_data[event_data[:] != 0][:5]}")
        
        # Analyze Metadata
        print("\n3. METADATA ANALYSIS")
        print("-" * 30)
        
        metadata_group = data_group['Metadata']
        for meta_name, meta_data in metadata_group.items():
            print(f"{meta_name}: Shape {meta_data.shape}, Dtype {meta_data.dtype}")
            if hasattr(meta_data, 'shape') and meta_data.shape:
                try:
                    print(f"  Data: {meta_data[:]}")
                except:
                    print(f"  Data: [Complex object]")
        
        # Analyze Behavior data
        print("\n4. BEHAVIOR DATA ANALYSIS")
        print("-" * 30)
        
        bhv_group = data_group['bhv']
        for bhv_name, bhv_data in bhv_group.items():
            print(f"{bhv_name}: Shape {bhv_data.shape}, Dtype {bhv_data.dtype}")
            if bhv_data.shape[0] > 0:
                try:
                    # Try to read first few values
                    sample_data = []
                    for i in range(min(3, bhv_data.shape[0])):
                        try:
                            ref = bhv_data[i, 0]
                            sample_data.append(f.read(ref)[0])
                        except:
                            sample_data.append("Error reading")
                    print(f"  Sample data: {sample_data}")
                except:
                    print(f"  Data: [Complex object]")
        
        # Analyze Stimulation data
        print("\n5. STIMULATION DATA ANALYSIS")
        print("-" * 30)
        
        stim_group = data_group['Stimulation']
        for stim_name, stim_data in stim_group.items():
            print(f"{stim_name}: Shape {stim_data.shape}, Dtype {stim_data.dtype}")
            non_zero = np.count_nonzero(stim_data[:])
            print(f"  Non-zero values: {non_zero}")
            if non_zero > 0:
                print(f"  Sample non-zero values: {stim_data[stim_data[:] != 0][:5]}")
        
        # Analyze Video data
        print("\n6. VIDEO DATA ANALYSIS")
        print("-" * 30)
        
        video_group = data_group['Video']
        for video_name, video_data in video_group.items():
            print(f"{video_name}: Shape {video_data.shape}, Dtype {video_data.dtype}")
            non_nan = np.count_nonzero(~np.isnan(video_data[:]))
            print(f"  Non-NaN values: {non_nan}")
            if non_nan > 0:
                valid_data = video_data[~np.isnan(video_data[:])]
                print(f"  Sample valid values: {valid_data[:5]}")
        
        # Summary
        print("\n7. SUMMARY")
        print("-" * 30)
        print(f"Total recording duration: {raw_voltage.shape[0] / 1000:.1f} seconds ({raw_voltage.shape[0] / 1000 / 60:.1f} minutes)")
        print(f"Number of channels: {raw_voltage.shape[1]}")
        print(f"Number of frequency bands: {freq_bands.shape[1]}")
        print(f"Number of trials (from behavior): {bhv_group['TrialStart'].shape[0]}")
        
        # Check for trial start events
        trial_starts = events_group['trialStart']
        trial_start_count = np.count_nonzero(trial_starts[:])
        print(f"Trial start events in continuous data: {trial_start_count}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
    else:
        filename = 'Data/8_PM14Ecog_20231217_101228.mat'
    
    analyze_mat_detailed(filename)
