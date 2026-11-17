const {chromium}=require('playwright');const fs=require('fs');const S='/home/claude/tr';
(async()=>{const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage();
await p.addInitScript(()=>{try{localStorage.setItem('sensorPlateMode','sandwich')}catch(e){}});
await p.route('**/*',r=>{const u=r.request().url();
 if(u.includes('three.min.js'))return r.fulfill({body:fs.readFileSync(S+'/npmt/node_modules/three/build/three.min.js'),contentType:'text/javascript'});
 if(u.includes('OrbitControls'))return r.fulfill({body:fs.readFileSync(S+'/npmt/node_modules/three/examples/js/controls/OrbitControls.js'),contentType:'text/javascript'});
 if(u.endsWith('meshes.js'))return r.fulfill({body:fs.readFileSync(S+'/viewer/meshes.js'),contentType:'text/javascript'});
 if(u.startsWith('http://local/'))return r.fulfill({body:'<!doctype html><html><head><meta charset=utf-8></head><body>'+fs.readFileSync(S+'/viewer/app.html','utf8').replace('})();\n</script>','window.__dbg={get layout(){return layout},get objs(){return boardObjs},LIB,evaluate,PLATE_TOP,PLATE_T,BTOP,SPACER,offPlate};})();\n</script>')+'</body></html>',contentType:'text/html'});
 return r.abort();});
await p.goto('http://local/i.html');await p.waitForTimeout(3000);
const d=await p.evaluate(()=>{const D=window.__dbg;const {G}=D.evaluate();
 return {BTOP:D.BTOP, SPACER:D.SPACER, PT:D.PLATE_T, boards:D.layout.map((b,i)=>{const o=D.objs[i]; o.updateMatrixWorld(true); const L=D.LIB[b.type], g=G[i], bd=g.body||g;
  return {id:b.id,type:b.type,brd:g.brd,face:D.offPlate(b)?'off':(g.back?'back':'front'),m:o.matrixWorld.elements.slice(),
   u0:g.u0,u1:g.u1,v0:g.v0,v1:g.v1,bu0:bd.u0,bu1:bd.u1,bv0:bd.v0,bv1:bd.v1,ntop:g.ntop,nbot:g.nbot,box:L.box||null,cyl:!!L.cyl,cylZ:!!L.cylZ,hex:!!L.hex};})};});
fs.writeFileSync(S+'/layout_sandwich.json',JSON.stringify(d,null,1));
for(const x of d.boards) console.log(x.id.padEnd(9),x.brd,x.face.padEnd(5),'U',x.bu0.toFixed(2),x.bu1.toFixed(2),'V',x.bv0.toFixed(2),x.bv1.toFixed(2),'N',x.nbot.toFixed(2),x.ntop.toFixed(2));
console.log(JSON.stringify(d.BTOP));await b.close();})();
