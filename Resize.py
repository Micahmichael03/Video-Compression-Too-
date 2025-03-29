# Video Compression Tool
# Version 1.0
# Author: Michael Chukwuemeka Micah 
# Date: 2025-March
# Link: https://github.com/MichaelMicah1/Video-Compression-Tool
# Linkedin: https://www.linkedin.com/in/Michael-Micah003

# import necessary libraries
import subprocess
import os
import re

# Function to get video duration in seconds using ffprobe
def get_video_duration(input_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', 
           '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout.strip())

# Function to get video resolution (width x height) using ffprobe
def get_video_resolution(input_path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height', 
           '-of', 'default=noprint_wrappers=1:nokey=1', input_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = result.stdout.strip().split('\n')
    width, height = int(output[0]), int(output[1])
    return width, height

# Function to calculate bitrate based on target size and duration
def calculate_bitrate(target_size_mb, duration_s):
    # Convert target size from MB to bits (1 MB = 8,000,000 bits)
    target_size_bits = target_size_mb * 8000 * 1000
    
    # Calculate base bitrate
    total_bitrate_kbps = target_size_bits / duration_s / 1000
    
    # Adjust audio bitrate based on duration
    if duration_s < 30:  # Very short videos
        audio_bitrate_kbps = 160  # Higher quality audio for short clips
    elif duration_s > 3600:  # Long videos
        audio_bitrate_kbps = 96
    else:
        audio_bitrate_kbps = 128
    
    # Calculate video bitrate
    video_bitrate_kbps = total_bitrate_kbps - audio_bitrate_kbps
    
    # Adjust minimum bitrate based on duration
    if duration_s < 30:  # Very short videos
        min_bitrate = 1000  # Reduced from 1500
    elif duration_s < 60:  # Short videos (30-60 seconds)
        min_bitrate = 800  # Reduced from 1000
    elif duration_s > 3600:  # Long videos
        min_bitrate = 300  # Reduced from 400
    elif duration_s > 600:  # Medium length videos
        min_bitrate = 400  # Reduced from 600
    else:
        min_bitrate = 500  # Reduced from 800
    
    # If video bitrate is too low, calculate a new target size that maintains minimum quality
    if video_bitrate_kbps < min_bitrate:
        # Calculate new target size based on minimum bitrate
        new_total_bitrate = min_bitrate + audio_bitrate_kbps
        new_target_size = (new_total_bitrate * 1000 * duration_s) / (8000 * 1000)
        
        # If new size would be larger than original target, reduce bitrate instead
        if new_target_size > target_size_mb:
            # Use a bitrate that will result in the target size
            video_bitrate_kbps = target_size_bits / duration_s / 1000 - audio_bitrate_kbps
            print("Note: Using original target size to maintain reasonable file size")
        else:
            video_bitrate_kbps = min_bitrate
            print(f"Note: Target size adjusted to {new_target_size:.1f} MB to maintain minimum quality")
    
    return video_bitrate_kbps, audio_bitrate_kbps

# Function to determine resolution and minimum bitrate based on user choice
def get_resolution_settings(original_width, original_height, choice):
    # Base minimum bitrates
    if choice == '1':  # SD
        return 854, 480, 300  # Reduced from 400
    elif choice == '2':  # HD
        return 1280, 720, 500  # Reduced from 800
    elif choice == '3':  # Full HD
        return 1920, 1080, 800  # Reduced from 1200
    elif choice == '4' and (original_width > 1920 or original_height > 1080):  # 4K
        return original_width, original_height, 1500  # Reduced from 2000
    else:  # Original
        return original_width, original_height, 300 if original_height <= 480 else 500 if original_height <= 720 else 800

# Main compression function using FFmpeg two-pass encoding
def compress_video(input_path, output_path, target_size_mb, resolution_choice):
    # Get video duration and original resolution
    duration_s = get_video_duration(input_path)
    original_width, original_height = get_video_resolution(input_path)
    original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    
    # Calculate bitrates
    video_bitrate_kbps, audio_bitrate_kbps = calculate_bitrate(target_size_mb, duration_s)
    
    # Get resolution and minimum bitrate based on user choice
    width, height, min_video_bitrate = get_resolution_settings(original_width, original_height, resolution_choice)
    
    # Check if video bitrate is too low for quality
    if video_bitrate_kbps < min_video_bitrate:
        # Calculate new target size based on minimum bitrate
        new_total_bitrate = min_video_bitrate + audio_bitrate_kbps
        new_target_size = (new_total_bitrate * 1000 * duration_s) / (8000 * 1000)
        
        # If new size would be larger than original target, reduce bitrate instead
        if new_target_size > target_size_mb:
            video_bitrate_kbps = target_size_mb * 8000 * 1000 / duration_s / 1000 - audio_bitrate_kbps
            print("Note: Using original target size to maintain reasonable file size")
        else:
            video_bitrate_kbps = min_video_bitrate
            print(f"Note: Target size adjusted to {new_target_size:.1f} MB to maintain minimum quality")
    
    # First pass: Analyze video for better quality allocation
    pass1_cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264',
        '-preset', 'medium',  # Changed from slow to medium for better compatibility
        '-profile:v', 'high',
        '-level', '4.1',      # Changed back to 4.1 for better compatibility
        '-crf', '17',         # Lower CRF for better quality
        '-b:v', f'{video_bitrate_kbps}k',
        '-maxrate', f'{video_bitrate_kbps * 2}k',
        '-bufsize', f'{video_bitrate_kbps * 4}k',
        '-vf', f'scale={width}:{height}:flags=lanczos',  # Simplified scaling
        '-pix_fmt', 'yuv420p',  # Standard pixel format
        '-pass', '1',
        '-f', 'null',
        os.devnull
    ]
    subprocess.run(pass1_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Second pass: Encode video with calculated settings
    pass2_cmd = [
        'ffmpeg', '-y', '-i', input_path,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-profile:v', 'high',
        '-level', '4.1',
        '-crf', '17',
        '-b:v', f'{video_bitrate_kbps}k',
        '-maxrate', f'{video_bitrate_kbps * 2}k',
        '-bufsize', f'{video_bitrate_kbps * 4}k',
        '-vf', f'scale={width}:{height}:flags=lanczos',
        '-pix_fmt', 'yuv420p',
        '-pass', '2',
        '-c:a', 'aac',
        '-b:a', f'{audio_bitrate_kbps}k',
        '-ar', '48000',
        output_path
    ]
    subprocess.run(pass2_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Check output file size
    actual_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"Output file size: {actual_size_mb:.2f} MB")
    if abs(actual_size_mb - target_size_mb) > 5:
        print("Warning: Actual size differs from target by more than 5 MB.")
    return True

# User input and script execution
def main():
    # Get input and output paths
    input_path = input("Enter the input video path (e.g., video.mp4): ").strip()
    output_path = input("Enter the output video path (e.g., output.mp4): ").strip()
    
    # Get video duration and original file size
    duration_s = get_video_duration(input_path)
    original_size_mb = os.path.getsize(input_path) / (1024 * 1024)
    duration_minutes = duration_s / 60
    print(f"Video duration: {duration_minutes:.1f} minutes ({duration_minutes/60:.1f} hours)")
    print(f"Original file size: {original_size_mb:.1f} MB")
    
    # Special handling for very small videos (less than 3MB)
    if original_size_mb < 3:
        print("\nNote: This is a very small video. Recommended compression:")
        print("1: Compress to 1.0 MB (smaller file, good quality)")
        print("2: Compress to 1.5 MB (larger file, better quality)")
        while True:
            try:
                small_video_choice = input("Enter your choice (1-2): ").strip()
                if small_video_choice in ['1', '2']:
                    target_size_mb = 1.0 if small_video_choice == '1' else 1.5
                    break
                print("Please enter 1 or 2.")
            except ValueError:
                print("Please enter a valid number.")
    else:
        # Calculate recommended target size based on duration
        if duration_s < 30:  # Very short videos (less than 30 seconds)
            recommended_size = max(10, duration_s * 0.5)  # 0.5 MB per second, minimum 10MB
            min_size = max(5, duration_s * 0.2)  # 0.2 MB per second, minimum 5MB

        else:
            duration_minutes = duration_s / 60
            # Calculate base recommended size
            if duration_minutes <= 1:
                base_size = 15  # 1 minute
            elif duration_minutes <= 2:
                base_size = 25  # 2 minutes
            elif duration_minutes <= 3:
                base_size = 35  # 3 minutes
            elif duration_minutes <= 4:
                base_size = 45  # 4 minutes
            elif duration_minutes <= 5:
                base_size = 55  # 5 minutes
            elif duration_minutes <= 6:
                base_size = 65  # 6 minutes
            elif duration_minutes <= 7:
                base_size = 75  # 7 minutes
            elif duration_minutes <= 8:
                base_size = 85  # 8 minutes
            elif duration_minutes <= 9:
                base_size = 95  # 9 minutes
            elif duration_minutes <= 10:
                base_size = 105  # 10 minutes
            elif duration_minutes <= 15:
                base_size = 150  # 15 minutes
            elif duration_minutes <= 20:
                base_size = 200  # 20 minutes
            elif duration_minutes <= 25:
                base_size = 250  # 25 minutes
            elif duration_minutes <= 30:
                base_size = 300  # 30 minutes
            elif duration_minutes <= 35:
                base_size = 350  # 35 minutes
            elif duration_minutes <= 40:
                base_size = 400  # 40 minutes
            elif duration_minutes <= 45:
                base_size = 450  # 45 minutes
            elif duration_minutes <= 50:
                base_size = 500  # 50 minutes
            elif duration_minutes <= 55:
                base_size = 550  # 55 minutes
            elif duration_minutes <= 60:
                base_size = 600  # 60 minutes
            elif duration_minutes <= 65:
                base_size = 650  # 65 minutes
            elif duration_minutes <= 70:
                base_size = 700  # 70 minutes
            elif duration_minutes <= 75:
                base_size = 750  # 75 minutes
            elif duration_minutes <= 80:
                base_size = 800  # 80 minutes
            elif duration_minutes <= 85:
                base_size = 850  # 85 minutes
            elif duration_minutes <= 90:
                base_size = 900  # 90 minutes

            else:
                # For videos longer than 90 minutes, use the original calculation
                first_hour = 3600 * 0.3  # First hour at 0.3 MB/s
                remaining_seconds = duration_s - 3600
                remaining_size = remaining_seconds * 0.2  # Remaining time at 0.2 MB/s
                base_size = first_hour + remaining_size
            
            # Adjust recommended size based on original file size
            if base_size >= original_size_mb:
                # If base size is larger than original, calculate a smaller size
                recommended_size = max(original_size_mb * 0.5, 10)  # 50% of original size, minimum 10MB
            else:
                recommended_size = base_size
            
            # Calculate minimum size (about 1/3 of recommended size)
            min_size = max(10, recommended_size * 0.3)
        
        # Cap size based on duration and original size
        if duration_s < 30:  # Very short videos
            max_size = min(50, original_size_mb)
        elif duration_s <= 3600:  # Up to 1 hour
            max_size = min(500, original_size_mb)
        elif duration_s <= 7200:  # Up to 2 hours
            max_size = min(1000, original_size_mb)
        else:  # More than 2 hours
            max_size = min(2000, original_size_mb)
        
        # Ensure recommended size is between min and max
        recommended_size = min(max_size, max(min_size, recommended_size))
        
        print(f"Original file size: {original_size_mb:.1f} MB")
        print(f"Recommended target size: {recommended_size:.1f} MB")
        print(f"Minimum recommended size: {min_size:.1f} MB")
        
        # Get target size and validate
        while True:
            try:
                user_input = input(f"Enter target size in MB ({min_size:.1f}-{recommended_size:.1f}): ").strip()
                # Remove 'MB' suffix if present and convert to float
                user_input = user_input.replace('MB', '').replace('mb', '').strip()
                target_size_mb = float(user_input)
                
                if min_size <= target_size_mb <= recommended_size:
                    break
                print(f"Please enter a value between {min_size:.1f} and {recommended_size:.1f} MB.")
            except ValueError:
                print(f"Please enter a valid number (e.g., {min_size:.1f} or {recommended_size:.1f})")
    
    # Get resolution choice
    print("\nChoose resolution:")
    print("1: SD (854x480) - Good for mobile, smallest file size")
    print("2: HD (1280x720) - Good balance of quality and size")
    print("3: Full HD (1920x1080) - High quality, larger file size")
    print("4: Original resolution (or 4K if applicable)")
    print("5: Custom resolution (maintain aspect ratio)")
    resolution_choice = input("Enter your choice (1-5): ").strip()
    
    # Compress the video
    if compress_video(input_path, output_path, target_size_mb, resolution_choice):
        if original_size_mb < 3:
            print("Note: Small video compression completed with optimized settings.")
        elif duration_s < 30:
            print("Note: Short video compression will maintain high quality.")
        elif duration_s > 3600:
            print("Note: For long videos, compression may take a while. Please be patient.")
        print("Compression completed successfully!")
        
    else:
        print("Compression failed. Try increasing the target size or choosing a lower resolution.")

if __name__ == "__main__":
    main()