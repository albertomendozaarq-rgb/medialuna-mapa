import * as T from 'three';
import {GLTFLoader} from './GLTFLoader.js';
export const MAX_BYTES=80*1024*1024;
export const CATEGORIES={decor:'Decoración',buildings:'Edificios',animals:'Animales',people:'Personas',vehicles:'Autos',ranch:'Corrales',plants:'Vegetación'};
const items=new Map();let db;
const openDB=()=>db?Promise.resolve(db):new Promise((resolve,reject)=>{const r=indexedDB.open('media-luna-modulos-01',1);r.onupgradeneeded=()=>r.result.createObjectStore('modules',{keyPath:'id'});r.onsuccess=()=>resolve(db=r.result);r.onerror=()=>reject(r.error)});
export async function persist(item){const d=await openDB();await new Promise((resolve,reject)=>{const tx=d.transaction('modules','readwrite');tx.objectStore('modules').put(item);tx.oncomplete=resolve;tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error)})}
export function allModules(){return [...items.values()]}
export function getModule(id){return items.get(id)}
export function metadata(item){return {id:item.id,name:item.name,category:item.category,height:item.height,yaw:item.yaw||0,hidden:!!item.hidden}}
export function validateMeta(m){if(!m||!/^mod:[a-z0-9_-]{1,80}$/.test(m.id)||typeof m.name!=='string'||!m.name.trim()||m.name.length>80||!CATEGORIES[m.category]||!Number.isFinite(m.height)||m.height<.05||m.height>100||!Number.isFinite(m.yaw||0))throw Error('Ficha de módulo inválida');return metadata(m)}
export function inspectGLB(buffer){
 if(!(buffer instanceof ArrayBuffer)||buffer.byteLength<20||buffer.byteLength>MAX_BYTES)throw Error('Usa un GLB de hasta 80 MB');const v=new DataView(buffer);
 if(v.getUint32(0,true)!==0x46546c67||v.getUint32(4,true)!==2||v.getUint32(8,true)!==buffer.byteLength||v.getUint32(16,true)!==0x4e4f534a)throw Error('El archivo no es un GLB 2 válido');
 const len=v.getUint32(12,true);if(len+20>buffer.byteLength)throw Error('GLB incompleto');const j=JSON.parse(new TextDecoder().decode(new Uint8Array(buffer,20,len)).trim());
 for(const resource of [...(j.buffers||[]),...(j.images||[])])if(resource.uri&&!/^data:(image\/|application\/octet-stream)/.test(resource.uri))throw Error('El GLB debe incluir sus texturas y recursos, sin archivos externos');
 if(j.skins?.length)throw Error('Exporta este módulo estático sin esqueleto o rig');
 const unsupported=(j.extensionsRequired||[]).filter(k=>['KHR_draco_mesh_compression','EXT_meshopt_compression','KHR_texture_basisu'].includes(k));if(unsupported.length)throw Error('Exporta GLB sin compresión Draco, Meshopt o KTX2');return j;
}
export async function parseModel(buffer){inspectGLB(buffer);const manager=new T.LoadingManager();manager.setURLModifier(url=>{if(!url.startsWith('blob:')&&!url.startsWith('data:'))throw Error('Recurso externo no permitido');return url});const gltf=await new GLTFLoader(manager).parseAsync(buffer,'');const root=gltf.scene;
 const bounds=new T.Box3().setFromObject(root),size=bounds.getSize(new T.Vector3());if(!size.toArray().every(Number.isFinite)||size.y<.00001)throw Error('El modelo no tiene un volumen válido');root.traverse(o=>{if(o.isLight||o.isCamera)o.visible=false;if(o.isMesh){o.castShadow=o.receiveShadow=true}});return root;
}
export function instance(item){
 const root=new T.Group();if(!item?.template){const m=new T.Mesh(new T.BoxGeometry(1,1,1),new T.MeshStandardMaterial({color:'#b9a880',wireframe:true}));m.position.y=.5;root.add(m);root.userData.missingModule=true;return root}
 const model=item.template.clone(true);model.traverse(o=>{if(o.isMesh){o.geometry=o.geometry.clone();o.material=Array.isArray(o.material)?o.material.map(m=>m.clone()):o.material.clone()}});
 const wrapper=new T.Group();wrapper.add(model);const b=new T.Box3().setFromObject(model),s=b.getSize(new T.Vector3()),c=b.getCenter(new T.Vector3());model.position.sub(new T.Vector3(c.x,b.min.y,c.z));wrapper.scale.setScalar(item.height/s.y);wrapper.rotation.y=T.MathUtils.degToRad(item.yaw||0);root.add(wrapper);return root;
}
export async function prepare(buffer,fields){const hash=await crypto.subtle.digest('SHA-256',buffer);const id='mod:'+Array.from(new Uint8Array(hash)).slice(0,12).map(n=>n.toString(16).padStart(2,'0')).join('');const m=validateMeta({...fields,id});return {...m,buffer,template:await parseModel(buffer),source:'local'}}
export async function register(item,save=true){validateMeta(item);if(save)await persist({...metadata(item),buffer:item.buffer,source:item.source});items.set(item.id,item);return item}
export async function hideModule(item,hidden){await persist({...metadata(item),buffer:item.buffer,source:item.source,hidden});item.hidden=hidden}
export function ensureRefs(refs=[]){for(const ref of refs){const m=validateMeta(ref);if(!items.has(m.id))items.set(m.id,{...m,missing:true,hidden:true})}}
export async function loadModules(){const errors=[];try{const d=await openDB();const stored=await new Promise((resolve,reject)=>{const r=d.transaction('modules').objectStore('modules').getAll();r.onsuccess=()=>resolve(r.result);r.onerror=()=>reject(r.error)});for(const raw of stored){try{const m=validateMeta(raw);items.set(m.id,{...m,buffer:raw.buffer,source:raw.source||'local',template:raw.buffer?await parseModel(raw.buffer):null})}catch(e){errors.push('Módulo local: '+e.message)}}}catch(e){errors.push('No se pudo leer el catálogo local')}
 if(location.protocol==='http:'||location.protocol==='https:')try{const url=new URL('catalogo/manifest.json',document.baseURI),r=await fetch(url,{cache:'no-cache'});if(r.ok){const manifest=await r.json();if(manifest.version!==1||!Array.isArray(manifest.modules)||manifest.modules.length>200)throw Error('Manifest inválido');for(const raw of manifest.modules){try{const m=validateMeta(raw),local=items.get(m.id);if(local?.template){local.retired=!!raw.retired;continue;}const asset=new URL(raw.file,url);if(asset.origin!==url.origin||!asset.pathname.startsWith(new URL('modulos/',url).pathname))throw Error('Ruta fuera de catalogo/modulos');const response=await fetch(asset);if(!response.ok)throw Error('No se encontró '+m.name);const buffer=await response.arrayBuffer();items.set(m.id,{...m,hidden:local?.hidden??false,buffer,template:await parseModel(buffer),source:'shared',retired:!!raw.retired})}catch(e){errors.push(e.message)}}}}catch(e){errors.push('Catálogo compartido: '+e.message)}return errors;
}
export function base64(buffer){const a=new Uint8Array(buffer);let parts=[];for(let i=0;i<a.length;i+=32768)parts.push(String.fromCharCode(...a.subarray(i,i+32768)));return btoa(parts.join(''))}
export function unbase64(s){if(typeof s!=='string'||s.length>MAX_BYTES*1.34)throw Error('Módulo demasiado grande');const r=atob(s),a=new Uint8Array(r.length);for(let i=0;i<r.length;i++)a[i]=r.charCodeAt(i);return a.buffer}
export function modulePackage(item){if(!item.buffer)throw Error('Falta el archivo del módulo');return {format:'medialuna-module',version:1,...metadata(item),glb:base64(item.buffer)}}
export async function fromPackage(raw){if(raw.format!=='medialuna-module'||raw.version!==1)throw Error('Paquete de módulo inválido');const m=validateMeta(raw),item=await prepare(unbase64(raw.glb),m);if(item.id!==m.id)throw Error('El contenido no coincide con la ficha');return {...item,hidden:!!raw.hidden}}
export function releaseInstance(root){root.traverse(o=>{if(o.isMesh){o.geometry.dispose();for(const m of Array.isArray(o.material)?o.material:[o.material])m.dispose()}})}
