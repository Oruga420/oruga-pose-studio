#!/usr/bin/env python3
"""Original procedural mannequin and reproducible Blender pose renderer.
Run: blender -b --python scripts/render.py -- --catalog poses/catalog.json
No downloaded geometry, image, rig, textures or source assets are used.
"""
import argparse, json, math, sys
from pathlib import Path
import bpy
from mathutils import Vector, Euler

BASE = Path(__file__).resolve().parents[1]
ANGLES = {
    'front': (0, 8, 'Frente'),
    'three-quarter': (45, 8, 'Tres cuartos'),
    'side': (90, 8, 'Perfil'),
    'back': (180, 8, 'Espalda'),
    'high': (35, 38, 'Picado'),
}
BODY = None
JOINT = None
ACCENT = None
GUIDE = None

def material(name, color, roughness=.65):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    return m

def finish(obj, mat= None):
    obj.data.materials.append(mat or BODY)
    for p in obj.data.polygons: p.use_smooth = True
    return obj

def ellipsoid(name, center, scale, mat=None, quat=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=16, location=center)
    o=bpy.context.object; o.name=name; o.scale=scale
    if quat is not None: o.rotation_mode='QUATERNION'; o.rotation_quaternion=quat
    return finish(o,mat)

def shape(name, rings, origin, rotation=None, mat=None, segments=32):
    """Original elliptical ring loft, z longitudinal axis. rings=(z,rx,ry,cy)."""
    verts=[]; faces=[]
    for z,rx,ry,cy in rings:
        for j in range(segments):
            t=2*math.pi*j/segments
            p=Vector((rx*math.cos(t),cy+ry*math.sin(t),z))
            if rotation is not None: p=rotation @ p
            verts.append(tuple(p+Vector(origin)))
    for i in range(len(rings)-1):
        for j in range(segments):
            a=i*segments+j;b=i*segments+(j+1)%segments
            faces.append((a,b,b+segments,a+segments))
    faces.append(tuple(reversed(range(segments))))
    faces.append(tuple((len(rings)-1)*segments+j for j in range(segments)))
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],faces);mesh.update()
    obj=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(obj)
    finish(obj,mat)
    sub=obj.modifiers.new('Soft silhouette','SUBSURF');sub.levels=1;sub.render_levels=1
    return obj

def line(name,points,closed=False,radius=.0018):
    curve=bpy.data.curves.new(name,'CURVE');curve.dimensions='3D';curve.resolution_u=2;curve.bevel_depth=radius;curve.bevel_resolution=2
    spline=curve.splines.new('POLY');spline.points.add(len(points)-1)
    for p,co in zip(spline.points,points):p.co=(*co,1)
    spline.use_cyclic_u=closed
    ob=bpy.data.objects.new(name,curve);bpy.context.collection.objects.link(ob);ob.data.materials.append(GUIDE)
    return ob

def surface_guide(name,obj,points,centers,closed=False,radius=.0017):
    """Ray-project construction marks onto the evaluated smooth surface."""
    if not closed and len(points)<32:
        dense=[];dense_centers=[]
        for i in range(len(points)-1):
            for j in range(12):
                t=j/12;dense.append(Vector(points[i]).lerp(Vector(points[i+1]),t));dense_centers.append(Vector(centers[i]).lerp(Vector(centers[i+1]),t))
        dense.append(points[-1]);dense_centers.append(centers[-1]);points,centers=dense,dense_centers
    bpy.context.view_layer.update();evaluated=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    result=[]
    for point,center in zip(points,centers):
        direction=(Vector(point)-Vector(center)).normalized()
        hit,position,normal,_=evaluated.ray_cast(Vector(center),direction)
        result.append(position+normal*.0011 if hit else Vector(point))
    return line(name,result,closed,radius)

def ellipse_guide(name,center,rx,ry,rotation=None,obj=None):
    points=[]
    for i in range(64):
        t=i*math.tau/64;p=Vector((rx*math.cos(t),ry*math.sin(t),0))
        if rotation is not None:p=rotation@p
        points.append(Vector(center)+p)
    return surface_guide(name,obj,points,[center]*len(points),True) if obj else line(name,points,True)

