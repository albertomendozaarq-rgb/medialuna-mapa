import math, json, struct, base64, io, random
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT=Path(__file__).resolve().parents[1]/'outputs'
rng=random.Random(31)
V=[]; N=[]; C=[]; groups={}; current='estructura'
colors={'wood':(0.49,.30,.14),'light':(.69,.49,.27),'dark':(.22,.14,.08),'roof':(.76,.65,.46),'tile':(.62,.25,.10),'stone':(.48,.45,.36),'adobe':(.52,.25,.17),'cream':(.77,.69,.51),'glass':(.12,.20,.19),'iron':(.15,.17,.16),'leaf':(.28,.36,.12),'gold':(1,.72,.28)}
def tri(a,b,c,col):
    a,b,c=map(lambda p:np.array(p,dtype=float),(a,b,c)); n=np.cross(b-a,c-a); l=np.linalg.norm(n)
    if l<1e-9:return
    n/=l
    V.extend([a.tolist(),b.tolist(),c.tolist()]);N.extend([n.tolist()]*3);C.extend([col]*3)
    groups[current]=groups.get(current,0)+1
def quad(a,b,c,d,col):tri(a,b,c,col);tri(a,c,d,col)
def roofquad(a,b,c,d,col):
    if np.cross(np.array(b)-a,np.array(c)-a)[1]<0:quad(d,c,b,a,col)
    else:quad(a,b,c,d,col)
def rooftri(a,b,c,col):
    if np.cross(np.array(b)-a,np.array(c)-a)[1]<0:tri(c,b,a,col)
    else:tri(a,b,c,col)
def tint(key,delta=.06):
    c=colors.get(key,key); k=rng.uniform(-delta,delta);return tuple(max(0,min(1,x+k)) for x in c)
def box(x,y,z,w,h,d,key='wood'):
    col=colors.get(key,key); p=[(x+a*w/2,y+b*h/2,z+c*d/2) for a,b,c in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]]
    for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:quad(*(p[i] for i in ids),col)
def beam(a,b,r=.10,key='dark',sides=6,r2=None):
    a=np.array(a,float);b=np.array(b,float); v=b-a;v/=np.linalg.norm(v)
    t=np.array([0,1,0]) if abs(v[1])<.95 else np.array([1,0,0]);u=np.cross(v,t);u/=np.linalg.norm(u);w=np.cross(v,u)
    r2=r if r2 is None else r2; col=colors.get(key,key)
    aa=[a+r*(math.cos(i*2*math.pi/sides)*u+math.sin(i*2*math.pi/sides)*w) for i in range(sides)]
    bb=[b+r2*(math.cos(i*2*math.pi/sides)*u+math.sin(i*2*math.pi/sides)*w) for i in range(sides)]
    for i in range(sides):
        j=(i+1)%sides;quad(aa[i],aa[j],bb[j],bb[i],col);tri(a,aa[j],aa[i],col);tri(b,bb[i],bb[j],col)
def wall(x,z,w,d,y,h,key):
    box(x,y+h/2,z,w,h,d,key)
    if key=='wood':
        for yy in np.arange(y+.15,y+h,.28):
            box(x,yy,z+d/2+.018,w,.25,.045,tint('light'))
            box(x+w/2+.018,yy,z,.045,.25,d,tint('light'))
            box(x-w/2-.018,yy,z,.045,.25,d,tint('wood'))
            box(x,yy,z-d/2-.018,w,.25,.045,tint('wood'))
def masonry(x,z,w,d,y,h):
    box(x,y+h/2,z,w,h,d,'dark')
    for row,yy in enumerate(np.arange(y+.19,y+h,.4)):
        for xx in np.arange(x-w/2+.25,x+w/2,.65):
            xx=min(xx+(row%2)*.16,x+w/2-.12)
            for zz in [z-d/2-.01,z+d/2+.01]:box(xx,yy,zz,.57,.33,.12,tint('stone',.1))
        for zz in np.arange(z-d/2+.25,z+d/2,.65):
            for xx in [x-w/2-.01,x+w/2+.01]:box(xx,yy,zz,.12,.33,.57,tint('stone',.1))
