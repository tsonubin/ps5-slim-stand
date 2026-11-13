# v15 print brief / 打印说明

**Check on your own console first.** v15 seats the console on the bottoms of its two white covers, the way it stands on a desk. That layout comes from a phone scan of one CFI-2009, not from a drawing. Before ordering, stand your console on a flat table and confirm it rests on the cover bottoms without rocking, with the black base clear of the table. / **请先在自己的主机上确认。** v15 让主机以两块白色外壳的底边落座，与直接立在桌面上相同。该布局来自对一台 CFI-2009 的手机扫描，而非图纸。下单前请把主机立在平整桌面上，确认它靠外壳底边站稳、不晃动，且黑色底面不接触桌面。

**Development prototype.** The numbers below come from simulation and data sheets. Nothing has been printed, fitted, loaded or heat-tested yet. Engineering detail is in [README.md](README.md).

## Plan

1. **Fit check at home, PETG, Bambu Lab H2D.** Print only the cavity gauge and the local coupon. Check the gauge against the console outline and inspect the coupon's openings, rib and wall. Neither part can carry the console.
2. **Final part by laser sintering (SLS), plain PA12 nylon, white, bead-blasted**, ordered from the UnionTech service. One piece, no supports.
3. HP Multi Jet Fusion PA12 only if a black part is wanted instead of white.

## Files

| File | Size | Volume | Use |
|---|---|---:|---|
| `output/veil_v15_prototype.3mf` (or `.stl`) | 152.83 × 247.08 × 40.70 mm | 78.14 cm³ | Final part. About 73 g at the PA 2200 data-sheet density of 0.93 g/cm³ |
| `output/GAUGE_v15_cavity_1.6mm.stl` | 106.91 × 227.00 × 1.60 mm | 3.77 cm³ | Cavity outline gauge |
| `output/PRINT_TEST_v15_section.stl` | 58.00 × 36.00 × 40.70 mm | 6.42 cm³ | Local section: wall, openings, rib, one seat land |

Millimetres, 100% scale. The files hold geometry only, no printer settings. Do not scale the part to fit a build volume.

## For the SLS service

