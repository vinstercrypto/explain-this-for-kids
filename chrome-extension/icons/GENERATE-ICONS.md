# Icon Generation Instructions

The Chrome extension requires PNG icons in the following sizes:
- 16x16 (icon16.png)
- 32x32 (icon32.png)
- 48x48 (icon48.png)
- 128x128 (icon128.png)

## Option 1: Use ImageMagick (Recommended)

If you have ImageMagick installed, run these commands from the `icons/` directory:

```bash
convert icon-template.svg -resize 16x16 icon16.png
convert icon-template.svg -resize 32x32 icon32.png
convert icon-template.svg -resize 48x48 icon48.png
convert icon-template.svg -resize 128x128 icon128.png
```

## Option 2: Use Online Converter

1. Upload `icon-template.svg` to https://www.svgtopng.com/
2. Generate PNG files at each required size
3. Save them as icon16.png, icon32.png, icon48.png, and icon128.png

## Option 3: Use Inkscape

```bash
inkscape icon-template.svg -w 16 -h 16 -o icon16.png
inkscape icon-template.svg -w 32 -h 32 -o icon32.png
inkscape icon-template.svg -w 48 -h 48 -o icon48.png
inkscape icon-template.svg -w 128 -h 128 -o icon128.png
```

## Option 4: Create Custom Icons

You can replace the SVG template with your own design and follow the same conversion process. The icons should:
- Use the Summarize It! brand colors (purple gradient: #667eea to #764ba2)
- Be clearly visible at small sizes (16x16)
- Represent the concept of summarization/simplification