def limb(name,a,b,kind):
    a,b=Vector(a),Vector(b);d=b-a;q=d.to_track_quat('Z','Y'); length=d.length
    profiles={
      'upper-arm':[(0,.040,.040),(.12,.052,.050),(.32,.054,.049),(.55,.046,.043),(.82,.034,.033),(1,.030,.030)],
      'forearm':[(0,.030,.030),(.18,.039,.036),(.4,.037,.033),(.72,.027,.025),(1,.022,.022)],
      'thigh':[(0,.070,.073),(.16,.086,.084),(.4,.077,.075),(.7,.057,.059),(1,.039,.040)],
      'shin':[(0,.038,.039),(.21,.054,.054),(.43,.051,.051),(.73,.033,.031),(1,.025,.026)],
    }
    rings=[(-.004,.001,.001,0)]+[(t*length,rx,ry,0) for t,rx,ry in profiles[kind]]+[(length+.004,.001,.001,0)]
    obj=shape(name,rings,a,q)
    if kind in ('upper-arm','thigh'):
        t,rx,ry=profiles[kind][2];ellipse_guide(name+' construction ring',a+(b-a)*t,rx+.0015,ry+.0015,q.to_matrix(),obj)
    return obj

def ik(origin,goal,pole,a,b):
    """Two-bone analytic IK. Unreachable targets clamp without stretching bones."""
    origin,goal,pole=map(Vector,(origin,goal,pole));v=goal-origin
    raw=v.length;d=max(abs(a-b)+.0001,min(raw,a+b-.0001))
    direction=v.normalized() if raw>1e-7 else Vector((0,0,-1))
    end=origin+direction*d
    along=(a*a-b*b+d*d)/(2*d)
    offset=max(0,a*a-along*along)**.5
    bend=pole-origin; bend-=direction*bend.dot(direction)
    if bend.length<1e-6: bend=direction.cross(Vector((0,1,0)))
    bend.normalize()
    return origin+direction*along+bend*offset,end,abs(raw-d)

def hand(name,wrist,elbow,side,orientation=None,gesture='relaxed'):
    # Finger axis follows forearm, palm is a broad volume rather than a sphere.
    direction=Vector(orientation).normalized() if orientation else (Vector(wrist)-Vector(elbow)).normalized()
    q=direction.to_track_quat('Z','Y'); r=q.to_matrix(); wrist=Vector(wrist)
    ellipsoid(name+' palm',wrist+r@Vector((0,0,.047)),(.036,.019,.055),quat=q)
    for i,(x,length) in enumerate([(-.024,.044),(-.008,.052),(.008,.049),(.023,.039)]):
        extended=gesture not in ('fist','thumb_up') and (gesture!='point' or i==(0 if side==1 else 3))
        if extended:
            curl=.012 if gesture=='relaxed' else 0
            ellipsoid(name+f' finger {i+1}',wrist+r@Vector((x,-.003-curl,.090+length/2)),(.008,.009,length/2+.008),quat=q)
        else:
            ellipsoid(name+f' curled finger {i+1}',wrist+r@Vector((x,-.022,.089)),(.009,.020,.018),quat=q)
    if gesture=='thumb_up':
        thumbdir=(r@Vector((-side*.95,-.05,.3))).normalized();position=(-side*.048,-.004,.046)
    elif gesture=='fist':
        thumbdir=(r@Vector((-side*.3,-.4,.8))).normalized();position=(-side*.027,-.030,.065)
    else:
        thumbdir=(r@Vector((-side*.7,-.12,.7))).normalized();position=(-side*.039,-.004,.043)
    tq=thumbdir.to_track_quat('Z','Y')
    ellipsoid(name+' thumb',wrist+r@Vector(position),(.011,.011,.030),quat=tq)