- Material: plain PA12, white, no glass or mineral fill. **Please state which PA12 powder and machine you run.** The stress numbers in the README use EOS PA 2200 data-sheet values (modulus 1,650 MPa, tensile strength 48 MPa in the plane and 42 MPa along the build direction); another powder may differ.
- Finish: bead-blasted, natural white, no dye, no vapour smoothing, no coating.
- Orientation: flat, base down, as modelled. If you need another orientation, say so before printing, because strength along the build direction is lower.
- Wall thickness is 2.8 mm at the two tight ends and 3.5 mm along the long sides. Ribs are 2.8 mm. The smallest designed radius on the added rib-foot blends is 1.5 mm. Please report any feature you consider too thin, and any powder you cannot clear from the openings or from under the ribs.
- Do not fill, thicken or close any opening, and do not add a floor. The 72 wall openings are the air path.
- Keep these as printed: the four flat pad tops at 30 mm height (the bottoms of the console's white covers rest on them, so the four tops must lie in one plane), the flat base ring, and the inner cavity outline (1.5 mm nominal clearance to the console).
- Please return: quoted tolerance, expected flatness of the base ring and of the four pad tops, and photographs before shipping.

## For the PETG fit check (gauge and coupon only)

Bambu PETG HF, dried as Bambu recommends (65 °C for 8 h). Slice normally; the gauge is a flat ring and the coupon may need support under the rib arch. The check is for outline fit and for how the openings and rib look at full scale. It is not a strength test of the final part.

| Property | PETG HF, printed, X-Y | PETG HF, printed, Z | PA 2200 (SLS), X-Y / Z |
|---|---:|---:|---:|
| Tensile modulus | 1,810 ± 190 MPa | 1,540 ± 130 MPa | 1,650 / 1,650 MPa |
| Tensile strength | 34 ± 4 MPa | 23 ± 4 MPa | 48 / 42 MPa |
| Heat deflection, 1.80 MPa | 62 °C | | 64 / 57 °C |
| Heat deflection, 0.45 MPa | 69 °C | | 157 / 145 °C |

PETG values are from Bambu Lab's PETG HF technical data sheet V1.0 ([download link on Bambu's PETG HF page](https://bambulab.com/en/filament/petg-hf)); they were read from a search-indexed copy of the sheet, so check them against the current sheet before relying on them. PA 2200 values are from the EOS data sheet cited in the README.

If the **whole stand** were ever printed in PETG, the linear results in the README scale like this: stress is unchanged, and deflection scales with 1,650 ÷ modulus, which is 0.91× using the X-Y modulus and 1.07× using the Z modulus. That assumes the same Poisson's ratio, which Bambu's sheet does not give. PETG's tensile strength is 29% lower in the plane and 45% lower between layers than PA 2200's, and its 0.45 MPa heat-deflection temperature is 69 °C against 157 °C, so the PA12 margins do not carry over. PETG is for the fit check only.

## Still open before the stand carries a console

- **Rear grille clearance.** Teardown photographs of the Slim show a lower rear grille. The rim stands 8–11 mm above the seat. Whether it overlaps that grille on real hardware is not checked.
- **Fan flow** through the underside slots is unmeasured. The airflow results are comparisons under assumed flows, not a cooling prediction.
- Creep under the constant weight and softening in warm air are not estimated.
- **Step between covers and black base.** The scan shows the covers 2–3 mm proud of the black base, but its mesh is too coarse to trust that figure. The rib crests are 1 mm below the seat, so the stand needs at least a visible gap there. Measure it with a ruler.
- Check on the real console: it rests on the four pads by its white covers; the row of vent slots under the black base is not covered; cables and disc slot are clear; the stand does not rock.

---

## 发给打印服务商（中文）

**这是开发样件。** 以下数据来自仿真和材料数据表，尚未实际打印、装机、承重或做温升测试。

### 计划

1. **先在家用 PETG（Bambu Lab H2D）做装配检查**：只打印量规和局部测试件，用量规核对主机外形，观察局部件的开孔、筋和壁。两者都不能承托主机。
2. **正式件采用 SLS 激光烧结，纯 PA12 尼龙，白色，喷砂处理**，由联泰（UnionTech）打印服务制作。整体一件，无需支撑。
3. 只有需要黑色时才改用 HP MJF PA12。

### 文件

| 文件 | 尺寸 | 体积 | 用途 |
|---|---|---:|---|
| `output/veil_v15_prototype.3mf`（或 `.stl`） | 152.83 × 247.08 × 40.70 mm | 78.14 cm³ | 正式件；按 PA 2200 数据表密度 0.93 g/cm³ 约 73 g |
| `output/GAUGE_v15_cavity_1.6mm.stl` | 106.91 × 227.00 × 1.60 mm | 3.77 cm³ | 装配腔轮廓量规 |
| `output/PRINT_TEST_v15_section.stl` | 58.00 × 36.00 × 40.70 mm | 6.42 cm³ | 局部件：壁、开孔、筋、一个支撑垫 |

单位毫米，按 100% 导入。文件只含几何，不含打印参数。请勿为适配成型仓而缩放。

### SLS 要求

- 材料：纯 PA12，白色，不加玻纤或矿物填充。**请告知所用 PA12 粉末牌号和设备型号。** 我们的受力计算采用 EOS PA 2200 数据表数值（拉伸模量 1,650 MPa；拉伸强度平面内 48 MPa、成型方向 42 MPa），其他粉末可能不同。
- 表面：喷砂，本白色；不染色，不做蒸汽平滑，不喷涂。
- 摆放：按模型方向平放、底面朝下。如需改变方向请先告知，因为成型方向强度较低。
- 壁厚：两端较紧处 2.8 mm，长边 3.5 mm；筋厚 2.8 mm；筋脚新增圆角的最小设计半径为 1.5 mm。如认为有过薄特征，或开孔内、筋下方有无法清除的余粉，请说明。
- 请勿填孔、加厚、封闭任何开孔，也不要加底板。72 个壁面开孔是进风通道。
- 请保持原样：高度 30 mm 的四个平顶支撑垫（主机白色外壳的底边落在上面，四个顶面必须共面）、平整的底圈、内腔轮廓（与主机名义间隙 1.5 mm）。
- 请提供：可达到的公差、底圈和四个支撑垫顶面的预期平面度，以及发货前的照片。

### PETG 装配检查（仅量规和局部件）

使用 Bambu PETG HF，按官方建议烘干（65 °C，8 小时）。正常切片即可；量规是平的环，局部件的筋拱下方可能需要支撑。目的是检查外形配合以及开孔和筋的实际观感，不是正式件的强度测试。

| 性能 | PETG HF 打印件 X-Y | PETG HF 打印件 Z | PA 2200（SLS）X-Y / Z |
|---|---:|---:|---:|
| 拉伸模量 | 1,810 ± 190 MPa | 1,540 ± 130 MPa | 1,650 / 1,650 MPa |
| 拉伸强度 | 34 ± 4 MPa | 23 ± 4 MPa | 48 / 42 MPa |
| 热变形温度（1.80 MPa） | 62 °C | | 64 / 57 °C |
| 热变形温度（0.45 MPa） | 69 °C | | 157 / 145 °C |

PETG 数值来自 Bambu Lab PETG HF 技术数据表 V1.0（经搜索引擎收录的副本读取，使用前请与官网现行版本核对）；PA 2200 数值来自 EOS 数据表。

如果整件改用 PETG：线弹性结果中应力不变，变形按 1,650 ÷ 模量换算（按 X-Y 模量为 0.91 倍，按 Z 模量为 1.07 倍，假设泊松比相同）。但 PETG 的拉伸强度平面内低 29%、层间低 45%，0.45 MPa 热变形温度为 69 °C（PA 2200 为 157 °C），因此 PA12 的安全余量不适用于 PETG。PETG 只用于装配检查。

### 承托主机之前仍需确认

- **后下方格栅间距**：Slim 拆解照片显示机身后下方有格栅；支架上沿高出支撑面 8–11 mm，与真实格栅是否重叠尚未核实。
- 经底部进风槽的**实际风量**未测量；气流结果是在假设风量下的对比，不是散热预测。
- 长期受载蠕变和温热环境下的软化未作估算。
- **外壳与黑色底面的高差**：扫描显示外壳比黑色底面低 2–3 mm，但扫描网格较粗，此数值不可靠。筋顶比支撑面低 1 mm，因此该处必须有可见间隙，请用尺实测。
- 实机检查：主机以白色外壳落在四个支撑垫上；黑色底面的一排进风槽不被遮挡；线缆和光驱口不受阻；支架不晃动。
