# v11 print-service brief / 打印服务说明

**Development prototype for process review, not production approval. No v11 FEA or physical fit, print, strength, creep or thermal qualification has been completed.** Final size **151.71 × 244.56 × 53.22 mm**, geometric volume **128.41 cm³**. Use only the final `veil_v11_prototype.3mf` or matching decompressed STL, not root-only/preblend cache files. The `.stl.gz` is lossless gzip; decompress it before importing. Import in millimeters at 100%; 3MF contains geometry only.

- The final local coupon is 58 × 36 × 48.17 mm, 9.47 cm³; the gauge is about 106.91 × 227 × 1.6 mm, 3.77 cm³.
- Dense round weave, nominal midspan diameter 3.3 mm. Strands enlarge smoothly toward rounded top/base rings; the base ring has a flat desk contact. Three curved supporting rails and two ties carry the intended load. Maintain the reference cavity, 30 mm seat height and contact surfaces during finishing.
- Ring roots and selected crossings have local blended additions. The final geometry is triangulated; mathematical guide-curve continuity does not guarantee a perfectly smooth printed surface or a qualified joint. Do not polish away structural roots or alter the cavity to hide surface artifacts.
- Please quote material grade, process, tolerances, finishing and suitability for sustained warm loading. Assess FDM orientation, supports and removal around the weave, rounded rings and broad rail arches. If offered, assess powder-bed nylon separately. Neither material nor process has been qualified. The geometric 0.2 mm layer screen flags two nonoverlapping-island events and a maximum 184.65 mm² overhang-growth area near z=14.1 mm; it is not a slicer. **Do not assume support-free printing.**
- First print `GAUGE_v11_cavity_1.6mm.stl` and `PRINT_TEST_v11_section.stl` in the proposed process. The gauge checks outline only and cannot support a console. The coupon includes a real tie/web region but is not a complete printability or strength test. Return slice previews, thin-feature warnings, support/removal plan, material estimate and photographs.
- Before console use, inspect flatness, rocking, bonding and junctions. Verify black-core contact without loading white covers, plus plugs/cables, disc access and all vents. Any pads change fit/contact. Use agreed restrained dummy-load/deformation tests before placing the console; thermal testing is separate. Historical v7 stress fields do not qualify v11.

## 可发给淘宝 / 阿里巴巴商家

这是 **v11 研发样件，仅用于工艺审核，不是量产批准文件**。v11 尚未做应力仿真，也未完成实际装机、打印、承重、长期蠕变或散热验证。最终尺寸约 **151.71 × 244.56 × 53.22 mm**，几何体积 **128.41 cm³**。只使用最终 `veil_v11_prototype.3mf` 或对应解压后的 STL（`.stl.gz` 为无损 gzip 压缩），不要使用 root-only / preblend 中间缓存。按毫米、100% 导入，不能自动缩放；3MF 不含打印参数。

1. 外网采用中段名义直径 3.3 mm 的圆截面线材，端部逐渐加粗并连接圆润的上下环。底环保留平面桌面接触；下部为三条弯曲支撑轨及两条连接肋。后处理需保留机身间隙、30 mm 支撑高度及接触面。
2. 线材根部和部分交叉处有局部平滑过渡加料。模型是三角网格；数学引导线的连续性不等于实际打印表面绝对光滑，也不代表连接强度已验证。不能为了掩盖表面痕迹而磨薄连接根部或改变装配腔。
3. 请说明材料牌号、工艺、精度、表面处理和持续受载/温热环境适用性。FDM 需实际审核方向、支撑及拆除，重点检查网格、圆润环和底部宽拱。如可提供，可另行评估尼龙粉末床类工艺；材料和工艺均尚未验证，**不能默认免支撑**。
几何分层检查有两次与前层无直接重叠的小区域，14.1 mm 高度处的悬垂生长区域最大约 184.65 mm²；这不是实际切片结果。

4. 请先用拟用于完整件的同一工艺打印 `GAUGE_v11_cavity_1.6mm.stl` 量规和 `PRINT_TEST_v11_section.stl` 局部样件。量规约 106.91 × 227 × 1.6 mm、3.77 cm³，不可承重；局部样件约 58 × 36 × 48.17 mm、9.47 cm³，不能代表全部结构或强度。请提供切片预览、薄壁提示、支撑/拆除方案、耗材估算和照片。
5. 完整样件需检查平整度、晃动、层间结合、连接处、黑色机身底部接触，以及接口/线缆/光盘/通风孔避让。不要让白色外壳承重；防滑垫需纳入装配检查。先以受约束的模拟配重测试，再考虑放置主机。旧 v7 应力图不能用于证明 v11 安全。
