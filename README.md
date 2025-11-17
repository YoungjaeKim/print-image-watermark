# print-image-watermark

A Python application to add text watermarks to images based on configuration.

## Features

- Add text watermarks to PNG and JPG images
- Configurable watermark position (bottom-right, top-left, center, etc.)
- Customizable font color and size
- Extract text from filenames using regex patterns
- Batch processing of multiple images

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YoungjaeKim/print-image-watermark.git
cd print-image-watermark
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```bash
python app.py --config config.yaml --source images
```

### Arguments

- `--config`: Path to YAML configuration file
- `--source`: Directory path containing images (PNG/JPG)

### Configuration File

Create a YAML configuration file with the following parameters:

```yaml
position: bottom-right
fontcolor: red
fontsize: 14
contents: filename
type: regex
format: "*"
```

#### Configuration Parameters

- `position`: Watermark position on the image
  - Options: `bottom-right`, `bottom-left`, `top-right`, `top-left`, `center`
- `fontcolor`: Color of the watermark text
  - Supported colors: `red`, `green`, `blue`, `white`, `black`, `yellow`, `cyan`, `magenta`, `orange`, `purple`, `pink`, `brown`, `gray`
  - Also supports hex colors (e.g., `#FF5733`)
- `fontsize`: Font size in pixels (e.g., `14`, `20`)
- `contents`: Content type (`filename`)
- `type`: Pattern matching type (`regex`)
- `format`: Regex pattern to extract text from filename
  - `"*"` means use the entire filename (without extension)
  - Custom regex patterns can be used to extract specific parts

## Example

Given a configuration file `config.yaml`:
```yaml
position: bottom-right
fontcolor: red
fontsize: 14
contents: filename
type: regex
format: "*"
```

Run the application:
```bash
python app.py --config config.yaml --source ./my_images
```

This will process all PNG and JPG files in the `my_images` directory and create watermarked versions with the filename displayed in red text (size 14) at the bottom-right corner.

Output files are saved with a `_watermarked` suffix (e.g., `photo.jpg` → `photo_watermarked.jpg`).

## Requirements

- Python 3.6+
- PyYAML >= 6.0
- Pillow >= 10.0.0

## License

See LICENSE file for details.