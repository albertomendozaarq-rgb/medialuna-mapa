import * as T from 'three';
// Geometry stays three-dimensional when the map rotates. All sizes are metres.
const colors={ink:'#39362d',ivory:'#d7ccb1',hoof:'#514b3c'};
function mat(c){const m=new T.MeshStandardMaterial({color:colors[c]||c,roughness:.95});m.onBeforeCompile=s=>{s.vertexShader='varying vec3 ranchPoint;\n'+s.vertexShader;s.vertexShader=s.vertexShader.replace('#include <begin_vertex>','#include <begin_vertex>\nranchPoint=position;');s.fragmentShader='varying vec3 ranchPoint;\n'+s.fragmentShader;s.fragmentShader=s.fragmentShader.replace('#include <color_fragment>','#include <color_fragment>\nfloat grain=fract(sin(dot(floor(ranchPoint*95.),vec3(12.9898,78.233,34.13)))*43758.5453);float coatVariation=sin(ranchPoint.x*17.+sin(ranchPoint.y*11.))*sin(ranchPoint.z*13.);diffuseColor.rgb*=.91+.10*grain+.055*coatVariation;');};return m}
function ell(g,p,s,c){const m=new T.Mesh(new T.SphereGeometry(1,14,10),mat(c));m.position.set(...p);m.scale.set(...s);m.castShadow=m.receiveShadow=true;g.add(m);return m}
function line(g,points,r,c){const m=new T.Mesh(new T.TubeGeometry(new T.CatmullRomCurve3(points.map(p=>new T.Vector3(...p))),12,r,6,false),mat(c));g.add(m);m.castShadow=true;return m}
function horn(g,a,b,r,c){const v=new T.Vector3(...b).sub(new T.Vector3(...a));const m=new T.Mesh(new T.ConeGeometry(r,v.length(),9),mat(c));m.position.copy(new T.Vector3(...a).add(new T.Vector3(...b)).multiplyScalar(.5));m.quaternion.setFromUnitVectors(new T.Vector3(0,1,0),v.normalize());g.add(m);m.castShadow=true;return m}
function eyes(g,x,y,z,size=.025){for(const s of [-1,1]){ell(g,[x,y,s*z],[size,size,size*.5],'ink');ell(g,[x+.006,y+.009,s*(z+.01)],[size*.25,size*.25,size*.2],'ivory')}}
export function equine(type){const g=new T.Group(),donkey=type.startsWith('burr'),baby=type==='burrito',mare=type==='yegua';const coat=donkey?'#8b8980':mare?'#c9c1a8':'#9b603a',mane=donkey?'#49483f':mare?'#786d52':'#42372b';
 ell(g,[0,1.05,0],[.88,.44,.34],coat);ell(g,[-.60,1.10,0],[.34,.42,.34],coat);ell(g,[.56,1.12,0],[.30,.42,.32],coat);
 for(const x of [-.60,.57])for(const z of [-.22,.22]){const knee=x<0?x+.12:x-.025;ell(g,[x,.82,z],[.13,.32,.12],coat);line(g,[[x,.77,z],[knee,.45,z],[x-.055,.13,z]],.052,coat);ell(g,[knee,.44,z],[.073,.085,.07],coat);ell(g,[x-.02,.08,z],[.115,.08,.095],'hoof')}
 ell(g,[.69,1.47,0],[.26,.52,.24],coat).rotation.z=-.4;ell(g,[.88,1.81,0],[.22,.29,.205],coat).rotation.z=.45;
 ell(g,[1.09,1.73,0],[.34,.16,.18],coat).rotation.z=-.27;ell(g,[1.31,1.65,0],[.15,.14,.175],donkey?'#d0c7af':mare?'#a9a18e':'#76634b');
 for(const s of [-1,1]){const ear=ell(g,[.83,donkey?2.18:2.07,s*.115],[.062,donkey?.30:.145,.075],coat);ear.rotation.x=s*.22;ell(g,[.845,donkey?2.20:2.10,s*.12+.01],[.026,donkey?.20:.08,.055],'#b4a58e');ell(g,[1.38,1.71,s*.12],[.025,.016,.02],'ink')}
 eyes(g,1.025,1.86,.181,baby?.036:.027);
 for(let i=0;i<15;i++){const t=i/14;line(g,[[.38+t*.4,1.31+t*.67,0],[.32+t*.4,1.38+t*.65,-.03],[.30+t*.4,1.27+t*.65,-.09]],donkey?.025:.028,mane)}
 if(donkey){line(g,[[-.78,1.15,0],[-1.02,.94,.03],[-1.1,.51,.05]],.025,mane);ell(g,[-1.09,.43,.05],[.065,.14,.065],mane);line(g,[[-.7,1.46,0],[0,1.49,0],[.47,1.47,0]],.018,mane)}else for(let i=0;i<7;i++)line(g,[[-.80,1.26,(i-3)*.027],[-1.02,.89,(i-3)*.033],[-1.0,.26,(i-3)*.036]],.028,mane);
 if(type==='burrita'){// Small flower from the supplied mascot, kept subtle at map scale.
  for(let i=0;i<6;i++){let a=i*Math.PI/3;ell(g,[.9+.045*Math.cos(a),1.98+.045*Math.sin(a),.21],[.035,.025,.014],'ivory')}ell(g,[.9,1.98,.228],[.027,.027,.013],'#bc9c4f');
 }
 if(baby){const root=new T.Group();g.scale.set(.58,.64,.61);root.add(g);return root}
 if(donkey){const root=new T.Group();g.scale.set(.9,.86,.95);root.add(g);return root}
 return g;
}
export function goat(){let g=new T.Group(),c='#b29a72';ell(g,[0,.48,0],[.44,.26,.22],c);ell(g,[.35,.65,0],[.16,.26,.16],c).rotation.z=-.4;ell(g,[.49,.80,0],[.18,.16,.12],c);ell(g,[.62,.74,0],[.14,.085,.1],'#cbb99a');
 for(let x of [-.28,.27])for(let z of [-.14,.14]){line(g,[[x,.46,z],[x+.02,.24,z],[x-.015,.05,z]],.031,c);ell(g,[x,.04,z],[.055,.044,.043],'hoof')}
 for(let s of [-1,1]){ell(g,[.42,.86,s*.19],[.14,.045,.11],c);line(g,[[.41,.92,s*.07],[.36,1.09,s*.10],[.27,1.13,s*.13]],.025,'#776d56')}
 eyes(g,.54,.85,.113,.018);horn(g,[.55,.69,0],[.51,.54,0],.045,'#655941');horn(g,[-.38,.60,0],[-.53,.76,0],.06,c);return g;
}
// Individual tapered feathers create the layered silhouette of the references.
function feather(g,a,b,width,c){const av=new T.Vector3(...a),bv=new T.Vector3(...b),d=bv.clone().sub(av),n=new T.Vector3(-d.z,0,d.x).normalize().multiplyScalar(width);const mid=av.clone().lerp(bv,.5),ps=[av,mid.clone().add(n),bv,mid.clone().sub(n)];const geo=new T.BufferGeometry();geo.setAttribute('position',new T.Float32BufferAttribute(ps.flatMap(p=>p.toArray()),3));geo.setIndex([0,1,2,0,2,3]);geo.computeVertexNormals();const m=mat(c);m.side=T.DoubleSide;const o=new T.Mesh(geo,m);o.castShadow=true;g.add(o)}
export function bird(type){const g=new T.Group(),hawk=type==='gavilan',chick=type==='pollito',rooster=type==='gallo';
 if(hawk){ell(g,[0,.20,0],[.17,.13,.34],'#997049');ell(g,[0,.28,.33],[.115,.13,.14],'#c2a277');horn(g,[0,.29,.44],[0,.23,.54],.056,'#534b35');eyes(g,0,.31,.0);for(let s of [-1,1]){ell(g,[s*.084,.30,.375],[.020,.021,.027],'#d6ac4c');ell(g,[s*.10,.30,.38],[.008,.013,.016],'ink');for(let i=0;i<13;i++){let t=i/12;feather(g,[s*(.10+t*.65),.22, .10-t*.10],[s*(.35+t*.64),.16+t*.19,-.25-t*.19],.068,i%3?'#967048':'#604c35')}for(let i=0;i<9;i++){let t=i/8;feather(g,[s*(.12+t*.50),.24,.12],[s*(.28+t*.51),.245,-.18],.061,i%2?'#ae8351':'#805c38')}}for(let i=0;i<7;i++)feather(g,[(i-3)*.023,.19,-.20],[(i-3)*.055,.17,-.65],.043,i%2?'#b18a55':'#715639');return g}
 const coat=chick?'#dfc26e':rooster?'#935b30':'#bba17a',h=chick?.13:.31;
 ell(g,[0,h,0],[chick?.12:.24,chick?.115:.23,chick?.10:.19],coat);ell(g,[.17*(chick?.6:1),h+(chick?.08:.20),0],[chick?.085:.12,chick?.09:.14,chick?.075:.10],chick?coat:rooster?'#b6894d':'#cdb795');
 for(let s of [-1,1]){line(g,[[0,h-.06,s*(chick?.045:.09)],[.015,.035,s*(chick?.045:.09)]],chick?.009:.017,'#aa8946');for(let toe of [-1,0,1])line(g,[[.015,.025,s*(chick?.045:.09)],[chick?.065:.12,.014,s*(chick?.045:.09)+toe*(chick?.018:.03)]],.008,'#aa8946');ell(g,[-.02,h,s*(chick?.075:.14)],[chick?.08:.17,chick?.07:.12,.035],chick?'#ccb064':rooster?'#4e6353':'#90734f')}
 const hx=chick?.10:.17,hy=h+(chick?.08:.20);horn(g,[hx+.06,hy,0],[hx+(chick?.115:.18),hy-.02,0],chick?.024:.044,'#b89843');eyes(g,hx+.035,hy+.033,chick?.07:.094,chick?.012:.015);
 if(!chick){for(let i=0;i<4;i++)ell(g,[.11+i*.04,hy+.13+Math.sin(i)*.02,0],[.034,.052,.024],'#a44732');ell(g,[.23,hy-.10,0],[.033,.06,.025],'#a44732');for(let i=0;i<(rooster?8:5);i++){let z=(i-3)*.027;line(g,[[-.15,h,z],[-.35,h+(rooster?.32:.16),z],[-.49,h+(rooster?.21:.10),z]],.023,rooster?(i%2?'#43594e':'#555745'):'#8d7654')}}
 return g;
}
export function stable(){const g=new T.Group(),wood='#77603f',light='#a18a60';function beam(a,b,r=.055){line(g,[a,b],r,wood)}
 for(let x of [-3,-1,1,3]){for(let z of [-1.5,1.5])beam([x,0,z],[x,2.65,z],.085);beam([x,1.15,-1.5],[x,1.15,1.5]);beam([x,2.65,-1.5],[x,3.35,0]);beam([x,3.35,0],[x,2.65,1.5]);for(let y=.25;y<2.5;y+=.20)beam([x,y,-1.5],[x,y,1.5],.07)}
 for(let y=.2;y<2.6;y+=.21)beam([-3,y,-1.5],[3,y,-1.5],.08);
 for(let x of [-2,0,2]){beam([x-1,1.0,1.5],[x+1,1.0,1.5]);beam([x-1,.45,1.5],[x+1,.45,1.5]);beam([x-1,.4,1.5],[x+1,1.15,1.5],.036);}
 for(let s of [-1,1]){const roof=new T.Mesh(new T.BoxGeometry(6.6,.055,1.96),mat('#b7b5a4'));roof.position.set(0,3.0,s*.82);roof.rotation.x=s*.4;roof.castShadow=true;g.add(roof);for(let x=-3.25;x<3.3;x+=.14)line(g,[[x,3.37,0],[x,2.67,s*1.75]],.015,(Math.round(x*100)%7===0)?'#9e7950':'#d1ceba')}
 for(let x of [-2,0,2])ell(g,[x,.20,-.9],[.55,.2,.36],light);return g;
}
