"""Write an OpenFOAM (v2412) case for the table-sealed, wall-intake screen.
usage: make_case.py <case_dir> <stand|empty> <flow_m3_per_min> <base_cell_mm> [stand_refine_level=2]
Domain x -90..100, y -140..140, z 0..40 mm. Table z=0 is a wall. A solid cap fills z 30..40 except a chimney with the
outline of the reference core's flat underside, so air can only arrive sideways below seat height and leaves upward
through the whole underside. Side faces are open to still air (total pressure 0); the chimney top draws a fixed flow.
Steady incompressible air at 20 C (nu 1.516e-5 m2/s, rho 1.204 kg/m3), k-omega SST."""
import sys,json,shutil
from pathlib import Path
import numpy as np,trimesh,manifold3d as m3
from shapely.geometry import Polygon
case=Path(sys.argv[1]);kind=sys.argv[2];Q=float(sys.argv[3])/60;h=float(sys.argv[4]);lvl=int(sys.argv[5]) if len(sys.argv)>5 else 2
root=Path(__file__).resolve().parents[3];X0,X1,Y0,Y1,Z1=-90.,100.,-140.,140.,40.
for d in ['system','constant/triSurface','0']:(case/d).mkdir(parents=True,exist_ok=True)
sec=trimesh.load(root/'references/console-model/PS5_Slim.glb').geometry['unnamed_6'].section(plane_origin=[0,0,.5],plane_normal=[0,0,1])
core=max((Polygon(c[:,:2]) for c in sec.discrete if np.linalg.norm(c[0]-c[-1])<.01),key=lambda q:q.area).simplify(.05)
ring=np.asarray(core.exterior.coords)[:-1];ring=ring if Polygon(ring).exterior.is_ccw else ring[::-1]
cap=m3.Manifold.cube((X1-X0+20,Y1-Y0+20,Z1+5-30)).translate((X0-10,Y0-10,30))-m3.Manifold.extrude(m3.CrossSection([ring]),30).translate((0,0,20))
mm=cap.to_mesh();trimesh.Trimesh(np.asarray(mm.vert_properties)[:,:3],np.asarray(mm.tri_verts)).export(case/'constant/triSurface/cap.stl')
if kind=='stand':shutil.copy(root/'designs/v14/output/veil_v14_prototype.stl',case/'constant/triSurface/stand.stl')
A=core.area*1e-6;nx,ny,nz=[int(round(v/h)) for v in (X1-X0,Y1-Y0,Z1)]
k0=3.75e-3;om0=22.;END=int(sys.argv[6]) if len(sys.argv)>6 else 1500  # fields are written once, at the last iteration
def w(name,body,cls='dictionary',loc='system'):
 (case/loc/name).write_text('FoamFile\n{\n    version 2.0;\n    format ascii;\n    class %s;\n    object %s;\n}\n'%(cls,name)+body)
