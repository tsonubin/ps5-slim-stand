"""Weld only nonmanifold sliver edges shorter than 1e-5 mm.
No boundary-loop filling, remeshing, or change to intentional openings.
"""
import numpy as np

def bounded_sliver_weld(mesh,limit=1e-5):
    before_volume=float(mesh.volume);before_faces=len(mesh.faces)
    edges,counts=np.unique(mesh.edges_sorted,axis=0,return_counts=True)
    bad=edges[counts!=2]
    lengths=np.linalg.norm(mesh.vertices[bad[:,0]]-mesh.vertices[bad[:,1]],axis=1)
    short=bad[lengths<limit]
    assert len(short)>0,'No bounded sliver correction available'
    parent=np.arange(len(mesh.vertices));moves=[]
    for a,b in short:
        while parent[a]!=a:a=parent[a]
        while parent[b]!=b:b=parent[b]
        if a==b:continue
        d=float(np.linalg.norm(mesh.vertices[a]-mesh.vertices[b]));assert d<limit
        moves.append({'from_vertex_mm':mesh.vertices[b].tolist(),'to_vertex_mm':mesh.vertices[a].tolist(),'distance_mm':d})
        parent[b]=a
    while np.any(parent[parent]!=parent):parent=parent[parent]
    mesh.faces=parent[mesh.faces]
    valid=~np.any(np.diff(np.sort(mesh.faces,axis=1),axis=1)==0,axis=1)
    mesh.update_faces(valid);mesh.update_faces(mesh.unique_faces());mesh.remove_unreferenced_vertices()
    assert mesh.is_watertight and mesh.is_winding_consistent,'Bounded weld did not resolve closure'
    delta=float(mesh.volume-before_volume);assert abs(delta)<.001,'Unexpected repair volume change'
    return mesh,{'method':'Only short nonmanifold edges welded; collapsed-index and duplicate faces removed; no holes filled','threshold_mm':limit,'max_vertex_movement_mm':max(x['distance_mm'] for x in moves),'weld_pairs':len(moves),'removed_faces':before_faces-len(mesh.faces),'volume_delta_mm3':delta,'moves':moves}
