(()=>{
 if(globalThis.__icGenericGoalWake)return;globalThis.__icGenericGoalWake=true;
 const eligible=()=>location.origin==="https://chatgpt.com"&&/\/c\/[a-zA-Z0-9-]+\/?$/.test(location.pathname);
 let last=0,timer=null;
 function dispose(){if(timer!==null)clearInterval(timer);timer=null;globalThis.__icGenericGoalWake=false}
 function wake(){
  if(!eligible()||Date.now()-last<1500)return;
  last=Date.now();
  try{
   if(!chrome.runtime?.id){dispose();return}
   Promise.resolve(chrome.runtime.sendMessage({type:"iclone-goal-ready"})).catch(e=>{if(/context invalidated/i.test(String(e)))dispose()});
  }catch(e){dispose()}
 }
 timer=setInterval(wake,2000);wake();
})();