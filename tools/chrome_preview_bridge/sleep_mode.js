/* Sleep Mode: one plan, one bound chat, no blind resend on ambiguous submission. */
const SLEEP_ALARM="iclone-sleep", SLEEP_LOCAL="icloneSleepHandoff";
async function sleepApi(path,body){const r=await req("/sleep/"+path,body);if(!r.ok){let x={};try{x=await r.json()}catch{}throw Error(x.error||("Sleep relay "+r.status))}return r.json()}
async function sleepLocal(){return (await chrome.storage.local.get(SLEEP_LOCAL))[SLEEP_LOCAL]||{}}
async function sleepStore(x){await chrome.storage.local.set({[SLEEP_LOCAL]:x})}
async function sleepGoal(url,enabled){
 const s=await goalGet();if(s?.enabled&&s.url!==url)throw Error("another goal chat active");
 const n=newSession(url,enabled);n.mode="sleep";await goalSet(n);
 if(enabled)await chrome.alarms.create(GOAL_ALARM,{periodInMinutes:.5});else await chrome.alarms.clear(GOAL_ALARM)
}
async function sleepPage(tab,project,marker,message,send){
 const result=await chrome.scripting.executeScript({target:{tabId:tab.id},args:[project,marker,message,send],func:async(project,marker,message,send)=>{
  const href=location.origin+location.pathname.replace(/\/$/,"");
  const within=href===project||href===project+"/project"||href.startsWith(project+"/c/");
  if(!within)return {state:"wrong project"};
  const vis=e=>e&&e.getClientRects().length>0;
  const users=[...document.querySelectorAll('[data-message-author-role="user"],[data-turn="user"],article[data-role="user"]')];
  if(users.some(e=>e.innerText.trim().startsWith(marker)))return {state:"sent",url:href};
  if(href.includes("/c/")||users.length)return {state:"not a fresh chat"};
  const c=document.querySelector("#prompt-textarea"),draft=()=>String(c?.value??c?.innerText??"").trim();
  const busy=()=>[...document.querySelectorAll('[data-testid="stop-button"],button[aria-label="หยุด"],button[aria-label="Stop"]')].some(vis);
  const attach=()=>[...document.querySelectorAll('[data-testid="remove-attachment"],button[aria-label*="Remove attachment"],button[aria-label^="ลบ "]')].some(vis);
  if(!c||!vis(c)||busy()||attach())return {state:"not ready"};
  if(draft()&&draft()!==message.trim())return {state:"user draft"};
  if(!send)return {state:draft()?"own draft":"ready"};
  if(!(await chrome.runtime.sendMessage({type:"iclone-sleep-safe",project,marker})).ok)return {state:"wait"};
  if(!draft()){
   c.focus({preventScroll:true});
   if("value" in c){Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value").set.call(c,message);c.dispatchEvent(new Event("input",{bubbles:true}))}
   else document.execCommand("insertText",false,message);
  }
  if(draft()!==message.trim())return {state:"draft unknown"};
  // Sending may have created a conversation even if the service worker loses its receipt.
  for(let i=0;i<30;i++){
   const b=[...document.querySelectorAll('button#composer-submit-button,button[data-testid="send-button"],button[aria-label="ส่ง"],button[aria-label="Send"]')].filter(e=>vis(e)&&!e.disabled&&e.getAttribute("aria-disabled")!=="true");
   if(b.length===1&&!busy()&&!attach()&&draft()===message.trim()&&(await chrome.runtime.sendMessage({type:"iclone-sleep-safe",project,marker})).ok){
    b[0].click();return {state:"attempted"}
   }
   await new Promise(r=>setTimeout(r,250));
  }
  return {state:"draft waiting"}
 }});
 return result[0]?.result||{state:"unknown"}
}
let sleepRunning=false;
async function sleepTick(){
 if(sleepRunning||running)return;sleepRunning=true;running=true;
 try{
  let s=await sleepApi("status");if(!s.enabled||s.ready===false)return;
  if(!await idle())return;
  let l=await sleepLocal();
  if(s.phase==="work"){
   const tabs=(await chrome.tabs.query({url:"https://chatgpt.com/*"})).filter(t=>chatURL(t.url)===s.url);
   if(tabs.length!==1)return;
   const g=await goalGet();
   if(g?.enabled&&g.url!==s.url)throw Error("other goal active");
   const probe=await goalPage(tabs[0],g?.url===s.url?g:{url:s.url},"probe",g?.pending?.marker||"",g?.pending?.message||"");
   if(probe.busy||probe.draft||probe.attachment)return;
   if((await previewPriority(s.url)).wait)return;
   // Server verifies actual files, final QA and exact approved plan before advancing.
   try{s=await sleepApi("advance",{url:s.url,session:s.session})}catch{
    if(!g?.enabled){await sleepGoal(s.url,true)}
    return
   }
   await sleepGoal(g?.url||s.old_url||s.url,false);
   await sleepStore({});
   if(!s.enabled||s.ready===false)return;
  }
  if(s.phase!=="handoff")return;
  l=await sleepLocal();
  if(l.session!==s.session||l.part!==s.part){
   l={session:s.session,part:s.part,marker:"[Sleep "+s.session.slice(0,8)+" part "+s.part+"]",phase:"create"};
   await sleepStore(l);
  }
  if(l.phase==="create"){
   // Reserve before creating a tab; after ambiguous crash do not create another.
   l.phase="creating";await sleepStore(l);
   const t=await chrome.tabs.create({url:s.project+"/project",active:false});l.tabId=t.id;l.phase="draft";await sleepStore(l);return
  }
  if(l.phase==="creating")throw Error("tab creation uncertain; pause and inspect");
  const tab=await chrome.tabs.get(l.tabId);
  if(l.phase==="attempted"){
   const res=await sleepPage(tab,s.project,l.marker,"",false);
   if(res.state==="sent"&&chatURL(res.url)&&res.url!==s.old_url){
    s=await sleepApi("bind",{session:s.session,url:res.url});await sleepGoal(s.url,true);await sleepStore({});return
   }
   l.status="awaiting exact posted receipt (no resend)";await sleepStore(l);return
  }
  if(l.phase==="draft"){
   const data=await sleepApi("prompt");
   const msg=l.marker+" "+data.prompt;
   const probe=await sleepPage(tab,s.project,l.marker,msg,false);
   if(probe.state!=="ready"&&probe.state!=="own draft")return;
   // Persist ambiguity fence before the send. Never retry after unknown outcome.
   l.phase="attempted";await sleepStore(l);
   const res=await sleepPage(tab,s.project,l.marker,msg,true);
   if(["wait","draft waiting","not ready","user draft"].includes(res.state)){l.phase="draft";await sleepStore(l)}
  }
 }catch(e){const l=await sleepLocal();l.status=String(e);await sleepStore(l)}
 finally{running=false;sleepRunning=false}
}
chrome.alarms.onAlarm.addListener(a=>{if(a.name===SLEEP_ALARM)void sleepTick()});
async function sleepInit(){await chrome.alarms.create(SLEEP_ALARM,{periodInMinutes:.5})}
chrome.runtime.onInstalled.addListener(sleepInit);chrome.runtime.onStartup.addListener(sleepInit);sleepInit().catch(()=>{});
chrome.runtime.onMessage.addListener((m,sender,reply)=>{
 if(m?.type==="iclone-sleep-safe"){
  (async()=>{const s=await sleepApi("status"),l=await sleepLocal();return {ok:!!s.enabled&&s.phase==="handoff"&&s.project===m.project&&l.marker===m.marker&&l.tabId===sender.tab?.id&&await idle()}})().then(reply).catch(()=>reply({ok:false}));return true
 }
 if(m?.type!=="iclone-sleep-control")return;
 (async()=>{
  if(m.action==="status"){const s=await sleepApi("status");return {...s,local:await sleepLocal()}}
  if(m.action==="pause"){const s=await sleepApi("pause",{});const g=await goalGet();if(g?.enabled&&(g.url===s.url||g.url===s.old_url))await sleepGoal(g.url,false);return s}
  if(m.action==="start"){
   const url=await callerURL(sender);const g=await goalGet();
   if(!url||g?.enabled&&g.url!==url)throw Error("pause other goal and select project chat");
   const ready=await sleepApi("status");if(!ready.ready)throw Error(ready.reason||"Preview runtime not ready");const s=await sleepApi("start",{url,confirmed:m.confirmed===true,scope:m.scope||"all"});await sleepStore({});
   if(g?.enabled)await sleepGoal(url,false);return s
  }
  throw Error("unknown action")
 })().then(reply).catch(e=>reply({error:String(e)}));return true
});
