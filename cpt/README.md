# CPT Color Palette Files

这个目录包含了用于地震台站分布图的CPT (Color Palette Table) 配色文件。

## 文件说明

- `elevation_temp_style.cpt`: 默认的海拔配色方案，使用绿色低地到土黄色高地的过渡

## CPT文件格式

CPT文件使用GMT标准格式，每行包含：
```
高度值1  R1  G1  B1  高度值2  R2  G2  B2
```

- 高度值：海拔米数
- R, G, B：RGB颜色值 (0-255)

## 自定义配色

您可以创建自己的CPT文件，然后使用 `--cpt` 参数指定：

```bash
python plot_temp_style.py --dataless BJ.dataless --cpt your_custom.cpt
```

## 配色设计建议

- 使用渐变色彩确保平滑过渡
- 低海拔区域建议使用冷色调（蓝、绿）
- 高海拔区域建议使用暖色调（黄、棕、红）
- 海面以下使用蓝色系