# Seismic Station Distribution Mapping Tool

This project is developed by [the Seismic Data Processing Group](#About_the_Seismic_Data_Processing_Group).A Python command-line tool for generating high-quality seismic station distribution maps from Dataless SEED and stationXML files, with support for multiple color schemes and customizable terrain rendering.

## Features

- Automatic parsing of Dataless SEED files to extract station metadata
- Support for multiple resolutions of global topographic data (01m, 30s, 15s, 03s, 01s)
- Rich CPT color palette system with 9 preset color schemes
- Fine 3D shaded relief terrain effects
- Automatic optimal map bounds calculation or manual specification
- Optional station name labels and elevation colorbar
- Multiple output formats: PNG, PDF, JPG with 300 DPI resolution
- Intelligent data caching system to avoid repeated downloads
- Error handling with informative messages for data download failures

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
python stn_plot.py --dataless stn.dataless
```

### Advanced Usage Examples

```bash
# Generate map with default color scheme
python stn_plot.py --dataless stn.dataless --output network_map.png

# Use custom color scheme with labels and PDF output
python stn_plot.py --dataless stn.dataless \
                   --cpt cpt/colombia.cpt \
                   --output network_map.pdf \
                   --labels \
                   --colorbar \
                   --title "Seismic Network"

# Specify map region and resolution
python stn_plot.py --dataless stn.dataless \
                   --region 115/118/39/42 \
                   --resolution 15s \
                   --output custom_region.png

# High-resolution map without title
python stn_plot.py --dataless stn.dataless \
                   --resolution 01s \
                   --output high_res_map.png
```

## Parameters

### Required Parameters
- `--dataless`: Path to Dataless SEED file

### Optional Parameters
- `--output`: Output file path (default: temp_style_map.png)
  - Supports PNG, PDF, JPG formats based on file extension
- `--region`: Map bounds lon_min/lon_max/lat_min/lat_max
- `--resolution`: Topographic data resolution (01m, 30s, 15s, 03s, 01s), default: 03s
- `--labels`: Add station name labels to map
- `--title`: Map title (no default title - only shows when specified)
- `--cpt`: Custom CPT color palette file path (default: cpt/colombia.cpt)
- `--colorbar`: Show elevation colorbar on right side (default: not shown)

## CPT Color Schemes

The project includes multiple preset color schemes located in the `cpt/` directory:

### Available Color Schemes
- **colombia.cpt**: Default Colombia-inspired elevation scheme (current default)
- **elevation_temp_style.cpt**: Green-brown elevation scheme (gentle style)
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
├── stn.dataless                    # Sample data file
├── cpt/                           # CPT color palette files directory
│   ├── colombia.cpt               # Default color scheme
│   ├── elevation_temp_style.cpt   # Alternative color scheme
│   ├── mars_adjusted.cpt          # Mars style
│   ├── usgs_style.cpt            # USGS standard
│   ├── wiki_2_0_adjusted.cpt     # Wikipedia style
│   └── *.png                     # Color scheme preview images
├── cache/                         # Cached topographic data files
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
![GeoNet Station Distribution Map](GeoNet_map.png)
*GeoNet seismic network distribution map generated using the default color scheme, showing spatial distribution of seismic stations with detailed topographic background*

## Quick Start

1. **Install Environment**
   ```bash
   conda create --name stn_plot_env -c conda-forge python=3.12 obspy pygmt
   conda activate stn_plot_env
   ```

2. **Generate Your First Map**
   ```bash
   python stn_plot.py --dataless stn.dataless --output my_first_map.png
   ```

3. **Explore Color Options**
   ```bash
   python generate_cpt_previews.py  # Generate all color scheme previews
   ls cpt/*.png                     # View preview images
   ```

4. **Use Different Color Schemes and Formats**
   ```bash
   # Mars color scheme in PDF format
   python stn_plot.py --dataless stn.dataless --cpt cpt/mars_adjusted.cpt --output mars_style.pdf
   
   # High-resolution with custom title
   python stn_plot.py --dataless stn.dataless --resolution 01s --title "Seismic Network" --output hires.png
   ```

## Troubleshooting

- **GMT Installation Issues**: Use conda to install PyGMT, which automatically installs GMT dependencies
- **Network Connection**: First run requires downloading topographic data, ensure stable internet connection
- **Memory Issues**: High-resolution topographic data is large, reduce resolution parameter if encountering memory problems
- **Data Download Failures**: If topographic data cannot be downloaded, the program will exit with an error message. Check internet connection and try again
- **Cached Data**: Downloaded data is cached in the `cache/` directory to speed up subsequent runs with the same region and resolution

## About_the_Seismic_Data_Processing_Group

Our group focuses on cutting-edge research and software development in the field of seismology. The team is led by Lin Xiangdong, with core members including Mu Leiyu, Yang Xuan, and Wu Peng.

Our key objectives include:

- Algorithm Development: Building on the theoretical foundations of the book Seismic Data Processing Techniques¹, we are dedicated to developing advanced seismological algorithms. These algorithms serve as both extensions and supplements to the classic methods in the book, while also incorporating our team's innovative approaches to enhance the precision and efficiency of data processing.
- Open-Source Contributions: Providing stable and efficient open-source programs for seismic data processing to serve the scientific community.
- Data Research: Conducting analysis of real-world seismic data and publishing our findings in academic papers.

We are committed to bridging the gap between theoretical research and practical application to drive progress in the field of seismology.


## License

This project is open source. See individual CPT files for their respective licenses.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.
