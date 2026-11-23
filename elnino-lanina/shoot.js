const {chromium}=require('playwright');
(async()=>{
  const [,,out,...times]=process.argv;
  const b=await chromium.launch({args:['--allow-file-access-from-files']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  const errs=[]; p.on('pageerror',e=>errs.push(e.message)); p.on('console',m=>{if(m.type()==='error')errs.push(m.text())});
  await p.goto('file://'+__dirname+'/'+(process.env.SCENE||'globe.html')+''); await p.evaluate(()=>window.ready);
  require('fs').mkdirSync(out,{recursive:true});
  for(const [i,t] of times.entries()){ await p.evaluate(t=>renderFrame(+t),t);
    await (await p.$('canvas')).screenshot({path:`${out}/${String(i).padStart(2,'0')}.png`}); }
  if(errs.length) console.log('ERR',errs.slice(0,5));
  await b.close();
})();
