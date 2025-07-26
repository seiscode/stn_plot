#!/usr/bin/env python3
"""
生成CPT配色方案预览图片的脚本
为cpt目录下的每个CPT文件生成对应的PNG预览图
"""

import os
import sys
from pathlib import Path

# 检查必要的库
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


def generate_cpt_preview(cpt_file_path, output_png_path, dataless_path):
    """
    为指定的CPT文件生成预览图
    
    Args:
        cpt_file_path: CPT文件路径
        output_png_path: 输出PNG文件路径
        dataless_path: Dataless SEED文件路径
    """
    try:
        print(f"正在为 {os.path.basename(cpt_file_path)} 生成预览图...")
        
        # 解析Dataless文件
        if not os.path.exists(dataless_path):
            print(f"错误: 未找到Dataless文件: {dataless_path}")
            return False
            
        inventory = read_inventory(dataless_path)
        
        # 提取台站信息
        stations = []
        for network in inventory:
            for station in network:
                station_info = {
                    'network': network.code,
                    'station': station.code,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'elevation': station.elevation if station.elevation else 0
                }
                stations.append(station_info)
        
        if not stations:
            print("错误: 未找到台站信息")
            return False
        
        # 计算地图范围
        lons = [s['longitude'] for s in stations]
        lats = [s['latitude'] for s in stations]
        padding = 0.5
        region = [
            min(lons) - padding,
            max(lons) + padding,
            min(lats) - padding,
            max(lats) + padding
        ]
        
        # 设置GMT配置
        pygmt.config(MAP_FRAME_TYPE="plain")
        pygmt.config(MAP_FRAME_PEN="0p")
        
        # 初始化PyGMT图形
        fig = pygmt.Figure()
        
        # 加载地形数据
        grid = pygmt.datasets.load_earth_relief(
            resolution="03s", 
            region=region
        )
        
        # 复制CPT文件到工作目录
        import shutil
        work_cpt = "temp_preview.cpt"
        shutil.copy(cpt_file_path, work_cpt)
        
        # 绘制地形背景
        fig.grdimage(
            grid=grid,
            projection="M15c",
            cmap=work_cpt,
            shading="+a315+ne0.2+nt0.8",
            transparency=0
        )
        
        # 绘制地理要素
        fig.coast(
            shorelines="1/0.05p,180/180/185",
            water="230/240/245",
            lakes="230/240/245"
        )
        
        # 绘制台站
        fig.plot(
            x=lons,
            y=lats,
            style="t0.5c",
            fill="180/40/40",
            pen="1.0p,120/20/20"
        )
        
        # 添加边框
        fig.basemap(frame=["a1f1", "WSen"])
        
        # 添加标题
        cpt_name = os.path.splitext(os.path.basename(cpt_file_path))[0]
        center_lon = (region[0] + region[1]) / 2
        title_lat = region[3] + (region[3] - region[2]) * 0.08
        
        fig.text(
            text=f"CPT Preview: {cpt_name}",
            x=center_lon,
            y=title_lat,
            font="16p,Helvetica-Bold,gray30",
            justify="CB"
        )
        
        # 添加色彩条
        fig.colorbar(
            frame=["x+lElevation (m)", "y+lm"],
            position="JMR+w10c/0.5c+o1.5c/0c"
        )
        
        # 保存图片
        fig.savefig(
            output_png_path,
            dpi=300,
            crop=True,
            anti_alias=True
        )
        
        # 清理临时文件
        if os.path.exists(work_cpt):
            os.remove(work_cpt)
        
        print(f"成功生成预览图: {output_png_path}")
        return True
        
    except Exception as e:
        print(f"生成预览图时发生错误: {e}")
        # 清理临时文件
        if os.path.exists("temp_preview.cpt"):
            os.remove("temp_preview.cpt")
        return False


def main():
    """主函数"""
    # 获取当前脚本目录
    script_dir = Path(__file__).parent
    cpt_dir = script_dir / "cpt"
    dataless_file = script_dir / "BJ.dataless"
    
    if not cpt_dir.exists():
        print(f"错误: CPT目录不存在: {cpt_dir}")
        sys.exit(1)
        
    if not dataless_file.exists():
        print(f"错误: Dataless文件不存在: {dataless_file}")
        sys.exit(1)
    
    # 查找所有CPT文件
    cpt_files = list(cpt_dir.glob("*.cpt"))
    
    if not cpt_files:
        print(f"未在 {cpt_dir} 目录中找到CPT文件")
        sys.exit(1)
    
    print(f"找到 {len(cpt_files)} 个CPT文件")
    
    success_count = 0
    total_count = len(cpt_files)
    
    # 为每个CPT文件生成预览图
    for cpt_file in cpt_files:
        # 生成对应的PNG文件名
        png_name = cpt_file.stem + ".png"
        png_path = cpt_dir / png_name
        
        # 生成预览图
        if generate_cpt_preview(str(cpt_file), str(png_path), str(dataless_file)):
            success_count += 1
        
        print()  # 添加空行分隔
    
    print(f"预览图生成完成: {success_count}/{total_count} 成功")
    
    if success_count == total_count:
        print("所有CPT文件的预览图都已成功生成！")
    else:
        print(f"有 {total_count - success_count} 个文件生成失败")


if __name__ == "__main__":
    main()