(()=>{
 if(globalThis.__icGenericGoalWake)return;globalThis.__icGenericGoalWake=true;
 const eligible=()=>location.origin==="https://chatgpt.com"&&/\/c\/[a-zA-Z0-9-]+\/?$/.test(location.pathname);
 let last=0,timer=null,lastHandoff=0,boundHandoff="";
 function dispose(){if(timer!==null)clearInterval(timer);timer=null;globalThis.__icGenericGoalWake=false}
 function wake(){
  if(!eligible()||Date.now()-last<1500)return;
  last=Date.now();
  try{
   if(!chrome.runtime?.id){dispose();return}
   if(Date.now()-lastHandoff>5000){
    lastHandoff=Date.now();
    // user pasted the plugin prompt, or GPT wrote the chat code Ai-iclone printed (user 2026-11-28: no bind button)
    const msgs=Array.from(document.querySelectorAll('[data-message-author-role="user"],[data-message-author-role="assistant"],[data-turn="user"],[data-turn="assistant"],article[data-role="user"]'));
    const matches=msgs.map(e=>(e.innerText||"").match(/\[iClone Handoff ([a-f0-9]{32})\]/)).filter(Boolean);
    const id=matches.at(-1)?.[1];
    if(id&&id!==boundHandoff)Promise.resolve(chrome.runtime.sendMessage({type:"iclone-handoff-observed",id})).then(r=>{if(r?.ok)boundHandoff=id}).catch(()=>{});
   }
   Promise.resolve(chrome.runtime.sendMessage({type:"iclone-goal-ready"})).catch(e=>{if(/context invalidated/i.test(String(e)))dispose()});
  }catch(e){dispose()}
 }
 timer=setInterval(wake,2000);wake();
})();