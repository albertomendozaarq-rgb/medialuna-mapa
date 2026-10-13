import * as T from 'three';

const NO_SHADOW=new Set(['lavanda','maguey','vid','formio','silverDoll','arbusto','piedraS','piedraM','dolar']);

export class StreamingGrid{
 constructor(root,{cellSize=140}={}){this.root=root;this.cellSize=cellSize;this.cells=new Map();this.members=new WeakMap();this.last='';this.stats={active:0,total:0,cells:0};}
 keyFor(o){return `${Math.floor(o.position.x/this.cellSize)},${Math.floor(o.position.z/this.cellSize)}`}
 add(o){this.root.add(o);this.index(o);this.stats.total=this.root.children.length}
 remove(o){const key=this.members.get(o),set=this.cells.get(key);set?.delete(o);if(set&&!set.size)this.cells.delete(key);this.members.delete(o);this.root.remove(o);this.stats.total=this.root.children.length}
 index(o){const next=this.keyFor(o),prev=this.members.get(o);if(next===prev)return;if(prev){const old=this.cells.get(prev);old?.delete(o);if(old&&!old.size)this.cells.delete(prev)}if(!this.cells.has(next))this.cells.set(next,new Set());this.cells.get(next).add(o);this.members.set(o,next)}
 rebuild(){this.cells.clear();for(const o of this.root.children){this.members.delete(o);this.index(o)}this.last=''}
 radiusFor(target,camera){const distance=camera.position.distanceTo(target);return distance<280?1:distance<650?2:3}
 contains(x,z,target,camera,margin=0){const cx=Math.floor(target.x/this.cellSize),cz=Math.floor(target.z/this.cellSize),ox=Math.floor(x/this.cellSize),oz=Math.floor(z/this.cellSize);return Math.max(Math.abs(ox-cx),Math.abs(oz-cz))<=this.radiusFor(target,camera)+margin}
 update(target,camera,selected=null,force=false){
  const cx=Math.floor(target.x/this.cellSize),cz=Math.floor(target.z/this.cellSize),radius=this.radiusFor(target,camera),key=`${cx},${cz},${radius}`;
  if(!force&&key===this.last)return false;this.last=key;let active=0,cells=0;
  for(const [cell,set] of this.cells){const [x,z]=cell.split(',').map(Number),visible=Math.max(Math.abs(x-cx),Math.abs(z-cz))<=radius;if(visible)cells++;
   for(const o of set){const keep=visible||o===selected;o.visible=keep;if(keep)active++;const nearShadow=keep&&Math.max(Math.abs(x-cx),Math.abs(z-cz))<=1&&!NO_SHADOW.has(o.userData.type);o.traverse(n=>{if(n.isMesh)n.castShadow=nearShadow})}
  }
  this.stats={active,total:this.root.children.length,cells};return true;
 }
 visibleObjects(){return this.root.children.filter(o=>o.visible)}
}

export class AdaptiveResolution{
 constructor(renderer,controls){this.renderer=renderer;this.controls=controls;this.moving=true;this.lastMove=performance.now();this.current=0;controls.addEventListener('change',()=>{this.moving=true;this.lastMove=performance.now()})}
 update(){const moving=performance.now()-this.lastMove<220,target=Math.min(devicePixelRatio,moving?1:1.25);if(Math.abs(target-this.current)>.01){this.current=target;this.renderer.setPixelRatio(target);return true}return false}
}