def foot(name,ankle,yaw):
    r=Euler(tuple(math.radians(v) for v in yaw) if isinstance(yaw,(list,tuple)) else (0,0,math.radians(yaw))).to_matrix(); ankle=Vector(ankle)
    # Single original rounded foot loft: local z follows heel to toe, local y is height.
    footrot=r@Euler((math.pi/2,0,0)).to_matrix()
    rings=[(-.067,.008,.008,-.035),(-.048,.040,.042,-.035),(.010,.046,.055,-.028),(.065,.052,.045,-.040),(.125,.058,.030,-.052),(.166,.044,.024,-.055),(.184,.012,.011,-.055)]
    shape(name+' foot',[(z*.88,rx*.86,ry*.9,cy) for z,rx,ry,cy in rings],ankle,footrot)

def stool(root):
    h=max(.12,root[2]-.16)
    bpy.ops.mesh.primitive_cylinder_add(vertices=48,radius=.25,depth=.045,location=(root[0],root[1],h-.023))
    o=bpy.context.object;o.name='Support seat';finish(o,ACCENT)
    for x in [-.17,.17]:
        for y in [-.13,.13]:
            bpy.ops.mesh.primitive_cylinder_add(vertices=12,radius=.018,depth=h-.05,location=(root[0]+x,root[1]+y,(h-.05)/2))
            finish(bpy.context.object,ACCENT)

def mannequin(pose):
    root=Vector(pose.get('root',[0,0,1]));r=Euler(tuple(math.radians(v) for v in pose.get('torso_euler',[0,0,0]))).to_matrix()
    warnings=[];joints={}
    pr=Euler(tuple(math.radians(v) for v in pose.get('pelvis_euler',[0,0,0]))).to_matrix()
    # One continuous torso: pelvis, lumbar waist, rib cage and clavicle slope.
    # Ring rotations smoothly interpolate between pelvis and thorax for bending.
    rings=[(-.16,.050,.054,0),(-.13,.122,.091,.006),(-.075,.178,.112,.009),(-.005,.177,.107,.008),(.07,.133,.086,.003),(.14,.112,.076,0),(.21,.129,.085,0),(.29,.153,.099,-.004),(.36,.164,.094,0),(.415,.171,.078,.005),(.45,.111,.062,.006),(.465,.048,.044,.004)]
    torso=shape('Continuous anatomical torso',rings,(0,0,0))
    for v in torso.data.vertices:
        local=v.co.copy(); weight=max(0,min(1,(local.z+.025)/.19))
        rotation=pr.to_quaternion().slerp(r.to_quaternion(),weight)
        v.co=root+rotation@local
    def surface_point(z,rx,ry,cy,t):
        weight=max(0,min(1,(z+.025)/.19));rotation=pr.to_quaternion().slerp(r.to_quaternion(),weight)
        return root+rotation@Vector((rx*math.cos(t),cy+ry*math.sin(t),z))
    # Center line and transverse masses make tilt and foreshortening readable.
    surface_guide('Torso center guide',torso,[surface_point(z,rx,ry+.002,cy,-math.pi/2) for z,rx,ry,cy in rings[1:-1]],[surface_point(z,0,0,cy,0) for z,rx,ry,cy in rings[1:-1]],radius=.002)
    for idx in [2,5,7,9]:
        z,rx,ry,cy=rings[idx]
        surface_guide('Torso transverse guide '+str(idx),torso,[surface_point(z,rx+.002,ry+.002,cy,i*math.tau/64) for i in range(64)],[surface_point(z,0,0,cy,0)]*64,True)
    neck=root+r@Vector((0,0,.487))
    ellipsoid('Neck',neck,(.042,.043,.059),quat=r.to_quaternion())
    hr=r@Euler(tuple(math.radians(v) for v in pose.get('head_euler',[0,0,0]))).to_matrix()
    headroot=root+r@Vector((0,0,.525))
    headrings=[(0,.058,.062,0),(.035,.082,.077,-.005),(.085,.102,.086,0),(.16,.106,.091,.007),(.225,.085,.079,.014),(.265,.035,.033,.014),(.27,.005,.005,.014)]
    head=shape('Head',[(z*.9,rx*.93,ry*.95,cy) for z,rx,ry,cy in headrings],headroot,hr)
    surface_guide('Head center guide',head,[headroot+hr@Vector((0,cy-ry*.95-.002,z*.9)) for z,rx,ry,cy in headrings[1:-1]],[headroot+hr@Vector((0,cy,z*.9)) for z,rx,ry,cy in headrings[1:-1]],radius=.0018)
    ellipse_guide('Head eye-line guide',headroot+hr@Vector((0,.003,.118)),.096,.086,hr,head)

    for s,sgn in [('L',-1),('R',1)]:
        shoulder=root+r@Vector((sgn*.198,0,.415));hip=root+pr@Vector((sgn*.115,0,-.04))
        wrist=pose.get('wrists',{}).get(s,[sgn*.30,-.025,root.z-.12])
        ep=pose.get('elbows',{}).get(s,[sgn*1,0,root.z+.2])
        ankle=pose.get('ankles',{}).get(s,[sgn*.13,0,.1])
        kp=pose.get('knees',{}).get(s,[sgn*.2,-1,.5])
        elbow,wrist,armclamp=ik(shoulder,wrist,ep,.29,.26)
        knee,ankle,legclamp=ik(hip,ankle,kp,.45,.43)
        if armclamp>.005: warnings.append(f'{s} wrist clamped {armclamp:.3f}m')
        if legclamp>.005: warnings.append(f'{s} ankle clamped {legclamp:.3f}m')
        ellipsoid(s+' shoulder joint',shoulder,(.047,.047,.047),JOINT)
        ellipsoid(s+' elbow joint',elbow,(.030,.030,.030),JOINT)
        ellipsoid(s+' wrist joint',wrist,(.023,.023,.023),JOINT)
        ellipsoid(s+' hip joint',hip,(.052,.052,.052),JOINT)
        ellipsoid(s+' knee joint',knee,(.039,.039,.039),JOINT)
        ellipsoid(s+' ankle joint',ankle,(.025,.025,.025),JOINT)
        limb(s+' upper arm',shoulder,elbow,'upper-arm');limb(s+' forearm',elbow,wrist,'forearm')
        limb(s+' thigh',hip,knee,'thigh');limb(s+' calf',knee,ankle,'shin')
        hand(s,wrist,elbow,sgn,pose.get('hand_directions',{}).get(s,[0,-1,0] if pose.get('support')=='stool' else None),pose.get('hand_pose',{}).get(s,'relaxed'));foot(s,ankle,pose.get('foot_euler',{}).get(s,pose.get('foot_yaw',{}).get(s,sgn*-5)))
        joints[s]={k:list(v) for k,v in {'shoulder':shoulder,'elbow':elbow,'wrist':wrist,'hip':hip,'knee':knee,'ankle':ankle}.items()}
    if pose.get('support')=='stool':stool(root)
    return joints,warnings

