const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{
  const FPS=30, DUR=40, N=DUR*FPS, W=4; fs.mkdirSync('frames',{recursive:true});
  const b=await chromium.launch({args:['--allow-file-access-from-files']});
  let errs=[];
  await Promise.all([...Array(W)].map(async(_,w)=>{
    const p=await b.newPage({viewport:{width:1080,height:1920}});
    p.on('pageerror',e=>errs.push(e.message));
    await p.goto('file://'+__dirname+'/globe2.html'); await p.evaluate(()=>window.ready);
    const c=await p.$('canvas');
    for(let f=w; f<N; f+=W){ await p.evaluate(t=>renderFrame(t),f/FPS);
      await c.screenshot({path:`frames/${String(f).padStart(5,'0')}.png`}); }
  }));
  console.log('done',N,'errors',errs.length,errs.slice(0,3)); await b.close();
})();
