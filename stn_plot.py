#!/usr/bin/env python3
"""
基于temp_map.png配色的地震台站分布图绘制工具
使用极淡雅的浅绿色和浅灰色配色方案

作者: muly
版本: temp_style
日期: 2025-07-25
"""

import argparse
import sys
import os
from pathlib import Path
import numpy as np

try:
    import obspy
    from obspy import read_inventory
except ImportError:
    print("错误: 未安装ObsPy库。请运行: conda install -c conda-forge obspy")
    sys.exit(1)

try:
    import pygmt
except ImportError:
    print("错误: 未安装PyGMT库。请运行: conda install -c conda-forge pygmt")
    sys.exit(1)


class TempStylePlotter:
    """基于temp_map.png配色的地震台站分布图绘制器"""
    
    def __init__(self):
        self.stations = []
        self.region = None
        
    def parse_dataless(self, dataless_path):
        """解析Dataless SEED文件提取台站信息"""
        try:
            if not os.path.exists(dataless_path):
                raise FileNotFoundError(f"Dataless文件未找到: {dataless_path}")
            
            print(f"正在解析Dataless文件: {dataless_path}")
            inventory = read_inventory(dataless_path)
            
            self.stations = []
            station_count = 0
            
            for network in inventory:
                for station in network:
                    station_info = {
                        'network': network.code,
                        'station': station.code,
                        'latitude': station.latitude,
                        'longitude': station.longitude,
                        'elevation': station.elevation if station.elevation else 0
                    }
                    self.stations.append(station_info)
                    station_count += 1
            
            print(f"成功提取 {station_count} 个台站信息")
            
            if station_count == 0:
                raise ValueError("Dataless文件中未找到任何台站信息")
                
            return True
            
        except Exception as e:
            print(f"解析Dataless文件时发生错误: {e}")
            return False
    
    def calculate_region(self, padding=0.5):
        """自动计算地图范围"""
        if not self.stations:
            raise ValueError("无台站数据，无法计算地图范围")
        
        lons = [s['longitude'] for s in self.stations]
        lats = [s['latitude'] for s in self.stations]
        
        lon_min = min(lons) - padding
        lon_max = max(lons) + padding
        lat_min = min(lats) - padding
        lat_max = max(lats) + padding
        
        self.region = [lon_min, lon_max, lat_min, lat_max]
        print(f"自动计算地图范围: {self.region}")
        
        return self.region
    
    def set_manual_region(self, region_str):
        """设置手动指定的地图范围"""
        try:
            parts = region_str.split('/')
            if len(parts) != 4:
                raise ValueError("区域格式错误，应为: lon_min/lon_max/lat_min/lat_max")
            
            self.region = [float(p) for p in parts]
            print(f"使用手动指定地图范围: {self.region}")
            
        except ValueError as e:
            print(f"解析区域参数错误: {e}")
            sys.exit(1)
    
    def create_custom_elevation_cpt(self, grid, cpt_file=None):
        """创建或加载自定义海拔色彩表"""
        if cpt_file is None:
            cpt_file = os.path.join("cpt", "elevation_temp_style.cpt")
        
        print(f"使用CPT配色文件: {cpt_file}")
        
        # 检查CPT文件是否存在
        if not os.path.exists(cpt_file):
            raise FileNotFoundError(f"CPT配色文件未找到: {cpt_file}")
        
        # 复制CPT文件到工作目录
        import shutil
        work_cpt = "custom_elevation.cpt"
        shutil.copy(cpt_file, work_cpt)
        
        return work_cpt
    
    def create_temp_map(self, output_path, resolution="03s", add_labels=False, title="地震台站分布图", cpt_file=None, show_colorbar=False):
        """创建基于temp_map.png配色的地震台站分布图"""
        if not self.stations:
            raise ValueError("无台站数据")
        
        if not self.region:
            self.calculate_region()
        
        print(f"开始绘制temp_map.png风格地图，分辨率: {resolution}")
        print("注意: 高分辨率数据下载可能需要较长时间，请耐心等待...")
        
        # 设置GMT配置去除黑色边框
        pygmt.config(MAP_FRAME_TYPE="plain")  # 使用简洁边框类型
        pygmt.config(MAP_FRAME_PEN="0p")      # 设置边框线宽为0，去掉黑边
        
        # 尝试设置中文字体环境
        try:
            pygmt.config(PS_CHAR_ENCODING="Standard+")
            pygmt.config(FONT="12p,39,black")  # 使用39号中文字体
            print("尝试使用GMT中文字体配置...")
        except:
            print("GMT中文字体配置失败，使用默认字体...")
        
        # 初始化PyGMT图形
        fig = pygmt.Figure()
        
        try:
            # 加载高精度地形数据
            print("正在下载高精度地形数据...")
            grid = pygmt.datasets.load_earth_relief(
                resolution=resolution, 
                region=self.region
            )
            
            # 加载自定义海拔色彩表
            custom_cpt = self.create_custom_elevation_cpt(grid, cpt_file)
            
            # 使用自定义海拔配色方案
            min_elev = float(grid.min().values)
            max_elev = float(grid.max().values)
            
            # 使用外部CPT文件配色方案
            print(f"海拔范围: {min_elev:.0f}m 到 {max_elev:.0f}m")
            
            # 复制自定义配色为最终配色
            import shutil
            shutil.copy(custom_cpt, "final_elevation.cpt")
            
            # 绘制经典地形配色背景
            print("绘制经典地形配色背景...")
            fig.grdimage(
                grid=grid,
                projection="M22c",  # 更大的地图
                cmap="final_elevation.cpt",
                shading="+a315+ne0.2+nt0.8",  # 标准晕渲
                transparency=0  # 不透明，显示完整色彩
            )
            
            # 绘制地理要素 - map_temp1风格的极淡水体
            print("添加地理要素，map_temp1风格显示水体...")
            fig.coast(
                shorelines="1/0.05p,180/180/185",    # 极细极淡的海岸线
                water="230/240/245",                 # 极淡的蓝色水体，模拟map_temp1
                lakes="230/240/245"                  # 同样颜色的湖泊水库
                # 移除borders参数，不显示边界线条
            )
            
            # 提取台站经纬度
            lons = [s['longitude'] for s in self.stations]
            lats = [s['latitude'] for s in self.stations]
            
            # 绘制台站 - 使用深红色三角形
            print(f"绘制 {len(self.stations)} 个台站...")
            fig.plot(
                x=lons,
                y=lats,
                style="t0.7c",              # 适中大小的三角形
                fill="180/40/40",           # 深红色
                pen="1.5p,120/20/20"        # 更深的红色边框
            )
            
            # 添加台站标签 - 使用与浅红色和谐的颜色
            if add_labels:
                print("添加台站标签...")
                for station in self.stations:
                    label = f"{station['network']}.{station['station']}"
                    fig.text(
                        text=label,
                        x=station['longitude'],
                        y=station['latitude'],
                        font="10p,Helvetica-Bold,black",  # 使用黑色字体
                        justify="LM",
                        offset="0.3c/0.1c"
                    )
            
            # 添加经纬度标注 - 去掉黑色边框但保留标注
            print("添加经纬度标注...")
            fig.basemap(frame=["a1f1", "WSen"])  # 显示标注，去掉边框线
            
            # 添加中文标题 - 使用深灰色
            print("添加地图标题...")
            center_lon = (self.region[0] + self.region[1]) / 2
            title_lat = self.region[3] + (self.region[3] - self.region[2]) * 0.08
            
            # 添加标题 - GMT中文显示较复杂，建议使用英文
            if title:
                # 如果是中文标题，使用英文替代并提示
                if any('\u4e00' <= char <= '\u9fff' for char in title):
                    fallback_title = "Beijing Seismic Network"
                    print(f"检测到中文标题: {title}")
                    print(f"GMT中文字体配置复杂，使用英文标题: {fallback_title}")
                    print("提示: 如需中文标题，建议使用图像编辑软件后期添加")
                    title_to_use = fallback_title
                else:
                    title_to_use = title
                
                fig.text(
                    text=title_to_use,
                    x=center_lon,
                    y=title_lat,
                    font="24p,Helvetica-Bold,gray30",
                    justify="CB"
                )
            
            # 添加无边框英文高程图例（可选）
            if show_colorbar:
                print("添加高程图例...")
                fig.colorbar(
                    frame=["x+lElevation (m)", "y+lm"],
                    position="JMR+w12c/0.6c+o2.5c/0c"
                    # 移除box参数，不显示边框
                )
            else:
                print("跳过高程图例显示")
            
            # 不添加指北针和比例尺，保持简洁
            # print("添加比例尺和指北针...")
            # 注释掉指北针和比例尺
            
            # 保存地图
            print(f"保存地图到: {output_path}")
            fig.savefig(
                output_path, 
                dpi=300, 
                crop=True,
                anti_alias=True
            )
            
            print("temp_map.png风格地图生成完成！")
            
            # 清理临时文件
            for temp_file in ["custom_elevation.cpt", "temp1_base.cpt", "final_elevation.cpt", "gray_base.cpt", "light_base.cpt", "green_base.cpt", "terrain_base.cpt", "soft_base.cpt", "low_elevation.cpt", "high_elevation.cpt"]:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
        except Exception as e:
            print(f"绘制地图时发生错误: {e}")
            print("提示: 请检查GMT和PyGMT是否正确安装")
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="基于temp_map.png配色的地震台站分布图绘制工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python plot_temp_style.py --dataless BJ.dataless --output temp_style_map.png --resolution 03s --labels --title "北京地震台网分布图"
  python plot_temp_style.py --dataless BJ.dataless --cpt custom_colors.cpt --output custom_map.png
        """
    )
    
    parser.add_argument('--dataless', required=True, help='Dataless SEED文件路径')
    parser.add_argument('--output', default='temp_style_map.png', help='输出文件路径')
    parser.add_argument('--region', help='地图范围 lon_min/lon_max/lat_min/lat_max')
    parser.add_argument('--resolution', default='03s', choices=['01m', '30s', '15s', '03s', '01s'], help='地形数据分辨率')
    parser.add_argument('--labels', action='store_true', help='在地图上标注台站名称')
    parser.add_argument('--title', default='Seismic Station Distribution', help='地图标题 (建议使用英文)')
    parser.add_argument('--cpt', help='自定义CPT配色文件路径 (默认使用cpt/elevation_temp_style.cpt)')
    parser.add_argument('--colorbar', action='store_true', help='显示右侧高程图例色彩条 (默认不显示)')
    
    args = parser.parse_args()
    
    # 创建绘图器实例
    plotter = TempStylePlotter()
    
    # 解析Dataless文件
    if not plotter.parse_dataless(args.dataless):
        sys.exit(1)
    
    # 设置地图范围
    if args.region:
        plotter.set_manual_region(args.region)
    else:
        plotter.calculate_region()
    
    # 创建输出目录
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 生成地图
    try:
        plotter.create_temp_map(
            output_path=args.output,
            resolution=args.resolution,
            add_labels=args.labels,
            title=args.title,
            cpt_file=args.cpt,
            show_colorbar=args.colorbar
        )
    except Exception as e:
        print(f"生成地图失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()