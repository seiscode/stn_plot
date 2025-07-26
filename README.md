# Seismic Station Distribution Mapping Tool

A Python command-line tool for generating high-quality seismic station distribution maps from Dataless SEED and stationXML files, with support for multiple color schemes and customizable terrain rendering.

## Features

- Automatic parsing of Dataless SEED files to extract station metadata
- Support for multiple resolutions of global topographic data (01m, 30s, 15s, 03s, 01s)
- Rich CPT color palette system with 10+ preset color schemes
- Fine 3D shaded relief terrain effects
- Automatic optimal map bounds calculation or manual specification
- Optional station name labels and elevation colorbar
- High-quality PNG output (300 DPI)

## Installation

### Using Conda (Recommended)

```bash
# Create conda environment and install dependencies
conda create --name stn_plot_env -c conda-forge python=3.12 obspy pygmt
conda activate stn_plot_env
```

### Using pip

```bash
# Note: GMT system dependencies must be installed first
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python stn_plot.py --dataless BJ.dataless
```

### Advanced Usage Examples

```bash
# Generate map with default color scheme
python stn_plot.py --dataless BJ.dataless --output BJ_network_map.png

# Use custom color scheme with labels
python stn_plot.py --dataless BJ.dataless \
                   --cpt cpt/wiki_2_0_adjusted.cpt \
                   --output BJ_wiki_style.png \
                   --labels \
                   --colorbar \
                   --title "Beijing Seismic Network"

# Specify map region and resolution
python stn_plot.py --dataless BJ.dataless \
                   --region 115/118/39/42 \
                   --resolution 15s \
                   --output BJ_custom_region.png
```

## Parameters

### Required Parameters
- `--dataless`: Path to Dataless SEED file

### Optional Parameters
- `--output`: Output file path (default: temp_style_map.png)
- `--region`: Map bounds lon_min/lon_max/lat_min/lat_max
- `--resolution`: Topographic data resolution (01m, 30s, 15s, 03s, 01s), default: 03s
- `--labels`: Add station name labels to map
- `--title`: Map title (default: 'Seismic Station Distribution')
- `--cpt`: Custom CPT color palette file path (default: cpt/elevation_temp_style.cpt)
- `--colorbar`: Show elevation colorbar on right side (default: not shown)

## CPT Color Schemes

The project includes multiple preset color schemes located in the `cpt/` directory:

### Available Color Schemes
- **elevation_temp_style.cpt**: Default green-brown elevation scheme (gentle style)
- **light_green_plains_accurate.cpt**: Light green plains color scheme
- **mars_adjusted.cpt**: Mars terrain style
- **usgs_style.cpt**: USGS standard colors (colorblind-friendly)
- **wiki_2_0_adjusted.cpt**: Wikipedia style
- **OS_WAT_Mars.cpt**: Mars hydrological terrain colors

### Color Scheme Preview Generation

```bash
# Generate preview images for all CPT files
python generate_cpt_previews.py
```

This creates corresponding `.png` preview images for each `.cpt` file in the `cpt/` directory.

## System Requirements

- Python 3.12+ (recommended)
- GMT (Generic Mapping Tools) 6.0+
- Ghostscript (for certain output formats)
- Internet connection (for downloading topographic data)

## Project Structure

```
stn_plot/
├── stn_plot.py                    # Main program script
├── generate_cpt_previews.py        # CPT preview generation script
├── BJ.dataless                    # Sample data file
├── cpt/                           # CPT color palette files directory
│   ├── elevation_temp_style.cpt   # Default color scheme
│   ├── mars_adjusted.cpt          # Mars style
│   ├── usgs_style.cpt            # USGS standard
│   ├── wiki_2_0_adjusted.cpt     # Wikipedia style
│   └── *.png                     # Color scheme preview images
├── CLAUDE.md                      # Development documentation
├── README.md                      # Project documentation (English)
└── README_cn.md                   # Project documentation (Chinese)
```

## Sample Output

The program generates high-quality maps containing the following elements:
- High-resolution topographic background (customizable color schemes)
- Fine 3D shaded relief terrain effects
- Station locations (red triangular markers)
- Coastlines and water bodies (light blue)
- Geographic grid and annotations
- Optional elevation colorbar legend

### Example Map
![GeoNet Station Distribution Map](temp_style_map.png)
*GeoNet seismic network distribution map generated using the default color scheme, showing spatial distribution of seismic stations with detailed topographic background*

## Quick Start

1. **Install Environment**
   ```bash
   conda create --name stn_plot_env -c conda-forge python=3.12 obspy pygmt
   conda activate stn_plot_env
   ```

2. **Generate Your First Map**
   ```bash
   python stn_plot.py --dataless BJ.dataless --output my_first_map.png
   ```

3. **Explore Color Options**
   ```bash
   python generate_cpt_previews.py  # Generate all color scheme previews
   ls cpt/*.png                     # View preview images
   ```

4. **Use Different Color Schemes**
   ```bash
   python stn_plot.py --dataless BJ.dataless --cpt cpt/mars_adjusted.cpt --output mars_style.png
   ```

## Troubleshooting

- **GMT Installation Issues**: Use conda to install PyGMT, which automatically installs GMT dependencies
- **Network Connection**: First run requires downloading topographic data, ensure stable internet connection
- **Memory Issues**: High-resolution topographic data is large, reduce resolution parameter if encountering memory problems

## License

This project is open source. See individual CPT files for their respective licenses.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.