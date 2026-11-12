# v10 print-service brief / 打印服务说明

**Aesthetic review prototype, not yet user-approved. Request process review before a full print. No v10 stress simulation or physical fit, strength, creep or thermal qualification has been completed.**

- Complete part: `veil_v10_prototype.3mf` or matching STL, **151.32 × 244.47 × 53.22 mm**, geometric volume 131.40 cm³. White or blue. Import in millimeters at 100%; do not scale to fit a printer. 3MF contains geometry only.
- Exterior: nominal **3.3 mm round strands**, dense intersecting weave. Underside: three curved rails and two ties, nominally 3.2 mm thick, with smooth arch openings. Preserve the 30 mm seat, nominal 1.5 mm reference clearance and contact surfaces during finishing.
- Please quote process/material grade, tolerance, layer height, finishing and sustained warm-load suitability. Assess both FDM feasibility and, if offered, powder-bed nylon. Neither process nor any material is qualified for this geometry.
- FDM needs a real slice and support-removal review. Start from the exported upright orientation, but compare alternatives. Inspect dense strand crossings, thin features, rim undersides and especially the broad rail arches near z=12–15 mm. The geometric screen flags two nonoverlapping-island events and up to 191.65 mm² beyond a 45° layer-growth envelope at z=14.1 mm. **Do not assume support-free printing.** Settings must come from the provider's process, not from the mesh file.
- Print the same-process gauge and local coupon first: `GAUGE_v10_cavity_1.6mm.stl` (~106.91 × 227 × 1.6 mm, 3.77 cm³) and `PRINT_TEST_v10_section.stl` (~58 × 36 × 48.14 mm, 9.74 cm³). The gauge cannot support a console; the coupon includes a transverse tie and outer-web junction but does not cover all arches or validate strength.
- Return slice previews, support layout/removal plan, thin-feature warnings, material estimate and sample photographs. Supports/brim and finishing add to geometric volume. Do not glue broken strands and present them as intact manufacturing results.
- Before service use, inspect flatness, rocking, bonding and junctions; verify actual black-core contact without loading white covers. Check plugs, cables, disc access and all vents. Any pads alter fit/contact. Agree restrained dummy-load and deformation tests before placing a console; prototype thermal checks remain separate.

## 可发给淘宝 / 阿里巴巴商家

这是 PS5 Slim 光驱版支架的 **v10 外观评审样件，尚未获得用户最终外观确认**。请先审核工艺，不要直接按已验证成品处理。v10 尚未完成应力仿真，也未做实际装机、承重、长期蠕变或散热验证。

1. 完整模型为 `veil_v10_prototype.3mf` 或对应 STL，尺寸约 **151.32 × 244.47 × 53.22 mm**，几何体积 131.40 cm³，白色或蓝色。按毫米、100% 导入，不能为了适配平台而缩放；3MF 不含打印参数。
2. 外部为名义直径 **3.3 mm 的圆截面线材**交织网状结构，底部为三条弯曲支撑轨和两条连接肋，不是星形中心结构。肋厚约 3.2 mm，带平滑拱形开口。后处理需保留 30 mm 支撑高度、名义 1.5 mm 机身间隙及接触面。
3. 请说明材料牌号、工艺、精度、层高、表面处理和持续受载/温热环境适用性。如可提供，分别评估 FDM 和尼龙粉末床类工艺。材料及工艺均尚未验证。
4. FDM 必须实际切片并审核支撑拆除。可从导出直立方向开始比较方案，重点检查密集交叉线材、薄壁、顶边下方，以及约 12–15 mm 高度的宽拱。几何检查有两次与前层无直接重叠的小区域；14.1 mm 处超出前层 45° 生长范围的面积约 191.65 mm²。**不能默认免支撑**，也不能把几何分层检查当作切片结果。
5. 请先按拟用于完整件的同一工艺打印 `GAUGE_v10_cavity_1.6mm.stl` 量规及 `PRINT_TEST_v10_section.stl` 局部样件。量规约 106.91 × 227 × 1.6 mm，不可承重；局部样件约 58 × 36 × 48.14 mm，包含横向连接肋和外网交界，但不能代表全部拱结构或强度。
6. 请提供切片预览、支撑及拆除方案、薄壁/漏打提示、耗材估算和样件照片。完整样件还需检查平整度、层间结合、各连接处、黑色机身底部接触和接口/线缆/光盘/通风孔避让。不要让白色外壳承重；先以受约束的模拟配重验证，再考虑放置主机。
