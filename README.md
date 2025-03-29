# Video Compression Tool

A powerful Python-based video compression tool that allows you to compress videos while maintaining optimal quality based on your specific needs. This tool uses FFmpeg for efficient video processing and provides intelligent bitrate calculations based on video duration and target file size in Just 300 Lines of python.

## Features

- Intelligent bitrate calculation based on video duration and target size
- Multiple resolution options (SD, HD, Full HD, 4K, Custom)
- Two-pass encoding for better quality
- Adaptive audio bitrate based on video length
- Smart size recommendations based on video duration
- Maintains aspect ratio during compression
- Progress tracking and detailed output information

## Prerequisites

Before using this tool, you need to install the following:

1. **FFmpeg**
   - Windows: 
     ```bash
     # Using conda
     conda install ffmpeg -c conda-forge
     
     # Or download from https://ffmpeg.org/download.html
     ```
   - Linux:
     ```bash
     sudo apt-get update
     sudo apt-get install ffmpeg
     ```
   - macOS:
     ```bash
     brew install ffmpeg
     ```

2. **Python 3.8 or higher**
   - Download from [Python's official website](https://www.python.org/downloads/)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/video-compression-tool.git
   cd video-compression-tool
   ```

2. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```bash
   python Resize.py
   ```

2. Follow the prompts to:
   - Enter input video path
   - Enter output video path
   - Select target file size
   - Choose resolution option

## Resolution Options

1. SD (854x480) - Best for mobile devices
2. HD (1280x720) - Balanced quality and size
3. Full HD (1920x1080) - High quality
4. Original/4K - Maintains original resolution
5. Custom - User-defined resolution

## Results

### Example 1: Short Video Compression
![Short Video Results](results/short_video.png)
- Original Size: 50MB
- Compressed Size: 15MB
- Resolution: 1280x720
- Duration: 30 seconds

### Example 2: Long Video Compression
![Long Video Results](results/long_video.png)
- Original Size: 2GB
- Compressed Size: 500MB
- Resolution: 1920x1080
- Duration: 2 hours

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FFmpeg team for the powerful video processing library
- Python community for the excellent tools and libraries

## Support

If you encounter any issues or have questions, please:
- Open an issue in the GitHub repository
- Contact the developer:
  - Email: makoflash05@gmail.com
  - LinkedIn: [Michael Micah](https://www.linkedin.com/in/Michael-Micah003) 