# v13 prototype brief / 打印样件说明

**Development prototype. Request process advice and small samples before a full print. Fresh numerical analyses are separate from physical qualification: actual fit, load, creep and thermal behavior remain untested.**

- Overall size **150.34 × 241.28 × 40.70 mm**, geometric volume **74.61 cm³** (excluding supports/brim). Gauge: 106.91 × 227 × 1.6 mm, 3.77 cm³. Local coupon: 58 × 36 × 40.70 mm, 6.93 cm³.
- Use `veil_v13_prototype.3mf` or matching STL in millimeters at 100%. The 3MF contains geometry only; do not scale the cavity to fit a printer. White or blue remains the intended finish.
- The upper rim is nearly level (38.03–40.70 mm), and the lower contact loop is planar. The exterior is a nominal 2.8 mm sculpted shell with 72 irregular rounded openings and integrated upper/lower edges. It is not a collection of pipes. Preserve connecting material between openings, the 30 mm seat, reference cavity and narrowed support-contact edges during finishing.
- Quote material grade, process, tolerances and finishing. Review sustained warm loading. For FDM, inspect aperture roofs, narrow connecting regions, underside arches, supports and their removal in a real slicer; do not assume support-free printing. A powder-bed process may also be quoted, but is not qualified by this model.
- First print the provided cavity gauge and local coupon in the proposed process. The gauge cannot carry a console; the coupon does not cover every aperture/arch or establish strength. Return slice previews, support/removal plan, thin-feature warnings, material estimate and sample photographs.
- Before use, verify contact on the black core without loading white covers; inspect flatness, bonding, all connections, plugs/cables, disc access and vents. Pads change fit/contact. Use agreed restrained dummy-load tests before placing the console; thermal checks remain separate. Historical v7 stress fields are not validation of v13.

## 可发给淘宝 / 阿里巴巴商家

这是 **v13 开发样件，不是已验证量产件**。请先提供工艺建议并打印小样。数值受力和气流分析需结合各自假设阅读，不能替代实际装机、承重、长期蠕变或散热验证。

1. 完整件尺寸约 **150.34 × 241.28 × 40.70 mm**，几何体积 **74.61 cm³**，不含支撑/裙边。量规约 106.91 × 227 × 1.6 mm、3.77 cm³；局部件约 58 × 36 × 40.70 mm、6.93 cm³。使用 `veil_v13_prototype.3mf` 或对应 STL，按毫米、100% 导入，不能为了适配平台而缩放装配腔。3MF 不含打印参数；计划采用白色或蓝色。
2. 上沿高度约 38.03–40.70 mm，下沿接触桌面并保持共面。外部是名义厚度 2.8 mm 的连续曲面壳体，带 72 个不规则圆润开孔，上下边缘与壳体一体成形，不是独立线管拼接。后处理需保留孔间连接材料、30 mm 支撑高度、机身装配腔和支撑接触边缘。
3. 请说明材料牌号、工艺、精度、表面处理及持续受载/温热环境适用性。FDM 需实际审核开孔顶部、窄连接处、下方宽拱及支撑拆除，不能默认免支撑。如可提供，也可报价粉末床类工艺，但模型本身并未验证该工艺。
4. 请先以拟用于完整件的同一工艺打印量规和局部测试件。量规不可承重；局部件不能代表所有开孔/拱结构或强度。请提供切片预览、支撑/拆除方案、薄壁提示、耗材估算和照片。
5. 使用前需验证黑色机身底部接触，不要让白色外壳承重，并检查平整度、层间结合、连接处、接口/线缆/光盘和全部通风孔。防滑垫需纳入装配检查。先做受约束的模拟配重测试，再考虑放置主机。旧 v7 应力图不能用于证明 v13 安全。

The actual console vent map is unresolved. Do not add a continuous floor, fill apertures, enlarge pads over possible openings or close side passages without rechecking airflow and physical vent clearance. The user-confirmed sealed-bottom condition is an impermeable desktop with side apertures open, not permission to block console vents.

实际主机底部风口尚待确认。不要擅自增加封闭底板、填孔，或用加大的脚垫遮住可能的风口；修改侧面通道后需重新检查。用户确认型号为 CFI-20xx；底部密闭分析按实心桌面、侧面网孔开放处理，不表示可以堵住主机通风口。

**Hold full service-use printing pending rear-grille clearance review.** Slim teardown imagery shows a lower rear grille, while this rim rises about 8.03–10.70 mm above the seat. Its overlap/gap to the real grille is unresolved. Do not interpret the open mesh or conditional airflow calculation as clearance approval.

**先核实后下方格栅间距，再考虑完整件用于承托主机。** Slim 拆解图可见后下方格栅，本支架上沿高于支撑面约 8.03–10.70 mm；与真实格栅是否重叠、间距多大尚未确认。网孔开放和条件性气流计算不等于风口已通过遮挡检查。