def roof(x,z,w,d,y,rise,key='roof',hip=False):
    xl=x-w/2;xr=x+w/2;zf=z+d/2;zb=z-d/2
    if hip:
        p=[(xl,y,zb),(xr,y,zb),(xr,y,zf),(xl,y,zf)]; r0=(x,y+rise,zb+d*.28);r1=(x,y+rise,zf-d*.28)
        roofquad(p[0],r0,r1,p[3],colors[key]);roofquad(r0,p[1],p[2],r1,colors[key]);rooftri(p[0],p[1],r0,colors[key]);rooftri(p[3],r1,p[2],colors[key])
        for a,b in [(p[0],r0),(p[1],r0),(p[2],r1),(p[3],r1),(r0,r1)]:beam(a,b,.055,'cream')
    else:
        for s in [-1,1]:
            a=(x,y+rise,zb);b=(x+s*w/2,y,zb);c=(x+s*w/2,y,zf);dd=(x,y+rise,zf)
            roofquad(a,b,c,dd,colors[key])
        for zz in [zb,zf]:
            tri((xl,y,zz),(xr,y,zz),(x,y+rise,zz),colors['wood'])
            beam((xl,y,zz),(x,y+rise,zz),.085,'dark');beam((xr,y,zz),(x,y+rise,zz),.085,'dark')
        # Roof seams / rounded individual terracotta tiles
        for xx in np.arange(xl+.10,xr,.30 if key=='tile' else .50):
            yy=y+rise*(1-abs(xx-x)/(w/2))+.05
            if key=='tile':
                for zz in np.arange(zb+.08,zf,.42):beam((xx,yy,zz),(xx,yy, min(zz+.39,zf)),.10,tint('tile',.075),6)
            else:beam((xx,yy,zb),(xx,yy,zf),.028,'cream',4)
    for a,b in [((xl,y,zb),(xr,y,zb)),((xr,y,zb),(xr,y,zf)),((xr,y,zf),(xl,y,zf)),((xl,y,zf),(xl,y,zb))]:beam(a,b,.085,'dark',4)
def window(x,y,z,w=1.2,h=1.4):
    box(x,y,z,w,h,.075,'glass')
    for xx in [x-w/2,x,x+w/2]:box(xx,y,z+.06,.075,h+.13,.10,'dark')
    for yy in [y-h/2,y+h/2]:box(x,yy,z+.06,w+.15,.09,.12,'light')
def door(x,y,z,w=1.35,h=2.4):
    box(x,y+h/2,z,w,h,.16,'dark')
    for xx in np.arange(x-w/2+.09,x+w/2,.18):box(xx,y+h/2,z+.10,.15,h-.1,.06,tint('wood'))
    for yy in [y+.16,y+h-.16]:box(x,yy,z+.15,w,.13,.08,'light')
    beam((x-w/2+.1,y+.2,z+.17),(x+w/2-.1,y+h-.2,z+.17),.06,'light',4)
    beam((x+w/2-.1,y+.2,z+.17),(x-w/2+.1,y+h-.2,z+.17),.06,'light',4)
def rail(a,b,y):
    a=np.array(a,float);b=np.array(b,float);num=max(1,int(np.linalg.norm(b-a)/1.65))
    for i in range(num+1):
        p=a+(b-a)*i/num;beam((p[0],y,p[1]),(p[0],y+1.1,p[1]),.075,'dark',4)
    for yy in [y+.18,y+1.05]:beam((a[0],yy,a[1]),(b[0],yy,b[1]),.07,'light',4)
    for i in range(num):
        p=a+(b-a)*i/num;q=a+(b-a)*(i+1)/num
        beam((p[0],y+.2,p[1]),(q[0],y+1,p[1] if a[1]==b[1] else q[1]),.037,'wood',4)
        beam((p[0],y+1,p[1]),(q[0],y+.2,q[1]),.037,'wood',4)
