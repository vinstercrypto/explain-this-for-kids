#!/usr/bin/env python3
"""
Simple script to generate placeholder PNG icons for the Chrome extension.
Requires: pip install Pillow
"""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Error: Pillow not installed. Run: pip install Pillow")
    exit(1)

def create_icon(size):
    """Create a simple placeholder icon at the given size."""
    # Create image with gradient-like purple background
    img = Image.new('RGB', (size, size), color='#667eea')
    draw = ImageDraw.Draw(img)

    # Draw a simple document/page shape
    margin = size // 8
    doc_width = size - (margin * 2)
    doc_height = size - (margin * 2)

    # White rectangle for document
    draw.rounded_rectangle(
        [(margin, margin), (margin + doc_width, margin + doc_height)],
        radius=size // 16,
        fill='white'
    )

    # Draw simplified lines (text representation)
    if size >= 48:
        line_margin = margin + size // 10
        line_width = size // 20
        line_color = '#667eea'

        # Three horizontal lines
        for i in range(3):
            y = margin + (size // 6) + (i * size // 8)
            line_length = doc_width - (size // 5)
            if i == 2:  # Make last line shorter
                line_length = int(line_length * 0.7)

            draw.rectangle(
                [(line_margin, y), (line_margin + line_length, y + line_width)],
                fill=line_color
            )
    elif size >= 16:
        # For smaller sizes, just draw simple lines
        line_margin = margin + 2
        for i in range(2):
            y = margin + 4 + (i * (size // 4))
            draw.rectangle(
                [(line_margin, y), (size - line_margin, y + 1)],
                fill='#667eea'
            )

    return img

# Generate all required icon sizes
sizes = [16, 32, 48, 128]

for size in sizes:
    img = create_icon(size)
    filename = f'icon{size}.png'
    img.save(filename)
    print(f'Created {filename}')

print('\nAll icons generated successfully!')
print('These are simple placeholder icons.')
print('For better quality, consider using the SVG template with ImageMagick or Inkscape.')