def area(name,loc,power,size,target):
    data=bpy.data.lights.new(name,'AREA');data.energy=power;data.shape='DISK';data.size=size
    obj=bpy.data.objects.new(name,data);bpy.context.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()

def scene_setup(args):
    global BODY,JOINT,ACCENT,GUIDE
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    BODY=material('Military olive matte',(.22,.29,.135));JOINT=material('Olive articulation',(.11,.16,.075));ACCENT=material('Support',(.28,.32,.25));GUIDE=material('Construction guides',(.62,.72,.36))
    sc=bpy.context.scene;sc.render.engine=args.engine;sc.cycles.samples=args.samples;sc.cycles.use_denoising=False
    if args.engine=='BLENDER_WORKBENCH':
        sh=sc.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.45;sh.studio_light='studio.sl';sh.color_type='MATERIAL';sh.show_shadows=False;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=.6;sh.curvature_valley_factor=.7;sh.show_specular_highlight=False;sh.background_type='VIEWPORT';sh.background_color=(.88,.89,.87);sc.world.color=(.82,.83,.81);sc.display.render_aa='32'
    sc.render.resolution_x=args.width;sc.render.resolution_y=args.height;sc.render.resolution_percentage=100
    sc.render.dither_intensity=0
    sc.render.image_settings.file_format='PNG';sc.render.image_settings.color_mode='RGB';sc.render.film_transparent=False
    sc.render.threads_mode='FIXED';sc.render.threads=args.threads
    sc.world.use_nodes=True;sc.world.node_tree.nodes['Background'].inputs[0].default_value=(.72,.77,.75,1);sc.world.node_tree.nodes['Background'].inputs[1].default_value=.4
    sc.view_settings.view_transform='AgX';sc.view_settings.look='AgX - Medium High Contrast'
    ground=material('Backdrop',(.84,.86,.82));bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.005));o=bpy.context.object;o.name='Ground';finish(o,ground)
    if args.engine=='BLENDER_WORKBENCH':o.hide_render=True
    area('Key',(-3,-4,6),450,4,(0,0,1));area('Fill',(4,-2,3),200,3,(0,0,1));area('Rim',(1,4,5),500,3,(0,0,1))
    bpy.ops.object.camera_add();sc.camera=bpy.context.object;sc.camera.name='Camera';sc.camera.data.type='ORTHO';sc.camera.data.lens=50
    return sc