def plant(x,y,z,s=1):
    beam((x,y,z),(x,y+.38*s,z),.22*s,'tile',8,r2=.3*s)
    for i in range(7):
        t=i*2.4;beam((x,y+.32*s,z),(x+math.cos(t)*.4*s,y+(.65+rng.random()*.5)*s,z+math.sin(t)*.4*s),.075*s,tint('leaf'),5,r2=.008)
def table(x,y,z):
    box(x,y+.78,z,1.25,.12,.85,'wood')
    for xx in [-.47,.47]:
        for zz in [-.3,.3]:box(x+xx,y+.39,z+zz,.09,.78,.09,'dark')
    for zz in [-.8,.8]:
        box(x,y+.42,z+zz,1.35,.10,.30,'light')
        for xx in [-.45,.45]:box(x+xx,y+.21,z+zz,.09,.42,.22,'dark')

current='salon_alto'
masonry(-3,-7,6,6,0,1.15);wall(-3,-7,5.9,5.9,1.15,6,'wood');roof(-3,-7,7,7,7.15,4.3)
for xx in [-5,-3,-1]:window(xx,5.7,-3.99,1.4,2)
for xx in [-5.8,-3,-.2]:beam((xx,1.1,-3.95),(xx,7.1,-3.95),.13,'dark',4)
current='chimenea_piedra';masonry(-6.1,-6,1.7,2,0,7.5);box(-6.1,7.6,-6,1.95,.20,2.25,'cream')
current='restaurante_terraza'
masonry(2,-.6,10,8.3,0,1.15);wall(.2,-.8,6.3,7.8,1.15,3.2,'wood')
box(2,4.45,-.6,10.5,.25,8.8,'dark')
for zz in np.arange(-4.9,3.7,.26):box(2,4.61,zz,10.3,.08,.24,tint('light',.05))
wall(.1,-2,6.5,5.6,4.65,2.9,'wood')
roof(2,-.6,11.5,9.5,7.7,1.8,'roof',True)
# roof hip seams conform to hipped surface
for zz in np.arange(-5.25,4.1,.44):
    for side in [-1,1]:
        coords=[]
        for xx in np.linspace(2,2+side*5.75,16):
            ht=1.8*min(1,(5.75-abs(xx-2))/5.75,(4.75-abs(zz+.6))/(9.5*.28))
            coords.append((xx,7.75+max(0,ht),zz))
        for a,b in zip(coords,coords[1:]):beam(a,b,.018,'cream',4)
for zz in [-4.6,-1.9,.8,3.55]:
    beam((7,1.1,zz),(7,7.65,zz),.12,'dark',4)
    beam((7,6.6,zz),(7,7.6,zz-.75),.07,'wood',4)
for xx in [-3.1,0,3.4,7]:beam((xx,4.65,3.6),(xx,7.65,3.6),.11,'dark',4)
rail((7,-4.7),(7,3.6),4.65);rail((-3.2,3.6),(7,3.6),4.65)
for zz in [-3.2,-.6,2]:table(5.2,4.7,zz)
for xx in [-1.7,.7,3.1]:table(xx,4.7,2)
for xx in [-2,0,2]:window(xx,2.9,3.14,1.3,1.65)
door(4.8,1.15,3.64,1.6,2.8)
# Hanging bulbs on terrace
for i in range(22):
    zz=-4.5+i*8/21; yy=7.3-.32*math.sin(i/21*math.pi)
    if i:beam(prev,(7.12,yy,zz),.014,'iron',4)
    beam((7.12,yy,zz),(7.12,yy-.14,zz),.035,'gold',6,r2=.06);prev=(7.12,yy,zz)
