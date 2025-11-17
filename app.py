#!/usr/bin/env python3
"""
Image watermark synthesis application.
Adds text watermarks to images based on configuration.
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

import yaml
from PIL import Image, ImageDraw, ImageFont


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Add watermarks to images based on configuration"
    )
    parser.add_argument(
        "--config",
        required=True,
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--source",
        required=True,
        help="Directory path containing images (PNG/JPG)"
    )
    parser.add_argument(
        "--target",
        default=None,
        help="Directory path for output images (default: watermark directory inside source)"
    )
    return parser.parse_args()


def load_config(config_path: str) -> Dict:
    """Load and validate configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Validate required fields
        required_fields = ['position', 'fontcolor', 'fontsize', 'contents', 'type', 'format']
        for field in required_fields:
            if field not in config:
                raise ValueError(f"Missing required field in config: {field}")
        
        return config
    except FileNotFoundError:
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML config: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)


def get_image_files(source_dir: str) -> List[Path]:
    """Get list of image files (PNG/JPG) from source directory."""
    source_path = Path(source_dir)
    
    if not source_path.exists():
        print(f"Error: Source directory not found: {source_dir}")
        sys.exit(1)
    
    if not source_path.is_dir():
        print(f"Error: Source path is not a directory: {source_dir}")
        sys.exit(1)
    
    # Get all PNG and JPG files
    image_files = []
    for ext in ['*.png', '*.jpg', '*.jpeg', '*.PNG', '*.JPG', '*.JPEG']:
        image_files.extend(source_path.glob(ext))
    
    return sorted(image_files)


def extract_text_from_filename(filename: str, regex_pattern: str) -> str:
    """Extract text from filename using regex pattern."""
    if regex_pattern == "*":
        # "*" means use the entire filename (without extension)
        return Path(filename).stem
    
    # Use regex pattern to extract text
    match = re.search(regex_pattern, filename)
    if match:
        # Return the first group if groups exist, otherwise the entire match
        return match.group(1) if match.groups() else match.group(0)
    
    # If no match, return the filename stem
    return Path(filename).stem


def parse_color(color_name: str) -> Tuple[int, int, int]:
    """Parse color name to RGB tuple."""
    color_map = {
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'orange': (255, 165, 0),
        'purple': (128, 0, 128),
        'pink': (255, 192, 203),
        'brown': (165, 42, 42),
        'gray': (128, 128, 128),
        'grey': (128, 128, 128),
    }
    
    color_lower = color_name.lower()
    if color_lower in color_map:
        return color_map[color_lower]
    
    # Try to parse as hex color
    if color_name.startswith('#'):
        hex_color = color_name.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Default to black if color is not recognized
    print(f"Warning: Color '{color_name}' not recognized, using black")
    return (0, 0, 0)


def calculate_text_position(
    image_size: Tuple[int, int],
    text_bbox: Tuple[int, int, int, int],
    position: str,
    margin: int = 10
) -> Tuple[int, int]:
    """Calculate text position based on position string."""
    img_width, img_height = image_size
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position_lower = position.lower()
    
    # Parse position (e.g., "bottom-right", "top-left", "center")
    if 'bottom' in position_lower:
        y = img_height - text_height - margin
    elif 'top' in position_lower:
        y = margin
    else:  # center vertically
        y = (img_height - text_height) // 2
    
    if 'right' in position_lower:
        x = img_width - text_width - margin
    elif 'left' in position_lower:
        x = margin
    else:  # center horizontally
        x = (img_width - text_width) // 2
    
    return (x, y)


def add_watermark_to_image(
    image_path: Path,
    config: Dict,
    output_dir: Path = None
) -> None:
    """Add watermark to a single image."""
    try:
        # Load image
        img = Image.open(image_path)
        
        # Convert to RGB if necessary (for PNG with transparency)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Extract text from filename
        text = extract_text_from_filename(image_path.name, config['format'])
        
        # Create drawing context
        draw = ImageDraw.Draw(img)
        
        # Get font
        font_size = config['fontsize']
        try:
            # Try to use a TrueType font
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
        except (IOError, OSError):
            # Fallback to default font
            font = ImageFont.load_default()
            print(f"Warning: Could not load TrueType font, using default font")
        
        # Get text bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        
        # Calculate position
        position = calculate_text_position(img.size, bbox, config['position'])
        
        # Get color
        color = parse_color(config['fontcolor'])
        
        # Draw text
        draw.text(position, text, fill=color, font=font)
        
        # Determine output path
        if output_dir:
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / image_path.name
        else:
            # Save with "_watermarked" suffix
            output_path = image_path.parent / f"{image_path.stem}_watermarked{image_path.suffix}"
        
        # Save image
        img.save(output_path)
        print(f"Processed: {image_path.name} -> {output_path}")
        
    except Exception as e:
        print(f"Error processing {image_path.name}: {e}")


def main():
    """Main application entry point."""
    args = parse_arguments()
    
    # Load configuration
    config = load_config(args.config)
    
    # Get image files
    image_files = get_image_files(args.source)
    
    if not image_files:
        print(f"No image files found in {args.source}")
        return
    
    # Determine output directory
    if args.target:
        output_dir = Path(args.target)
    else:
        # Create watermark directory inside source directory
        source_path = Path(args.source)
        output_dir = source_path / "watermark"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}")
    
    print(f"Found {len(image_files)} image(s) to process")
    print(f"Configuration: position={config['position']}, "
          f"color={config['fontcolor']}, size={config['fontsize']}")
    
    # Process each image
    for image_path in image_files:
        add_watermark_to_image(image_path, config, output_dir)
    
    print("Done!")


if __name__ == "__main__":
    main()