w('blockMeshDict',f'''scale 0.001;
vertices (({X0} {Y0} 0) ({X1} {Y0} 0) ({X1} {Y1} 0) ({X0} {Y1} 0) ({X0} {Y0} {Z1}) ({X1} {Y0} {Z1}) ({X1} {Y1} {Z1}) ({X0} {Y1} {Z1}));
blocks (hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading (1 1 1));
boundary
(
    table {{ type wall; faces ((0 3 2 1)); }}
    outlet {{ type patch; faces ((4 5 6 7)); }}
    sides {{ type patch; faces ((0 1 5 4) (1 2 6 5) (2 3 7 6) (3 0 4 7)); }}
);
''')
geo='    cap.stl { type triSurfaceMesh; name cap; scale 0.001; }\n'+('    stand.stl { type triSurfaceMesh; name stand; scale 0.001; }\n' if kind=='stand' else '')
ref='        cap { level (1 1); patchInfo { type wall; } }\n'+(f'        stand {{ level ({lvl} {lvl}); patchInfo {{ type wall; }} }}\n' if kind=='stand' else '')
w('snappyHexMeshDict',f'''castellatedMesh true; snap true; addLayers false;
geometry
{{
{geo}}}
castellatedMeshControls
{{
    maxLocalCells 4000000; maxGlobalCells 8000000; minRefinementCells 10; nCellsBetweenLevels 2; maxLoadUnbalance 0.2;
    features ();
    refinementSurfaces
    {{
{ref}    }}
    resolveFeatureAngle 30;
    refinementRegions {{}}
    locationInMesh (-0.08013 -0.13031 0.01507);
    allowFreeStandingZoneFaces true;
}}
snapControls {{ nSmoothPatch 3; tolerance 2.0; nSolveIter 30; nRelaxIter 5; nFeatureSnapIter 0; implicitFeatureSnap false; explicitFeatureSnap false; multiRegionFeatureSnap false; }}
addLayersControls {{ relativeSizes true; layers {{}} expansionRatio 1.2; finalLayerThickness 0.3; minThickness 0.1; nGrow 0; featureAngle 60; nRelaxIter 3; nSmoothSurfaceNormals 1; nSmoothNormals 3; nSmoothThickness 10; maxFaceThicknessRatio 0.5; maxThicknessToMedialRatio 0.3; minMedialAxisAngle 90; nBufferCellsNoExtrude 0; nLayerIter 50; }}
meshQualityControls {{ maxNonOrtho 65; maxBoundarySkewness 20; maxInternalSkewness 4; maxConcave 80; minVol 1e-18; minTetQuality -1e30; minArea -1; minTwist 0.02; minDeterminant 0.001; minFaceWeight 0.05; minVolRatio 0.01; minTriangleTwist -1; nSmoothScale 4; errorReduction 0.75; }}
mergeTolerance 1e-6;
''')
w('controlDict',f'''application simpleFoam; startFrom latestTime; startTime 0; stopAt endTime; endTime {END}; deltaT 1;
writeControl timeStep; writeInterval {END}; purgeWrite 1; writeFormat ascii; writePrecision 8; timeFormat general; timePrecision 6; runTimeModifiable false;
functions
{{
    outletP {{ type surfaceFieldValue; libs (fieldFunctionObjects); regionType patch; name outlet; operation areaAverage; fields (p); writeFields false; writeControl timeStep; writeInterval 5; log false; }}
    sidesPhi {{ type surfaceFieldValue; libs (fieldFunctionObjects); regionType patch; name sides; operation sum; fields (phi); writeFields false; writeControl timeStep; writeInterval 5; log false; }}
}}
''')
w('fvSchemes','''ddtSchemes { default steadyState; }
gradSchemes { default cellLimited Gauss linear 1; }
divSchemes { default none; div(phi,U) bounded Gauss linearUpwind grad(U); div(phi,k) bounded Gauss upwind; div(phi,omega) bounded Gauss upwind; div((nuEff*dev2(T(grad(U))))) Gauss linear; }
laplacianSchemes { default Gauss linear limited 0.5; }
interpolationSchemes { default linear; }
snGradSchemes { default limited 0.5; }
wallDist { method meshWave; }
''')
w('fvSolution','''solvers
{
    p { solver GAMG; smoother GaussSeidel; tolerance 1e-8; relTol 0.05; }
    "(U|k|omega)" { solver smoothSolver; smoother symGaussSeidel; tolerance 1e-9; relTol 0.1; }
}
SIMPLE { nNonOrthogonalCorrectors 1; consistent yes; residualControl { p 1e-5; U 1e-6; "(k|omega)" 1e-6; } }
relaxationFactors { equations { U 0.8; k 0.6; omega 0.6; } fields { p 0.5; } }
''')
w('decomposeParDict','numberOfSubdomains 8; method scotch;\n')
w('meshQualityDict','#includeEtc "caseDicts/meshQualityDict"\n')
w('transportProperties','transportModel Newtonian; nu 1.516e-05;\n',loc='constant')
w('turbulenceProperties','simulationType RAS; RAS { RASModel kOmegaSST; turbulence on; printCoeffs off; }\n',loc='constant')
walls='"(table|cap|stand)"'
w('U',f'''dimensions [0 1 -1 0 0 0 0]; internalField uniform (0 0 0);
boundaryField {{ sides {{ type pressureInletOutletVelocity; value uniform (0 0 0); }} outlet {{ type flowRateInletVelocity; volumetricFlowRate {-Q:.8e}; value uniform (0 0 0); }} {walls} {{ type noSlip; }} }}
''','volVectorField','0')
w('p',f'''dimensions [0 2 -2 0 0 0 0]; internalField uniform 0;
boundaryField {{ sides {{ type totalPressure; p0 uniform 0; value uniform 0; }} outlet {{ type zeroGradient; }} {walls} {{ type zeroGradient; }} }}
''','volScalarField','0')
for name,val,wf in [('k',k0,'kqRWallFunction'),('omega',om0,'omegaWallFunction')]:
 w(name,f'''dimensions [0 {2 if name=='k' else 0} {-2 if name=='k' else -1} 0 0 0 0]; internalField uniform {val};
boundaryField {{ sides {{ type inletOutlet; inletValue uniform {val}; value uniform {val}; }} outlet {{ type zeroGradient; }} {walls} {{ type {wf}; value uniform {val}; }} }}
''','volScalarField','0')
w('nut',f'''dimensions [0 2 -1 0 0 0 0]; internalField uniform 0;
boundaryField {{ sides {{ type calculated; value uniform 0; }} outlet {{ type calculated; value uniform 0; }} {walls} {{ type nutUSpaldingWallFunction; value uniform 0; }} }}
''','volScalarField','0')
(case/'case.json').write_text(json.dumps({'kind':kind,'flow_m3_per_min':Q*60,'flow_m3_per_s':Q,'base_cell_mm':h,'stand_refinement_level':lvl if kind=='stand' else None,'chimney_area_m2':A,'mean_outlet_speed_m_per_s':Q/A,'nu_m2_per_s':1.516e-5,'rho_kg_per_m3':1.204,'turbulence':'kOmegaSST, inlet k 3.75e-3 m2/s2 and omega 22 1/s (assumed)'},indent=2))
print(case,kind,'Q',Q,'m3/s  outlet speed',Q/A)