current='porche_acceso'
masonry(-4.9,1.0,3.5,5.3,0,.5)
roof(-4.9,1,4.1,5.8,3.4,.95,'tile')
for zz in [-1.6,1.1,3.6]:beam((-6.65,.5,zz),(-6.65,3.4,zz),.11,'dark',4)
table(-4.8,.55,1)
current='casita_teja'
masonry(-2.5,6.3,4.8,4.8,0,.5);wall(-2.5,6.3,4.6,4.6,.5,2.6,'adobe');roof(-2.5,6.3,5.7,5.6,3.2,1.6,'tile')
door(-2.5,.5,8.64,1.25,2.3);window(-4,1.8,8.65,.9,1.3);window(-1,1.8,8.65,.9,1.3)
box(-2.5,.42,9,5,.18,1.15,'wood')
for i in range(3):box(-2.5,.1+i*.1,10-i*.3,2.6,.2,.65,'cream')
for xx in [-4.6,-.4]:beam((xx,.4,8.9),(xx,3.1,8.9),.09,'dark',4);plant(xx,.5,8.9,.8)
current='ala_adobe'
wall(4.2,7.2,6.9,6.8,0,2.6,'adobe');box(4.2,2.69,7.2,7.15,.18,7.05,'tile')
wall(5.3,12.0,5.5,3.1,0,2.8,'adobe');wall(1.55,11.1,2.0,3.4,0,2.6,'adobe')
for x,z,w,d,h in [(5.3,12,5.7,3.3,2.85),(1.55,11.1,2.2,3.6,2.65)]:
    box(x,h,z,w,.15,d,'cream')
    for xx in [x-w/2,x+w/2]:box(xx,h+.25,z,.16,.5,d,'cream')
    for zz in [z-d/2,z+d/2]:box(x,h+.25,zz,w,.5,.16,'cream')
for xx in [3.4,5.3,7.2]:window(xx,1.5,13.57,1.15,1.65)
door(1.55,0,12.83,1.1,2.2)
current='torre_de_agua'
for xx in [-.1,1.25]:
    for zz in [7.7,9.05]:beam((xx,0,zz),(xx,5.5,zz),.09,'dark',4)
for yy in [1.8,3.4,5.2]:
    box(.575,yy,8.375,1.65,.12,1.65,'wood')
for zz in [7.7,9.05]:
    beam((-.1,.3,zz),(1.25,3.3,zz),.055,'wood',4);beam((1.25,.3,zz),(-.1,3.3,zz),.055,'wood',4)
beam((.575,5.3,8.375),(.575,6.65,8.375),.73,'wood',20,r2=.68)
for yy in [5.4,5.95,6.55]:beam((.575,yy,8.375),(.575,yy+.075,8.375),.745,'iron',24)
for i in range(20):
    a=i*math.pi/10;beam((.575+.735*math.cos(a),5.4,8.375+.735*math.sin(a)),(.575+.69*math.cos(a),6.6,8.375+.69*math.sin(a)),.014,'dark',4)
current='jardineras'
for xx,zz in [(-6.3,3.3),(-5.4,8.5),(-1,10),(7,3),(7,10.4),(7.9,13.2),(2.7,13.6),(-6.5,-2)]:plant(xx,0,zz,1.0)
for xx in np.arange(-2.8,3.2,.5):plant(xx,4.65,3.35,.42)
current='letrero_rancho'
box(.1,6.4,.85,4.8,1.2,.1,'dark');box(.1,6.4,.92,4.65,1.05,.1,'light')
# Extruded pixel lettering, legible without external textures
font=ImageFont.truetype('C:/Windows/Fonts/georgiab.ttf',38)
im=Image.new('L',(240,55));dd=ImageDraw.Draw(im);dd.text((4,-3),'RANCHO',font=font,fill=255)
bb=im.getbbox();im=im.crop(bb);im.thumbnail((108,23));arr=np.asarray(im)
for yy in range(arr.shape[0]):
    for xx in range(arr.shape[1]):
        if arr[yy,xx]>110:box(.1+(xx-arr.shape[1]/2)*.037,6.4+(arr.shape[0]/2-yy)*.037,.99,.038,.038,.04,'dark')