def frame(sc,angle):
    points=[]
    for ob in sc.objects:
        if ob.type=='MESH' and ob.name!='Ground':
            points.extend(ob.matrix_world@Vector(corner) for corner in ob.bound_box)
    low=Vector([min(v[i] for v in points) for i in range(3)]);high=Vector([max(v[i] for v in points) for i in range(3)])
    target=(low+high)/2
    az,el,_=ANGLES[angle];a=math.radians(az);e=math.radians(el)
    direction=Vector((math.sin(a)*math.cos(e),-math.cos(a)*math.cos(e),math.sin(e)))
    cam=sc.camera;cam.location=target+direction*6;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
    # Project all geometry to camera axes for crop-safe orthographic fit.
    rot=cam.rotation_euler.to_matrix().transposed();screen=[rot@(p-target) for p in points]
    w=max(v.x for v in screen)-min(v.x for v in screen);h=max(v.y for v in screen)-min(v.y for v in screen)
    cam.data.ortho_scale=max(h,w*sc.render.resolution_y/sc.render.resolution_x)*1.16
    cam.data.clip_end=200

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--catalog',default=str(BASE/'poses/catalog.json'));ap.add_argument('--output',default=str(BASE/'assets'));ap.add_argument('--ids',default='');ap.add_argument('--angles',default=','.join(ANGLES));ap.add_argument('--width',type=int,default=640);ap.add_argument('--height',type=int,default=800);ap.add_argument('--samples',type=int,default=24);ap.add_argument('--threads',type=int,default=8);ap.add_argument('--save-blend',action='store_true');ap.add_argument('--engine',default='BLENDER_WORKBENCH',choices=['CYCLES','BLENDER_WORKBENCH','BLENDER_EEVEE_NEXT'])
    args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
    catalog=json.loads(Path(args.catalog).read_text());poses=catalog['poses'] if isinstance(catalog,dict) else catalog
    ids=set(filter(None,args.ids.split(',')));angles=args.angles.split(',');out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    report=[]
    for pose in poses:
        if ids and pose['id'] not in ids:continue
        sc=scene_setup(args);joints,warnings=mannequin(pose);bpy.context.view_layer.update()
        folder=out/pose['id'];folder.mkdir(exist_ok=True)
        for angle in angles:
            frame(sc,angle);sc.render.filepath=str(folder/f'{angle}.png');bpy.ops.render.render(write_still=True)
        metadata={**pose,'joints':joints,'warnings':warnings,'angles':{a:{'azimuth':ANGLES[a][0],'elevation':ANGLES[a][1],'label':ANGLES[a][2],'image':f'assets/{pose["id"]}/{a}.png'} for a in angles},'license':'CC0-1.0','generator':'Oruga Pose Studio 1.0'}
        (folder/'metadata.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
        if args.save_blend:bpy.ops.wm.save_as_mainfile(filepath=str(folder/'scene.blend'))
        report.append({'id':pose['id'],'warnings':warnings});print('POSE_DONE '+pose['id'],flush=True)
        # Clear orphan datablocks to keep long batch runs bounded.
        bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
        for collection in [bpy.data.meshes,bpy.data.curves,bpy.data.materials,bpy.data.lights,bpy.data.cameras]:
            for item in list(collection):
                if item.users==0:collection.remove(item)
    (out/'render-report.json').write_text(json.dumps(report,indent=2))
if __name__=='__main__':main()
