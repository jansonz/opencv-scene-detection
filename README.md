
# Video Scene Change Detector

This project is a proof of concept (POC) implementation of video scene detection using OpenCV, designed to detect scene changes in a video file and optionally write the timestamps of these changes to a text file.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Contributing](#contributing)
- [License](#license)

## Installation

To set up the project, please follow these steps:

1. Clone the repository:
   ```
   git clone https://github.com/jansonz/opencv-scene-detection
   ```
2. Navigate to the project directory:
   ```
   cd opencv-scene-detection
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

The script now supports command-line arguments for flexible operation. To use the project, execute the script with the following command:

```
python scene_change_detector.py --input <path_to_video> [--textout <output_text_file>] [--silent] [--verbose]
```

### Arguments

- `--input`: Path to the input video file (required).
- `--textout`: Enable text output to a file and specify the file path. If not specified, defaults to `scene_changes.txt`.
- `--silent`: Run the process in the background without opening the video window.
  > [!warning]- Performance is significantly reduced if not running silently.
- `--verbose`: Enable verbose output to provide progress and frame rate information.

## Features

- **Scene Change Detection**: Utilizes color histogram comparison to detect changes between frames.
- **Text Output**: Optionally writes scene change timestamps to a text file.
- **Silent Mode**: Can run without opening the video window for increased performance.
- **Verbose Mode**: Provides detailed progress and frame rate information during processing.

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