current='portal_luna'
for xx in [-8.4,-6.8]:beam((xx,0,-4),(xx,3.4,-4),.12,'dark',4)
beam((-8.6,3.4,-4),(-6.6,3.4,-4),.14,'wood',4)
# stylized crescent, extruded open strip
for i in range(24):
    a=-1.22+i*2.44/24;b=-1.22+(i+1)*2.44/24
    def cp(t,r,off=0):return (-9.0-r*math.cos(t)+off,2.3+r*math.sin(t))
    ao=cp(a,1.3);bo=cp(b,1.3);ai=cp(a,1.16,.25);bi=cp(b,1.16,.25)
    for zz in [-4.08,-3.92]:quad((ao[0],ao[1],zz),(bo[0],bo[1],zz),(bi[0],bi[1],zz),(ai[0],ai[1],zz),colors['iron'])
    quad((ao[0],ao[1],-4.08),(ao[0],ao[1],-3.92),(bo[0],bo[1],-3.92),(bo[0],bo[1],-4.08),colors['iron'])

# Center entire footprint horizontally, retain ground at y=0.
v=np.array(V,dtype=np.float32);n=np.array(N,dtype=np.float32);c=np.array(C,dtype=np.float32)
center=(v.min(0)+v.max(0))/2;v[:,0]-=center[0];v[:,2]-=center[2]
# glTF color factors are linear; authored colors above are display sRGB.
linear=np.where(c<=.04045,c/12.92,((c+.055)/1.055)**2.4).astype(np.float32)
blob=b''; views=[];access=[]
for data in [v,n,linear]:
    raw=data.tobytes();views.append({'buffer':0,'byteOffset':len(blob),'byteLength':len(raw),'target':34962});blob+=raw
    acc={'bufferView':len(views)-1,'componentType':5126,'count':len(data),'type':'VEC3'}
    if len(access)==0:acc.update(min=data.min(0).tolist(),max=data.max(0).tolist())
    access.append(acc)
