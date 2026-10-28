"""Author the seed poses in explicit world-space coordinates (metres)."""
import copy,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1]
neutral=dict(root=[0,0,1],torso_euler=[0,0,0],head_euler=[0,0,0],wrists={'L':[-.30,-.03,.9],'R':[.30,-.03,.9]},elbows={'L':[-1,0,1.2],'R':[1,0,1.2]},ankles={'L':[-.13,0,.1],'R':[.13,0,.1]},knees={'L':[-.2,-1,.5],'R':[.2,-1,.5]},foot_yaw={'L':-5,'R':5},support='none')
poses=[]
def add(id,name,category,tags,**kw):
    p=copy.deepcopy(neutral);p.update(kw);p.update(id=id,name=name,category=category,tags=tags);poses.append(p)
add('stand-neutral','De pie · neutral','standing',['equilibrio','frente','relajado'])
add('stand-contrapposto','Contrapposto','standing',['peso','asimetría'],root=[.08,0,.98],torso_euler=[0,-8,-8],ankles={'L':[-.2,-.08,.1],'R':[.18,.04,.1]},wrists={'L':[-.25,-.06,.86],'R':[.36,.02,.96]})
add('stand-hands-hips','Manos en la cintura','standing',['cintura','confianza'],wrists={'L':[-.22,-.13,1.05],'R':[.22,-.13,1.05]},elbows={'L':[-1,-.1,1.4],'R':[1,-.1,1.4]})
add('stand-arms-crossed','Brazos cruzados','standing',['brazos','cruzados'],wrists={'L':[.16,-.21,1.30],'R':[-.16,-.15,1.35]},elbows={'L':[-.4,-.1,1.05],'R':[.4,-.1,1.10]})
add('stand-wave','Saludo con una mano','standing',['saludo','gesto'],wrists={'L':[-.3,-.03,.9],'R':[.4,-.03,1.78]},elbows={'L':[-1,0,1.2],'R':[1,.1,1.4]},head_euler=[0,0,-10])
add('stand-reach','Alcanzar arriba','standing',['alcanzar','estirar'],torso_euler=[0,8,0],wrists={'L':[-.29,-.03,1.0],'R':[.32,-.06,1.95]},elbows={'L':[-1,0,1.2],'R':[1,0,1.7]},head_euler=[-12,0,0])
add('stand-t-pose','Brazos en cruz','standing',['simetría','rig'],wrists={'L':[-.76,0,1.42],'R':[.76,0,1.42]})
add('stand-thinking','Pensando','standing',['pensar','mano','rostro'],wrists={'L':[.1,-.2,1.24],'R':[.03,-.15,1.62]},elbows={'L':[-.6,0,1.1],'R':[.6,-.1,1.1]},head_euler=[12,0,-8])
add('upper-shrug','Encogerse de hombros','upper-body',['gesto','duda'],wrists={'L':[-.49,-.17,1.43],'R':[.49,-.17,1.43]},elbows={'L':[-.6,0,1.05],'R':[.6,0,1.05]})
add('upper-point','Señalar al frente','upper-body',['señalar','dirección'],wrists={'L':[-.28,0,.9],'R':[.27,-.54,1.45]},elbows={'L':[-1,0,1.2],'R':[.6,-.4,1.4]})
add('upper-hands-head','Manos detrás de la cabeza','upper-body',['cabeza','abierto'],wrists={'L':[-.06,.07,1.68],'R':[.06,.07,1.68]},elbows={'L':[-1,0,1.6],'R':[1,0,1.6]})
add('upper-prayer','Palmas juntas','upper-body',['manos','centrado'],wrists={'L':[-.045,-.21,1.39],'R':[.045,-.21,1.39]},elbows={'L':[-1,0,1.15],'R':[1,0,1.15]})
add('sit-upright','Sentado · erguido','seated',['silla','relajado'],root=[0,0,.58],wrists={'L':[-.16,-.28,.64],'R':[.16,-.28,.64]},ankles={'L':[-.16,-.45,.10],'R':[.16,-.45,.1]},support='stool')
add('sit-lean','Sentado · inclinado','seated',['silla','apoyo'],root=[0,0,.58],torso_euler=[24,0,0],wrists={'L':[-.13,-.51,.53],'R':[.13,-.51,.53]},ankles={'L':[-.22,-.45,.10],'R':[.22,-.45,.1]},support='stool')
add('sit-cross-ankles','Sentado · tobillos cruzados','seated',['silla','cruzado'],root=[0,0,.58],wrists={'L':[-.12,-.24,.63],'R':[.12,-.24,.63]},ankles={'L':[.07,-.48,.1],'R':[-.07,-.39,.1]},knees={'L':[-.4,-1,.6],'R':[.4,-1,.6]},support='stool')
add('sit-turn','Sentado · giro','seated',['silla','giro'],root=[0,0,.58],torso_euler=[0,0,25],head_euler=[0,0,20],wrists={'L':[-.22,-.30,.62],'R':[.27,.06,.56]},ankles={'L':[-.16,-.45,.1],'R':[.16,-.45,.1]},support='stool')
add('action-walk','Caminar · paso abierto','action',['caminar','paso'],root=[0,0,.94],torso_euler=[5,0,-7],wrists={'L':[-.26,-.28,1.0],'R':[.28,.23,1.0]},ankles={'L':[-.13,-.32,.1],'R':[.13,.32,.1]},knees={'L':[-.2,-1,.5],'R':[.2,-1,.5]})
add('action-run','Correr · impulso','action',['correr','impulso'],root=[0,0,.95],torso_euler=[18,0,8],wrists={'L':[-.26,-.41,1.33],'R':[.3,.13,1.1]},elbows={'L':[-.6,-.05,1.1],'R':[.6,.4,1.3]},ankles={'L':[-.12,-.35,.14],'R':[.13,.39,.38]},knees={'L':[-.2,-1,.8],'R':[.2,-1,.4]})
add('action-box-guard','Boxeo · guardia','action',['boxeo','guardia'],root=[0,0,.91],torso_euler=[8,0,-15],wrists={'L':[-.12,-.37,1.53],'R':[.17,-.24,1.52]},elbows={'L':[-.5,-.1,1.0],'R':[.5,0,1.0]},ankles={'L':[-.23,-.25,.1],'R':[.23,.25,.1]})
add('action-punch','Boxeo · golpe recto','action',['boxeo','golpe'],root=[0,0,.91],torso_euler=[8,0,-18],wrists={'L':[-.17,-.52,1.34],'R':[.17,-.24,1.50]},elbows={'L':[-.5,-.4,1.2],'R':[.5,0,1.0]},ankles={'L':[-.23,-.25,.1],'R':[.23,.25,.1]})
add('action-lunge','Zancada profunda','action',['piernas','zancada'],root=[0,0,.71],torso_euler=[6,0,0],wrists={'L':[-.34,-.30,.73],'R':[.34,.15,.76]},ankles={'L':[-.17,-.56,.10],'R':[.17,.53,.1]},knees={'L':[-.2,-1,.6],'R':[.2,-1,.3]})
add('action-squat','Sentadilla','action',['piernas','sentadilla'],root=[0,0,.62],torso_euler=[22,0,0],wrists={'L':[-.18,-.62,1.1],'R':[.18,-.62,1.1]},ankles={'L':[-.29,-.10,.1],'R':[.29,-.10,.1]},knees={'L':[-.65,-1,.6],'R':[.65,-1,.6]},foot_yaw={'L':-20,'R':20})
add('action-balance','Equilibrio en una pierna','action',['equilibrio','pierna'],root=[0,0,.99],torso_euler=[0,0,0],wrists={'L':[-.70,-.08,1.4],'R':[.7,-.08,1.4]},ankles={'L':[-.12,0,.1],'R':[.11,-.40,.59]},knees={'L':[-.2,-1,.5],'R':[.6,-1,1.0]})
add('action-celebrate','Celebración','action',['alegría','brazos'],root=[0,0,.99],wrists={'L':[-.48,-.06,1.87],'R':[.48,-.06,1.87]},elbows={'L':[-1,0,1.7],'R':[1,0,1.7]},ankles={'L':[-.22,0,.1],'R':[.22,0,.1]})
for pose in poses:
    if pose['id']=='action-run':
        pose['foot_euler']={'L':[-8,0,-5],'R':[55,0,5]}
    if pose['id'] in ('action-box-guard','action-punch'):
        pose['hand_pose']={'L':'fist','R':'fist'}
    if pose['id']=='upper-point':pose['hand_pose']={'L':'relaxed','R':'point'}
    if pose['id']=='stand-wave':pose['hand_pose']={'L':'relaxed','R':'open'}
(BASE/'poses/catalog.json').write_text(json.dumps({'title':'Oruga Pose Studio','version':'1.0','license':'CC0-1.0','poses':poses},ensure_ascii=False,indent=2))
print(len(poses),'poses written')
