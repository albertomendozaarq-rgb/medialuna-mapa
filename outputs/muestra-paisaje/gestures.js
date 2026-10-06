// State policy shared by pointer integration and deterministic tests.
// A second finger cancels any edit and blocks editing until ALL fingers lift.
export class GestureIntent {
 constructor(){this.pointers=new Map();this.blocked=false;this.primary=null;this.moved=false}
 down(e){this.pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});if(this.pointers.size>1){this.blocked=true;return 'navigate'}this.primary=e.pointerId;this.moved=false;return this.blocked?'navigate':'pending'}
 move(e){if(this.blocked||this.pointers.size>1)return 'navigate';const p=this.pointers.get(e.pointerId);if(!p||e.pointerId!==this.primary)return 'ignore';if(Math.hypot(e.clientX-p.x,e.clientY-p.y)>6)this.moved=true;return this.moved?'drag':'pending'}
 up(e,cancel=false){const was=this.pointers.has(e.pointerId);const result=!was||cancel||this.blocked?'cancel':this.moved?'dragEnd':'tap';this.pointers.delete(e.pointerId);if(!this.pointers.size){this.blocked=false;this.primary=null;this.moved=false}return result}
 reset(){this.pointers.clear();this.blocked=false;this.primary=null;this.moved=false}
}
