"""Write an OpenFOAM (v2412) case for air reaching the console's real underside vents.
usage: make_case.py <case_dir> <stand|hover|desk> <flow_m3_per_min> <base_cell_mm> [stand_refine_level=2] [iterations=1500] [step_mm=2.5]
stand: console on the v15 stand, covers resting at 30 mm.   hover: the same height with no stand (the stand's own cost).
desk : console standing straight on the desk, as it does without any stand.
Console = its footprint (source/outline.json) extruded upward from the cover bottoms. The black base is recessed above
the cover bottoms by <step> (2-3 mm in the scan; open at the front and rear ends). Air leaves ONLY through the 18 vent
slots measured in references/console-scan/underside.json; each slot is a short duct through the console to the outlet.
Domain x -90..100, y -140..140 mm; desk z=0 is a wall; the four sides are open to still air (total pressure 0); a lid
closes the top outside the slots. Steady incompressible air at 20 C (nu 1.516e-5 m2/s, rho 1.204 kg/m3), k-omega SST.
The flow through these slots is NOT known; the flow rates are assumptions."""
import sys,json,shutil
from pathlib import Path
import numpy as np,trimesh,manifold3d as m3
case=Path(sys.argv[1]);kind=sys.argv[2];Q=float(sys.argv[3])/60;h=float(sys.argv[4]);lvl=int(sys.argv[5]) if len(sys.argv)>5 else 2;STEP=float(sys.argv[7]) if len(sys.argv)>7 else 2.5
here=Path(__file__).resolve().parent;root=here.parents[2];X0,X1,Y0,Y1=-90.,100.,-140.,140.;H=0. if kind=='desk' else 30.;Z1=H+15.
for d in ['system','constant/triSurface','0']:(case/d).mkdir(parents=True,exist_ok=True)
OL=json.loads((here.parent/'source/outline.json').read_text());OY=np.array(OL['y'])[::-1];PL=np.array(OL['plain'])[::-1];DI=np.array(OL['disc'])[::-1];y=np.arange(-108,108.01,1.5)
CSn=m3.CrossSection;foot=CSn([np.vstack([np.c_[np.interp(y,OY,DI),y],np.c_[-np.interp(y[::-1],OY,PL),y[::-1]]])])
U=json.loads((root/'references/console-scan/underside.json').read_text());yy=np.linspace(-125,125,101)
black=CSn([np.vstack([np.c_[np.polyval(U['drive_cover_edge_x_of_y']['poly_deg1'],yy),yy],np.c_[np.polyval(U['left_rim_inner_edge_x_of_y']['poly_deg2'],yy[::-1]),yy[::-1]]])])
slots=[s for s in U['vent_slots']];ducts=m3.Manifold.batch_boolean([m3.Manifold.cube((s['x'][1]-s['x'][0],s['y'][1]-s['y'][0],Z1+10-H)).translate((s['x'][0],s['y'][0],H+STEP-.5)) for s in slots],m3.OpType.Add)
lid=m3.Manifold.cube((X1-X0+20,Y1-Y0+20,7.5)).translate((X0-10,Y0-10,Z1-2.5))
cap=(lid+m3.Manifold.extrude(foot,Z1+5-H).translate((0,0,H)))-m3.Manifold.extrude(black,STEP+1).translate((0,0,H-1))-ducts
mm=cap.to_mesh();trimesh.Trimesh(np.asarray(mm.vert_properties)[:,:3],np.asarray(mm.tri_verts)).export(case/'constant/triSurface/cap.stl')
if kind=='stand':shutil.copy(here.parent/'output/veil_v15_prototype.stl',case/'constant/triSurface/stand.stl')
A=sum((s['x'][1]-s['x'][0])*(s['y'][1]-s['y'][0]) for s in slots)*1e-6;nx,ny,nz=[int(round(v/h)) for v in (X1-X0,Y1-Y0,Z1)]
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
geo='    cap.stl { type triSurfaceMesh; name cap; scale 0.001; }\n'+f'    recess {{ type searchableBox; min ({-.045} {-.115} {(H-1.5)*1e-3}); max ({.040} {.115} {(H+STEP+1)*1e-3}); }}\n'+('    stand.stl { type triSurfaceMesh; name stand; scale 0.001; }\n' if kind=='stand' else '')
ref='        cap { level (2 2); patchInfo { type wall; } }\n'+(f'        stand {{ level ({lvl} {lvl}); patchInfo {{ type wall; }} }}\n' if kind=='stand' else '')
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
    refinementRegions {{ recess {{ mode inside; levels ((1E15 2)); }} }}
    locationInMesh (-0.08013 -0.13031 0.00107);
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
(case/'case.json').write_text(json.dumps({'kind':kind,'cover_bottom_height_mm':H,'black_base_recess_mm':STEP,'vent_slots':len(slots),'flow_m3_per_min':Q*60,'flow_m3_per_s':Q,'base_cell_mm':h,'stand_refinement_level':lvl if kind=='stand' else None,'vent_slot_area_m2':A,'mean_outlet_speed_m_per_s':Q/A,'nu_m2_per_s':1.516e-5,'rho_kg_per_m3':1.204,'turbulence':'kOmegaSST, inlet k 3.75e-3 m2/s2 and omega 22 1/s (assumed)'},indent=2))
print(case,kind,'Q',Q,'m3/s  outlet speed',Q/A)
