# Print-service brief / 打印服务说明

**Development sample for quotation and process review. The wider baseline has exploratory stress simulation; compact v8 needs its own review. Neither has passed physical fit, strength, creep or thermal testing.** This is the compact v8 candidate; confirm its process and prototype checks before making a full stand.

- Part: one-piece PS5 Slim Disc stand, white or blue. v8 reinforced size **151.02 × 244.23 × 65.22 mm**; geometric volume 185.89 cm³. STL units are millimeters, 100% scale. 3MF contains geometry only, no machine/material profile. Do not scale the part to fit the printer.
- Exterior wires have actual triangle, circle, X and square cross-sections. Nominal dimensions: triangle circumradius 3 mm, circle radius 1.9 mm, square side 3.5 mm, X envelope 5 mm with 1.6 mm arms. Corners have small relief; junctions overlap and one local reinforcement grows smoothly to 130%. Preserve the profiles during finishing. Under-console ribs are nominally 3.2 mm; reference clearance is 1.5 mm.
- Quote an appropriate FDM process/material and, if offered, a powder-bed nylon process separately. State material grade, process, tolerance, surface finish, and experience with sustained warm loading. No material or machine has been qualified for this design.
- For an FDM feasibility slice, begin upright as exported; roughly 0.4 mm nozzle and 0.16–0.20 mm layers are review starting points only. Select wall/infill settings that actually fill thin members. Review X arms, sharp profiles, crossings, rim undersides, rib arches and support removal. The geometric layer screen found 42 new nonoverlapping islands and local overhangs; it is **not** a slicer or evidence of support-free printing. Pay particular attention near z=10.5, 25.1, 43.3 and 53.3 mm, plus base layers.
- First print `GAUGE_v8_cavity_1.6mm.stl` (~106.91 × 226.98 × 1.6 mm, 3.77 cm³) and `PRINT_TEST_v8_section.stl` (~40.79 × 32 × 49.20 mm, 6.70 cm³) in the proposed process. The gauge checks the outline only and must not carry a console. The coupon is only a local slice of the design, not a certified strength specimen or a complete printability check.
- Return slice previews, omitted/thin-feature warnings, support layout/removal plan, material estimate and test-piece photographs. Supports, brim and postprocessing are additional to geometric volume. Do not repair broken strands with glue and present them as intact manufacturing results.
- Before console use, inspect flatness, rocking, every junction and layer bonding. Verify actual contact on the black core without loading white covers; check plugs, cable bends, disc insertion and all vents. Pads change fit and contact and must be included in that check. Define restrained dummy-load/deformation tests with the fabricator before placing a console. Simulation uses assumed isotropic material and constrained feet; it does not qualify real printing or stability.

## 可直接发给淘宝 / 阿里巴巴商家

这是 PS5 Slim 光驱版支架的**研发样件**。较宽的基准版已有探索性应力仿真，紧凑 v8 需单独审核。两个版本均尚未通过实际装机、承重、长期蠕变或散热测试。请先确认工艺和样件检查，再打印完整支架。

1. v8 加强版尺寸约 **151.02 × 244.23 × 65.22 mm**，一体打印，白色或蓝色。实体几何体积约 185.89 cm³，不含支撑/裙边。STL 请按毫米、100% 导入；3MF 仅含几何数据。不能为了适配打印平台而整体缩放。
2. 外部网状线材的**截面**分别为三角形、圆形、X 和正方形，不是要求网孔做成这些图案。名义尺寸：三角形外接圆半径 3 mm，圆半径 1.9 mm，正方形边长 3.5 mm，X 外包尺寸 5 mm、细臂宽 1.6 mm。局部连接处平滑加粗至 130%；下部肋厚约 3.2 mm，参考机身名义间隙 1.5 mm。后处理不要磨掉截面特征或改变装配面。
3. 请说明材料牌号、工艺、精度、层高、表面处理，以及持续受载和温热环境下的适用性。可以分别提供 FDM 和尼龙粉末烧结类工艺报价；材料尚未完成验证。
4. FDM 请按导出方向直立进行切片评估。0.4 mm 喷嘴、0.16–0.20 mm 层高仅作为初始评估参考，请以贵方工艺为准。重点检查 X 的细臂、交叉连接、顶部边缘、下方拱肋及支撑拆除方式。几何分层检查发现 42 次与前层无直接重叠的小区域，**不能默认免支撑**。请重点检查约 10.5 / 25.1 / 43.3 / 53.3 mm 高度及底部层。
5. 请先用拟用于完整支架的同一工艺打印轮廓量规 `GAUGE_v8_cavity_1.6mm.stl` 和小段测试件 `PRINT_TEST_v8_section.stl`。量规只检查外形，不可承重；测试件仅覆盖局部，不能代替完整工艺和强度验证。请提供切片预览、薄壁/漏打提示、支撑方案、耗材估算和样件照片。
6. 完整样件需检查平整度、层间结合、各连接处、黑色机身底部接触，以及接口、线缆、光盘和通风孔避让。不要让白色外壳承重。防滑垫会改变间隙及接触，需一并检查。先用受约束的模拟配重做承重和变形测试，再考虑放置主机；不能把仿真结果当作实物安全认证。
