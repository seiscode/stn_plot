# 地震台站分布图绘制工具 (Station Plot Tool)

本项目由[地震数据处理小组](#地震数据处理小组简介)研发。基于Dataless SEED文件生成高质量的地震台站分布图，支持多种配色方案和自定义地形渲染。

## 功能特点

- 自动解析Dataless SEED文件，提取台站元数据
- 支持多种分辨率的全球地形数据 (01m, 30s, 15s, 03s, 01s)
- 丰富的CPT配色方案系统，包含多种预设配色
- 精细的3D晕渲地形效果
- 自动计算最佳地图范围或手动指定
- 可选的台站名称标注和高程色彩条
- **插图功能**：显示主地图在更大地理区域中的位置
- 多种输出格式：PNG、PDF、JPG，300 DPI分辨率
- 智能数据缓存系统，避免重复下载
- 完善的错误处理，数据下载失败时提供详细信息

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
python stn_plot.py --dataless stn.dataless
```

### 完整用法示例

```bash
# 使用默认配色生成地图
python stn_plot.py --dataless stn.dataless --output network_map.png

# 使用自定义配色和标签，输出PDF格式
python stn_plot.py --dataless stn.dataless \
                   --cpt cpt/colombia.cpt \
                   --output network_map.pdf \
                   --labels \
                   --colorbar \
                   --title "Seismic Network"

# 指定地图范围和分辨率
python stn_plot.py --dataless stn.dataless \
                   --region 115/118/39/42 \
                   --resolution 15s \
                   --output custom_region.png

# 高分辨率地图，不显示标题
python stn_plot.py --dataless stn.dataless \
                   --resolution 01s \
                   --output high_res_map.png

# 生成带有插图的地图，显示更大地理背景
python stn_plot.py --dataless stn.dataless \
                   --output map_with_inset.png \
                   --inset \
                   --inset-region "110/125/35/45"

# 将插图放置在左上角
python stn_plot.py --dataless stn.dataless \
                   --output map_inset_topleft.png \
                   --inset \
                   --inset-region "110/125/35/45" \
                   --inset-position "jTL+o0.5c"
```

## 参数说明

### 必需参数
- `--dataless`：Dataless SEED文件路径

### 可选参数
- `--output`：输出文件路径（默认：temp_style_map.png）
  - 根据文件扩展名支持PNG、PDF、JPG格式
- `--region`：地图范围 lon_min/lon_max/lat_min/lat_max
- `--resolution`：地形数据分辨率（01m, 30s, 15s, 03s, 01s），默认03s
- `--labels`：在地图上标注台站名称
- `--title`：地图标题（无默认标题 - 仅在指定时显示）
- `--cpt`：自定义CPT配色文件路径（默认：cpt/colombia.cpt）
- `--colorbar`：显示右侧高程色彩条（默认不显示）

### 插图参数
- `--inset`：启用插图功能
- `--inset-region`：插图区域范围 lon_min/lon_max/lat_min/lat_max（例如："110/125/35/45"）
- `--inset-position`：插图位置（默认："jBR+o0.1c" - 右下角）
  - 可用位置：jTL（左上）、jTR（右上）、jBL（左下）、jBR（右下）
  - 偏移调整：+o（例如："+o0.5c"表示0.5厘米偏移）

## CPT配色方案

项目包含多种预设配色方案，位于 `cpt/` 目录：

### 可用配色方案
- **colombia.cpt**: 默认哥伦比亚风格高程配色（当前默认）
- **elevation_temp_style.cpt**: 绿棕配色（温和风格）
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

## 插图功能

插图功能通过在更大的地理区域内显示主地图的位置来提供地理背景信息。这对于区域地震台网展示其相对于大型地理特征的位置特别有用。

### 功能特点
- **地理背景**：在更大区域内显示主地图位置
- **色彩和谐**：自动匹配主地图的配色方案
- **灵活定位**：可配置位置（四个角落）和偏移
- **智能显示**：用红色矩形高亮主地图区域
- **台站标注**：当台站数量≤10个时在插图中显示台站点

### 使用示例

```bash
# 基本插图，位于右下角
python stn_plot.py --dataless data.xml --inset --inset-region "110/125/35/45"

# 将插图放置在左上角，增大偏移
python stn_plot.py --dataless data.xml --inset --inset-region "110/125/35/45" --inset-position "jTL+o0.5c"

# 结合高分辨率和自定义配色
python stn_plot.py --dataless data.xml --resolution 01s --cpt cpt/wiki_2_0_adjusted.cpt \
                   --inset --inset-region "110/125/35/45" --output map_with_context.pdf
```

### 位置选项
- `jTL+o0.1c`：左上角，0.1厘米偏移
- `jTR+o0.1c`：右上角，0.1厘米偏移
- `jBL+o0.1c`：左下角，0.1厘米偏移
- `jBR+o0.1c`：右下角，0.1厘米偏移（默认）

### 技术说明
- **PyGMT限制**：由于PyGMT/GMT约束，插图不支持经纬度标注显示
- **色彩协调**：插图自动使用与主地图CPT方案兼容的颜色
- **性能优化**：使用低分辨率地理数据实现快速渲染

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
├── stn.dataless                    # 示例数据文件
├── cpt/                           # CPT配色文件目录
│   ├── colombia.cpt               # 默认配色
│   ├── elevation_temp_style.cpt   # 备用配色
│   ├── mars_adjusted.cpt          # 火星风格
│   ├── usgs_style.cpt            # USGS标准
│   ├── wiki_2_0_adjusted.cpt     # 维基百科风格
│   └── *.png                     # 配色预览图
├── cache/                         # 地形数据缓存目录
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
- 可选的插图显示主地图在更大地理背景中的位置

### 示例地图
![GeoNet台站分布图](GeoNet_map.png)
*使用默认配色方案生成的GeoNet地震台网分布图，展示了地震台站的空间分布和精细的地形背景*

## 快速开始

1. **安装环境**
   ```bash
   conda create --name stn_plot_env -c conda-forge python=3.12 obspy pygmt
   conda activate stn_plot_env
   ```

2. **生成第一张地图**
   ```bash
   python stn_plot.py --dataless stn.dataless --output my_first_map.png
   ```

3. **查看配色选项**
   ```bash
   python generate_cpt_previews.py  # 生成所有配色预览
   ls cpt/*.png                     # 查看预览图
   ```

4. **使用不同配色和格式**
   ```bash
   # 火星风格配色，PDF格式
   python stn_plot.py --dataless stn.dataless --cpt cpt/mars_adjusted.cpt --output mars_style.pdf
   
   # 高分辨率图，自定义标题
   python stn_plot.py --dataless stn.dataless --resolution 01s --title "地震台网分布" --output hires.png
   
   # 带插图的地图，显示地理背景
   python stn_plot.py --dataless stn.dataless --inset --inset-region "110/125/35/45" --output map_with_inset.png
   ```

## 故障排除

- **GMT安装问题**: 确保使用conda安装PyGMT，它会自动安装GMT依赖
- **网络连接**: 首次运行需要下载地形数据，请确保网络连接正常
- **内存不足**: 高分辨率地形数据较大，如遇内存问题可降低resolution参数
- **数据下载失败**: 如果地形数据无法下载，程序会退出并显示错误信息。请检查网络连接后重试
- **数据缓存**: 下载的数据会缓存在 `cache/` 目录中，相同区域和分辨率的后续运行会更快

## 地震数据处理小组简介

本小组专注于测震学领域的前沿研究与软件开发。团队由组长**林向东**负责，核心成员包括**牟磊育**、**杨选**和**吴朋**。

**我们的主要目标包括：**

- 算法研发：在《地震数据处理技术》一书的理论基础上，我们致力于研发更为先进的测震学算法。这些算法既是书中经典方法的扩展与补充，也包含了我们团队的创新探索，旨在全面提升数据处理的精度与效率。
- 开源贡献：提供稳定、高效的开源地震数据处理程序，服务于科研社区。
- 数据研究：开展实际地震数据处理工作，并将研究成果发表为学术论文。

我们致力于将理论研究与实践应用相结合，推动地震科学的发展。


## 许可证

本项目为开源项目。各CPT文件的许可证请参考其各自的许可证信息。

## 贡献

欢迎贡献！请随时提交问题和拉取请求。
