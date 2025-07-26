# 地震台站分布图绘制工具 (Station Plot Tool)

基于Dataless SEED文件生成高质量的地震台站分布图，支持多种配色方案和自定义地形渲染。

## 功能特点

- 自动解析Dataless SEED文件，提取台站元数据
- 支持多种分辨率的全球地形数据 (01m, 30s, 15s, 03s, 01s)
- 丰富的CPT配色方案系统，包含10+种预设配色
- 精细的3D晕渲地形效果
- 自动计算最佳地图范围或手动指定
- 可选的台站名称标注和高程色彩条
- 高质量PNG输出（300 DPI）

## 环境安装

### 使用Conda（推荐）

```bash
# 创建conda环境并安装依赖
conda create --name stn_plot_env -c conda-forge python=3.12 obspy pygmt
conda activate stn_plot_env
```

### 使用pip

```bash
# 注意：需要先安装GMT系统依赖
pip install -r requirements.txt
```

## 使用方法

### 基本用法

```bash
python stn_plot.py --dataless BJ.dataless
```

### 完整用法示例

```bash
# 使用默认配色生成地图
python stn_plot.py --dataless BJ.dataless --output BJ_network_map.png

# 使用自定义配色和标签
python stn_plot.py --dataless BJ.dataless \
                   --cpt cpt/wiki_2_0_adjusted.cpt \
                   --output BJ_wiki_style.png \
                   --labels \
                   --colorbar \
                   --title "Beijing Seismic Network"

# 指定地图范围和分辨率
python stn_plot.py --dataless BJ.dataless \
                   --region 115/118/39/42 \
                   --resolution 15s \
                   --output BJ_custom_region.png
```

## 参数说明

### 必需参数
- `--dataless`：Dataless SEED文件路径

### 可选参数
- `--output`：输出文件路径（默认：temp_style_map.png）
- `--region`：地图范围 lon_min/lon_max/lat_min/lat_max
- `--resolution`：地形数据分辨率（01m, 30s, 15s, 03s, 01s），默认03s
- `--labels`：在地图上标注台站名称
- `--title`：地图标题（默认：'Seismic Station Distribution'）
- `--cpt`：自定义CPT配色文件路径（默认：cpt/elevation_temp_style.cpt）
- `--colorbar`：显示右侧高程色彩条（默认不显示）

## CPT配色方案

项目包含多种预设配色方案，位于 `cpt/` 目录：

### 可用配色方案
- **elevation_temp_style.cpt**: 默认绿棕配色（温和风格）
- **light_green_plains_accurate.cpt**: 浅绿平原配色
- **mars_adjusted.cpt**: 火星地形风格
- **usgs_style.cpt**: USGS标准配色（色盲友好）
- **wiki_2_0_adjusted.cpt**: 维基百科风格
- **OS_WAT_Mars.cpt**: 火星水文地形配色

### 配色预览生成

```bash
# 为所有CPT文件生成预览图
python generate_cpt_previews.py
```

这将在 `cpt/` 目录下为每个 `.cpt` 文件生成对应的 `.png` 预览图。

## 系统要求

- Python 3.12+ (推荐)
- GMT (Generic Mapping Tools) 6.0+
- Ghostscript（用于某些输出格式）
- 网络连接（用于下载地形数据）

## 文件结构

```
stn_plot/
├── stn_plot.py                    # 主程序脚本
├── generate_cpt_previews.py        # CPT预览生成脚本
├── BJ.dataless                    # 示例数据文件
├── cpt/                           # CPT配色文件目录
│   ├── elevation_temp_style.cpt   # 默认配色
│   ├── mars_adjusted.cpt          # 火星风格
│   ├── usgs_style.cpt            # USGS标准
│   ├── wiki_2_0_adjusted.cpt     # 维基百科风格
│   └── *.png                     # 配色预览图
├── CLAUDE.md                      # 开发文档
└── README.md                      # 项目说明
```

## 示例输出

程序将生成包含以下要素的高质量地图：
- 高精度地形背景（可自定义配色方案）
- 精细的3D晕渲地形效果
- 台站位置（红色三角形标记）
- 海岸线和水体（浅蓝色）
- 经纬网格和标注
- 可选的高程色彩条图例

### 示例地图
![GeoNet台站分布图](temp_style_map.png)
*使用默认配色方案生成的GeoNet地震台网分布图，展示了地震台站的空间分布和精细的地形背景*

## 快速开始

1. **安装环境**
   ```bash
   conda create --name stn_plot_env -c conda-forge python=3.12 obspy pygmt
   conda activate stn_plot_env
   ```

2. **生成第一张地图**
   ```bash
   python stn_plot.py --dataless BJ.dataless --output my_first_map.png
   ```

3. **查看配色选项**
   ```bash
   python generate_cpt_previews.py  # 生成所有配色预览
   ls cpt/*.png                     # 查看预览图
   ```

4. **使用不同配色**
   ```bash
   python stn_plot.py --dataless BJ.dataless --cpt cpt/mars_adjusted.cpt --output mars_style.png
   ```

## 故障排除

- **GMT安装问题**: 确保使用conda安装PyGMT，它会自动安装GMT依赖
- **网络连接**: 首次运行需要下载地形数据，请确保网络连接正常
- **内存不足**: 高分辨率地形数据较大，如遇内存问题可降低resolution参数