doc={'asset':{'version':'2.0','generator':'Rancho Media Luna - procedural concept v1'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'Rancho_Media_Luna_V1','mesh':0}],'meshes':[{'name':'Rancho completo','primitives':[{'attributes':{'POSITION':0,'NORMAL':1,'COLOR_0':2},'material':0,'mode':4}]}],'materials':[{'name':'Materiales rusticos - color por vertice','pbrMetallicRoughness':{'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':.88},'doubleSided':True}],'buffers':[{'byteLength':len(blob)}],'bufferViews':views,'accessors':access,'extras':{'units':'meters','upAxis':'Y','version':1,'source':'Interpretacion de imagen de referencia, dimensiones estimadas','parts':groups}}
j=json.dumps(doc,separators=(',',':')).encode();j+=b' '*((-len(j))%4);blob+=b'\0'*((-len(blob))%4)
glb=struct.pack('<III',0x46546c67,2,12+8+len(j)+8+len(blob))+struct.pack('<II',len(j),0x4e4f534a)+j+struct.pack('<II',len(blob),0x004e4942)+blob
(OUT/'rancho-medialuna-v1.glb').write_bytes(glb)
np.savez(Path(__file__).parent/'model.npz',v=v,n=n,c=c)
stats={'vertices':len(v),'triangulos':len(v)//3,'dimensiones_m':(v.max(0)-v.min(0)).round(2).tolist(),'tamano_MB':round(len(glb)/1048576,2),'partes':groups}
(OUT/'modelo-datos.json').write_text(json.dumps(stats,indent=2),encoding='utf8');print(stats)

# Self-contained native WebGL viewer, same mesh as the GLB; no CDN or network.
payload=base64.b64encode(v.tobytes()+n.tobytes()+c.tobytes()).decode()
html='''<!doctype html><html lang="es"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Rancho · primera versión 3D</title><style>body{margin:0;background:#e8e0cf;color:#352c21;font:15px system-ui}canvas{width:100vw;height:100vh;display:block;touch-action:none}header{position:absolute;top:25px;left:30px;pointer-events:none}h1{font:32px Georgia;margin:8px 0}small{letter-spacing:2px}footer{position:absolute;bottom:24px;left:30px;right:30px;display:flex;justify-content:space-between;align-items:center}a,button{border:1px solid #685c44;background:#fffaed;padding:12px 18px;color:#352c21;text-decoration:none;border-radius:8px;cursor:pointer}.note{position:absolute;right:30px;top:30px;background:#fffaedd9;padding:14px;border-radius:8px;max-width:240px;line-height:1.6}@media(max-width:700px){.note{display:none}footer span{max-width:180px}}</style><canvas id="c"></canvas><header><small>MEDIA LUNA / ESTUDIO 01</small><h1>Rancho restaurante</h1><span>Madera · piedra · adobe · terracota</span></header><div class="note">Modelo conceptual basado en tu imagen.<br>Escala aproximada; base en Y = 0.<br>Geometría 3D completa y materiales incluidos.</div><footer><span>Arrastra para girar · rueda para acercar</span><div><button id="reset">Restablecer vista</button> <a href="rancho-medialuna-v1.glb" download>Descargar .glb</a></div></footer><script>
const raw=atob('PAYLOAD'), buf=new Uint8Array(raw.length);for(let i=0;i<raw.length;i++)buf[i]=raw.charCodeAt(i);const floats=new Float32Array(buf.buffer),count=COUNT;
const canvas=document.querySelector('canvas'),gl=canvas.getContext('webgl',{antialias:true});
function shader(type,src){let s=gl.createShader(type);gl.shaderSource(s,src);gl.compileShader(s);if(!gl.getShaderParameter(s,gl.COMPILE_STATUS))throw Error(gl.getShaderInfoLog(s));return s}
let prog=gl.createProgram();gl.attachShader(prog,shader(gl.VERTEX_SHADER,`attribute vec3 p,n,c;uniform mat4 m;varying vec3 col;void main(){float l=.52+.48*max(0.,dot(normalize(n),normalize(vec3(-.5,1.,.7))));col=c*l;gl_Position=m*vec4(p,1.);}`));gl.attachShader(prog,shader(gl.FRAGMENT_SHADER,`precision mediump float;varying vec3 col;void main(){gl_FragColor=vec4(col,1.);}`));gl.linkProgram(prog);gl.useProgram(prog);
for(let [i,name] of ['p','n','c'].entries()){let b=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,b);gl.bufferData(gl.ARRAY_BUFFER,floats.subarray(i*count*3,(i+1)*count*3),gl.STATIC_DRAW);let a=gl.getAttribLocation(prog,name);gl.enableVertexAttribArray(a);gl.vertexAttribPointer(a,3,gl.FLOAT,false,0,0)}
gl.enable(gl.DEPTH_TEST);gl.clearColor(.91,.88,.81,1);let yaw=.70,pitch=.59,zoom=20;const uni=gl.getUniformLocation(prog,'m');
function draw(){let d=Math.min(devicePixelRatio,2);canvas.width=innerWidth*d;canvas.height=innerHeight*d;gl.viewport(0,0,canvas.width,canvas.height);let aspect=innerWidth/innerHeight, sx=1/(zoom*aspect),sy=1/zoom,cy=Math.cos(yaw),s=Math.sin(yaw),cp=Math.cos(pitch),sp=Math.sin(pitch);let right=[cy,0,-s],up=[-s*sp,cp,-cy*sp],dep=[s*cp,sp,cy*cp];let m=new Float32Array([right[0]*sx,up[0]*sy,-dep[0]/80,0,right[1]*sx,up[1]*sy,-dep[1]/80,0,right[2]*sx,up[2]*sy,-dep[2]/80,0,0,-4*cp*sy,4*sp/80,1]);gl.uniformMatrix4fv(uni,false,m);gl.clear(gl.COLOR_BUFFER_BIT|gl.DEPTH_BUFFER_BIT);gl.drawArrays(gl.TRIANGLES,0,count)}
let last;canvas.onpointerdown=e=>{last=[e.clientX,e.clientY];canvas.setPointerCapture(e.pointerId)};canvas.onpointermove=e=>{if(!last)return;yaw+=(e.clientX-last[0])*.007;pitch=Math.max(.08,Math.min(1.5,pitch+(e.clientY-last[1])*.007));last=[e.clientX,e.clientY];draw()};canvas.onpointerup=()=>last=null;canvas.onwheel=e=>{e.preventDefault();zoom=Math.max(8,Math.min(45,zoom*Math.exp(e.deltaY*.001)));draw()};document.querySelector('#reset').onclick=()=>{yaw=.70;pitch=.59;zoom=20;draw()};onresize=draw;draw();</script></html>'''
(OUT/'ver-rancho-3d.html').write_text(html.replace('PAYLOAD',payload).replace('COUNT',str(len(v))),encoding='utf8')

# Z-buffer rendered preview of actual geometry, not an image generation.
W,H=1500,1500;yaw=.70;pitch=.59
right=np.array([math.cos(yaw),0,-math.sin(yaw)]);up=np.array([-math.sin(yaw)*math.sin(pitch),math.cos(pitch),-math.cos(yaw)*math.sin(pitch)]);dep=np.cross(right,up)
pv=np.stack([v@right,v@up,v@dep],axis=1);scale=48;pv[:,0]=pv[:,0]*scale+W/2;pv[:,1]=H*.62-pv[:,1]*scale
pix=np.zeros((H,W,3),np.uint8);pix[:]=[235,226,207];depth=np.full((H,W),-np.inf,dtype=np.float32)
light=np.array([-.5,1,.7]);light/=np.linalg.norm(light)
for k in range(0,len(v),3):
    pts=pv[k:k+3];x0=max(0,int(pts[:,0].min()));x1=min(W-1,int(pts[:,0].max()+1));y0=max(0,int(pts[:,1].min()));y1=min(H-1,int(pts[:,1].max()+1))
    if x1<x0 or y1<y0:continue
    a,b,cc=pts;den=(b[1]-cc[1])*(a[0]-cc[0])+(cc[0]-b[0])*(a[1]-cc[1])
    if abs(den)<1e-8:continue
    xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
    aa=((b[1]-cc[1])*(xx-cc[0])+(cc[0]-b[0])*(yy-cc[1]))/den;bb=((cc[1]-a[1])*(xx-cc[0])+(a[0]-cc[0])*(yy-cc[1]))/den;ccc=1-aa-bb
    zz=aa*a[2]+bb*b[2]+ccc*cc[2];view=depth[y0:y1+1,x0:x1+1];mask=(aa>=0)&(bb>=0)&(ccc>=0)&(zz>view)
    view[mask]=zz[mask];shade=.52+.48*max(0,np.dot(n[k],light));pix[y0:y1+1,x0:x1+1][mask]=np.clip(c[k]*shade*255,0,255).astype(np.uint8)
im=Image.fromarray(pix);d=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/georgia.ttf',42);d.text((65,55),'RANCHO / MEDIA LUNA',font=font,fill='#483a28');d.text((67,112),'PRIMERA VERSION 3D  ·  VISTA DEL ARCHIVO GLB',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18),fill='#77664b');im.save(OUT/'rancho-v1-vista.png')
