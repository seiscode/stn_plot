#!/usr/bin/env python3
"""
地震台站分布图绘制工具

作者: Mu Leiyu
版本: V1.0
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
        """解析台站元数据文件（支持Dataless SEED和StationXML格式）"""
        try:
            if not os.path.exists(dataless_path):
                raise FileNotFoundError(f"台站文件未找到: {dataless_path}")
            
            print(f"正在解析台站文件: {dataless_path}")
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
                raise ValueError("台站文件中未找到任何台站信息")
                
            return True
            
        except Exception as e:
            print(f"解析台站文件时发生错误: {e}")
            return False
    
    def calculate_region(self, padding=None, min_range=2.0):
        """自动计算地图范围"""
        if not self.stations:
            raise ValueError("无台站数据，无法计算地图范围")
        
        lons = [s['longitude'] for s in self.stations]
        lats = [s['latitude'] for s in self.stations]
        
        # 计算台站分布范围
        lon_range = max(lons) - min(lons)
        lat_range = max(lats) - min(lats)
        
        # 动态计算padding：根据台站分布范围自适应
        if padding is None:
            # 使用台站分布范围的10-20%作为padding，最小0.05度，最大0.5度
            auto_padding = max(0.05, min(0.5, max(lon_range, lat_range) * 0.15))
            padding = auto_padding
        
        lon_min = min(lons) - padding
        lon_max = max(lons) + padding
        lat_min = min(lats) - padding
        lat_max = max(lats) + padding
        
        self.region = [lon_min, lon_max, lat_min, lat_max]
        print(f"台站分布范围: 经度 {lon_range:.3f}度, 纬度 {lat_range:.3f}度")
        print(f"自动padding: {padding:.3f}度")
        print(f"最终地图范围: 经度 {lon_max - lon_min:.3f}度, 纬度 {lat_max - lat_min:.3f}度")
        print(f"自动计算地图范围: {self.region}")
        
        return self.region
    
    def set_manual_region(self, region_str):
        """设置手动指定的地图范围"""
        try:
            parts = region_str.split('/')
            if len(parts) != 4:
                raise ValueError("区域格式错误，应为: lon_min/lon_max/lat_min/lat_max")
            
            self.region = [float(p) for p in parts]
            
            # 验证坐标范围
            lon_min, lon_max, lat_min, lat_max = self.region
            if lon_min >= lon_max:
                raise ValueError(f"经度范围错误: {lon_min} >= {lon_max}")
            if lat_min >= lat_max:
                raise ValueError(f"纬度范围错误: {lat_min} >= {lat_max}")
            if lat_min < -90 or lat_max > 90:
                raise ValueError(f"纬度超出范围: {lat_min}, {lat_max}")
            if lon_min < -180 or lon_max > 180:
                raise ValueError(f"经度超出范围: {lon_min}, {lon_max}")
                
            print(f"使用手动指定地图范围: {self.region}")
            
        except ValueError as e:
            print(f"解析区域参数错误: {e}")
            sys.exit(1)
    
    def create_custom_elevation_cpt(self, grid, cpt_file=None):
        """创建或加载自定义海拔色彩表"""
        if cpt_file is None:
            cpt_file = os.path.join("cpt", "colombia.cpt")
        
        print(f"使用CPT配色文件: {cpt_file}")
        
        # 检查CPT文件是否存在
        if not os.path.exists(cpt_file):
            raise FileNotFoundError(f"CPT配色文件未找到: {cpt_file}")
        
        # 复制CPT文件到工作目录
        import shutil
        work_cpt = "custom_elevation.cpt"
        shutil.copy(cpt_file, work_cpt)
        
        return work_cpt
    
    def create_temp_map(self, output_path, resolution="03s", add_labels=False, title="地震台站分布图", cpt_file=None, show_colorbar=False, draw_coast=True):
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
        
        # 配置PyGMT环境
        print("配置PyGMT环境...")
        
        # 获取conda环境路径并设置PATH
        import os
        conda_env = os.path.dirname(os.path.dirname(sys.executable))
        current_path = os.environ.get('PATH', '')
        if f"{conda_env}/bin" not in current_path:
            os.environ['PATH'] = f"{conda_env}/bin:{current_path}"
            print(f"已将{conda_env}/bin添加到PATH")
        
        # 使用默认字体配置，避免CJK字体问题
        pygmt.config(FONT_ANNOT_PRIMARY="12p,Helvetica,black")
        pygmt.config(FONT_LABEL="14p,Helvetica,black") 
        pygmt.config(FONT_TITLE="18p,Helvetica-Bold,black")
        
        print("PyGMT环境配置完成 - 使用默认字体")
        
        # 初始化PyGMT图形
        fig = pygmt.Figure()
        
        try:
            # 使用GMT命令预下载地形数据
            print(f"正在下载{resolution}分辨率地形数据...")
            use_relief = False
            grid_file = None
            
            # 构建GMT分辨率字符串
            resolution_map = {
                '01m': '01m',  # 1弧分
                '30s': '30s',  # 30弧秒 
                '15s': '15s',  # 15弧秒
                '03s': '03s',  # 3弧秒
                '01s': '01s'   # 1弧秒 (最高分辨率)
            }
            gmt_res = resolution_map.get(resolution, '30s')
            
            try:
                import subprocess
                import tempfile
                import os
                
                # 创建缓存文件名 - 使用grd格式而不是nc格式
                lon_min, lon_max, lat_min, lat_max = self.region
                cache_name = f"relief_{gmt_res}_{lon_min:.1f}_{lon_max:.1f}_{lat_min:.1f}_{lat_max:.1f}.grd"
                temp_relief = os.path.join("cache", cache_name)
                
                # 创建缓存目录
                os.makedirs("cache", exist_ok=True)
                
                # 检查缓存文件是否存在
                if os.path.exists(temp_relief):
                    print(f"使用缓存的grd地形数据: {cache_name}")
                    grid_file = temp_relief
                    use_relief = True
                else:
                    # 构建GMT命令下载数据 - 强制使用grd格式
                    gmt_region = f"{lon_min}/{lon_max}/{lat_min}/{lat_max}"
                    
                    cmd = [
                        f"{os.path.dirname(os.path.dirname(sys.executable))}/bin/gmt",
                        "grdcut", 
                        f"@earth_relief_{gmt_res}_g",  # 使用_g后缀强制grd格式
                        f"-R{gmt_region}",
                        f"-G{temp_relief}"
                    ]
                    
                    print(f"下载grd格式地形数据: {cache_name}")
                    print(f"执行命令: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if result.returncode == 0 and os.path.exists(temp_relief):
                        print("grd格式地形数据下载成功并已缓存")
                        grid_file = temp_relief
                        use_relief = True
                    else:
                        print(f"grd格式下载失败，尝试备用方法...")
                        print(f"详细信息: {result.stderr}")
                        # 备用方法：先下载nc格式然后转换为grd
                        temp_nc = temp_relief.replace('.grd', '.nc')
                        cmd_nc = [
                            f"{os.path.dirname(os.path.dirname(sys.executable))}/bin/gmt",
                            "grdcut", 
                            f"@earth_relief_{gmt_res}",
                            f"-R{gmt_region}",
                            f"-G{temp_nc}"
                        ]
                        result_nc = subprocess.run(cmd_nc, capture_output=True, text=True)
                        
                        if result_nc.returncode == 0 and os.path.exists(temp_nc):
                            print("成功下载nc格式，正在转换为grd...")
                            # 转换nc为grd格式
                            cmd_convert = [
                                f"{os.path.dirname(os.path.dirname(sys.executable))}/bin/gmt",
                                "grdconvert",
                                temp_nc,
                                temp_relief
                            ]
                            result_convert = subprocess.run(cmd_convert, capture_output=True, text=True)
                            if result_convert.returncode == 0:
                                print("成功转换为grd格式")
                                grid_file = temp_relief
                                use_relief = True
                                # 删除临时nc文件
                                try:
                                    os.remove(temp_nc)
                                except:
                                    pass
                            else:
                                print("转换grd格式失败，程序退出")
                                sys.exit(1)
                        else:
                            print("无法获取必需的地形数据，程序退出")
                            sys.exit(1)
                    
            except Exception as download_error:
                print(f"错误: 地形数据下载异常 - {download_error}")
                print("无法获取必需的地形数据，程序退出")
                sys.exit(1)
            
            if use_relief and grid_file:
                # 加载自定义海拔色彩表
                custom_cpt = self.create_custom_elevation_cpt(None, cpt_file)
                
                # 读取地形数据获取海拔范围
                try:
                    import xarray as xr
                    grid_data = xr.open_dataarray(grid_file)
                    min_elev = float(grid_data.min().values)
                    max_elev = float(grid_data.max().values)
                    print(f"海拔范围: {min_elev:.0f}m 到 {max_elev:.0f}m")
                except:
                    print("无法读取海拔范围信息")
                
                # 复制自定义配色为最终配色
                import shutil
                shutil.copy(custom_cpt, "final_elevation.cpt")
                
                # 绘制经典地形配色背景
                print("绘制经典地形配色背景...")
                fig.grdimage(
                    grid=grid_file,
                    projection="M22c",  # 更大的地图
                    region=self.region,  # 明确指定区域
                    cmap="final_elevation.cpt",
                    shading="+a315+ne0.3+nt1.0",  # 增强晕渲效果
                    transparency=0  # 不透明，显示完整色彩
                )
            else:
                # 这里不应该到达，因为数据下载失败会直接退出
                print("错误: 无法加载地形数据")
                sys.exit(1)
            
            # 绘制地理要素 - 海岸线和水体
            if draw_coast:
                print("添加地理要素，绘制海岸线和水体...")
                try:
                    # 尝试添加水体覆盖层，强制显示为白色
                    fig.coast(
                        water="white",                       # 强制水体显示为白色
                        shorelines="1/0.3p,black",          # 细黑色海岸线
                        resolution="f"                       # 最高分辨率
                    )
                    print("海岸线和水体绘制完成")
                except Exception as e:
                    print(f"海岸线绘制失败: {e}")
                    # 如果coast失败，尝试使用替代方法
                    try:
                        print("尝试使用替代水体显示方法...")
                        # 基于早期版本参考图的精确水库位置
                        reservoir_x = [116.845, 116.855, 116.857, 116.848, 116.845]
                        reservoir_y = [40.480, 40.480, 40.488, 40.490, 40.480]
                        
                        fig.plot(
                            x=reservoir_x,
                            y=reservoir_y,
                            pen="1p,blue",
                            fill="white"  # 纯白色，模仿早期版本
                        )
                        
                        # 添加水库标注
                        fig.text(
                            text="Reservoir",
                            x=116.851,
                            y=40.485,
                            font="10p,Helvetica-Bold,blue",
                            justify="CM"
                        )
                        print("替代水体显示完成")
                    except Exception as e2:
                        print(f"替代方法也失败: {e2}，继续绘制其他要素...")
            else:
                print("跳过海岸线绘制")
            
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
            
            # 处理标题
            title_to_use = title if title else None
            
            # 添加经纬度标注和标题
            print("添加经纬度标注和标题...")
            
            # 根据地图范围动态计算刻度间隔
            lon_range = self.region[1] - self.region[0]
            lat_range = self.region[3] - self.region[2]
            
            # 计算合适的刻度间隔，确保至少有2个刻度标记
            def calculate_interval(range_deg):
                # 目标：在给定范围内至少显示2个刻度标记
                # 刻度间隔应该小于等于range/3，这样保证至少有2个内部刻度
                target_interval = range_deg / 3.0
                
                # 选择合适的标准间隔
                standard_intervals = [0.05, 0.1, 0.2, 0.25, 0.5, 1.0, 2.0, 5.0]
                
                # 找到小于等于目标间隔的最大标准间隔
                best_interval = standard_intervals[0]  # 默认最小间隔
                for interval in standard_intervals:
                    if interval <= target_interval:
                        best_interval = interval
                    else:
                        break
                
                return best_interval
            
            lon_interval = calculate_interval(lon_range)
            lat_interval = calculate_interval(lat_range)
            
            # 构建frame参数
            x_frame = f"xa{lon_interval}f{lon_interval/2}"  # 主刻度和次刻度
            y_frame = f"ya{lat_interval}f{lat_interval/2}"
            
            print(f"地图范围: 经度{lon_range:.2f}度, 纬度{lat_range:.2f}度")
            print(f"刻度间隔: 经度{lon_interval}度, 纬度{lat_interval}度")
            
            if title_to_use:
                fig.basemap(frame=["WSen+t" + title_to_use, x_frame, y_frame])
            else:
                fig.basemap(frame=["WSen", x_frame, y_frame])
            
            # 添加无边框英文高程图例（可选）
            if show_colorbar and use_relief:
                print("添加高程图例...")
                fig.colorbar(
                    frame=["x+lElevation (m)", "y+lm"],
                    position="JMR+w12c/0.6c+o2.5c/0c"
                    # 移除box参数，不显示边框
                )
            else:
                if not use_relief:
                    print("跳过高程图例显示 (无地形数据)")
                else:
                    print("跳过高程图例显示")
            
            # 不添加指北针和比例尺，保持简洁
            # print("添加比例尺和指北针...")
            # 注释掉指北针和比例尺
            
            # 保存地图
            print(f"保存地图到: {output_path}")
            
            # 检测输出格式
            output_format = Path(output_path).suffix.lower()
            if output_format == '.pdf':
                print("输出PDF格式...")
                fig.savefig(
                    output_path, 
                    crop=True,
                    anti_alias=True
                )
            else:
                # PNG, JPG等光栅格式
                print(f"输出{output_format.upper()}格式...")
                fig.savefig(
                    output_path, 
                    dpi=300, 
                    crop=True,
                    anti_alias=True
                )
            
            # 根据输出格式显示完成信息
            if output_format == '.pdf':
                print("PDF格式地图生成完成！")
            else:
                print("temp_map.png风格地图生成完成！")
            
            # 清理临时文件
            temp_files = ["custom_elevation.cpt", "temp1_base.cpt", "final_elevation.cpt", "gray_base.cpt", "light_base.cpt", "green_base.cpt", "terrain_base.cpt", "soft_base.cpt", "low_elevation.cpt", "high_elevation.cpt"]
            
            # 不删除缓存的地形数据文件，保留供下次使用
            # if use_relief and grid_file and os.path.exists(grid_file):
            #     temp_files.append(grid_file)
                
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass  # 忽略删除失败
            
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
  python stn_plot.py --dataless BJ.dataless --output temp_style_map.png --resolution 03s --labels --title "北京地震台网分布图"
  python stn_plot.py --dataless BJ.dataless --cpt custom_colors.cpt --output custom_map.png
  python stn_plot.py --dataless BJ.dataless --output station_map.pdf --labels --title "Seismic Station Distribution"
        """
    )
    
    parser.add_argument('--dataless', required=True, help='Dataless SEED文件路径')
    parser.add_argument('--output', default='temp_style_map.png', help='输出文件路径 (支持PNG, PDF, JPG格式)')
    parser.add_argument('--region', help='地图范围 lon_min/lon_max/lat_min/lat_max')
    parser.add_argument('--resolution', default='03s', choices=['01m', '30s', '15s', '03s', '01s'], help='地形数据分辨率')
    parser.add_argument('--labels', action='store_true', help='在地图上标注台站名称')
    parser.add_argument('--title', default=None, help='地图标题 (建议使用英文)')
    parser.add_argument('--cpt', help='自定义CPT配色文件路径 (默认使用cpt/colombia.cpt)')
    parser.add_argument('--colorbar', action='store_true', help='显示右侧高程图例色彩条 (默认不显示)')
    parser.add_argument('--padding', type=float, help='地图边界padding (度)，不指定时自动计算')
    parser.add_argument('--min-range', type=float, default=2.0, help='地图最小范围 (度)，确保显示足够的经纬度标记，默认2.0度')
    parser.add_argument('--no-coast', action='store_true', help='不绘制海岸线和边界线')
    
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
        plotter.calculate_region(padding=args.padding, min_range=args.min_range)
    
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
            show_colorbar=args.colorbar,
            draw_coast=not args.no_coast
        )
    except Exception as e:
        print(f"生成地图失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
