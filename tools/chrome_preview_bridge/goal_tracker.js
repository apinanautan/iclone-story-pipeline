/* Generic context-driven follow-up, one explicitly selected chat at a time. */
const GOAL_KEY="icloneGoalTracker";
const GOAL_ALARM="iclone-goal-followup";
const LEGACY_URL=null;
const DEFAULT_PROMPT="ติดตามเป้าหมายล่าสุดจากบริบทของแชตนี้ ให้ลงมือทำงานต่อจริงด้วยเครื่องมือและขั้นตอนที่เกี่ยวข้องจนบรรลุผลตามที่ผู้ใช้สั่ง ไม่ใช่เพียงรายงานสถานะหรือเสนอว่าจะทำอะไร ตรวจผลงานจริง แก้ส่วนที่ยังไม่ผ่าน และทำขั้นถัดไปที่ได้รับอนุญาตทันที โดยคงข้อจำกัดและจุดรออนุมัติของผู้ใช้ทุกข้อ ถ้ามีอุปสรรคที่แก้เองไม่ได้ ให้แจ้งเฉพาะสิ่งที่ติดจริง ไม่อ้างว่างานเสร็จโดยไม่มีหลักฐาน";
const chatURL=x=>{try{const u=new URL(x);return u.origin==="https://chatgpt.com"&&/\/c\/[a-zA-Z0-9-]+\/?$/.test(u.pathname)?u.origin+u.pathname.replace(/\/$/,""):null}catch{return null}};
const goalGet=async()=>{const o=await chrome.storage.local.get(GOAL_KEY);return o[GOAL_KEY]||null};
const goalSet=async(s)=>{await chrome.storage.local.set({[GOAL_KEY]:s})};
const newSession=(url,enabled=false)=>({schema:2,url,session:crypto.randomUUID(),achievement:"ACHIEVEMENT: "+crypto.randomUUID().slice(0,12).toUpperCase(),enabled,minutes:1.5,next:Date.now(),pending:null,status:enabled?"starting immediately":"paused"});
const validFor=(s,url)=>s?.url===url;
async function goalInit(){
 let s=await goalGet();
 if(s?.schema!==2){const old=s;s=newSession(LEGACY_URL,false);s.next=old?.next||Date.now();await goalSet(s)}
 if(s.minutes!==1.5){const old=Number(s.minutes)||3;if(s.enabled&&s.next>Date.now())s.next=Math.max(Date.now(),s.next+(1.5-old)*60000);s.minutes=1.5;await goalSet(s)}
 if(s.enabled&&!await chrome.alarms.get(GOAL_ALARM))await chrome.alarms.create(GOAL_ALARM,{periodInMinutes:.5});
 const tabs=await chrome.tabs.query({url:"https://chatgpt.com/*"});
 for(const t of tabs.filter(t=>chatURL(t.url)))try{await chrome.scripting.executeScript({target:{tabId:t.id},files:["achievement_observer.js","goal_panel.js"]})}catch{}
 // Recover a completed session on extension reload, even if paused to stop runaway sends.
 const bound=tabs.filter(t=>chatURL(t.url)===s.url);
 if(bound.length===1&&s.achievement&&!s.completedAt){
  try{
   const probe=await goalPage(bound[0],s,"probe",s.pending?.marker||"",s.pending?.message||"");
   const current=await goalGet();
   if(probe.stop&&current?.session===s.session&&current?.revision===s.revision){
    if(probe.ownDraft&&s.pending)await goalPage(bound[0],s,"yield",s.pending.marker,s.pending.message);
    current.enabled=false;current.status="completed: "+current.achievement;current.pending=null;current.completedAt=Date.now();
    await goalSet(current);await chrome.alarms.clear(GOAL_ALARM);
   }
  }catch{}
 }
}
chrome.runtime.onInstalled.addListener(()=>goalInit().catch(()=>{}));
chrome.runtime.onStartup.addListener(()=>goalInit().catch(()=>{}));
chrome.alarms.onAlarm.addListener(a=>{if(a.name===GOAL_ALARM)goalTick()});
async function callerURL(sender){
 if(sender.tab)return chatURL(sender.tab.url);
 const [t]=await chrome.tabs.query({active:true,currentWindow:true});return chatURL(t?.url)
}
chrome.runtime.onMessage.addListener((m,sender,reply)=>{
 if(m?.type!=="iclone-goal-control")return;
 (async()=>{
  let s=await goalGet();const url=await callerURL(sender);
  if(!url)return {enabled:false,status:"เปิดบทสนทนา ChatGPT ที่มีงานก่อน"};
  if(m.action==="status")return validFor(s,url)?s:{enabled:false,status:s?.enabled?"กำลังติดตามอีกแชต — พักแชตนั้นก่อน":"พร้อมเริ่มติดตาม"};
  if(m.action==="pause"){
   if(!validFor(s,url))return {enabled:false,status:"ไม่ได้ติดตามแชตนี้"};
   s.enabled=false;s.status="paused";s.revision=(s.revision||0)+1;await goalSet(s);await chrome.alarms.clear(GOAL_ALARM);return s;
  }
  if(m.action==="resume"){
   if(s?.enabled&&!validFor(s,url))return {enabled:false,status:"กำลังติดตามอีกแชต — พักแชตนั้นก่อน"};
   if(!s?.enabled||!validFor(s,url))s=newSession(url,true);
   else{s.next=Date.now();s.status="starting immediately"}
   await goalSet(s);await chrome.alarms.create(GOAL_ALARM,{periodInMinutes:.5});void goalStartNow();return s;
  }
  return s||{enabled:false,status:"พร้อมเริ่มติดตาม"};
 })().then(reply).catch(e=>reply({error:String(e)}));return true
});

async function goalPage(tab,s,op,marker="",message=""){
 const r=await chrome.scripting.executeScript({target:{tabId:tab.id},args:[s.url,op,marker,message,s.achievement,s.session],func:async(url,op,marker,message,achievement,session)=>{
  const vis=e=>!!e&&e.getClientRects().length>0;
  if(location.href.split(/[?#]/)[0]!==url)return {state:"wrong chat"};
  const role=(r)=>Array.from(document.querySelectorAll('[data-message-author-role="'+r+'"],[data-turn="'+r+'"],article[data-role="'+r+'"]'));
  const assistant=role("assistant"),users=role("user");
  const last=assistant.at(-1);
  const answer=last?.innerText?.trim()||"";
  const sig=last?String(last.closest("[data-message-id]")?.getAttribute("data-message-id")||last.getAttribute("data-message-id")||assistant.length)+":"+answer.slice(-500):null;
  // The random achievement belongs to this session, not only the last turn.
  // Never match the user's own prompt, editor, code snippets, or goal panel.
  const userSelector='[data-message-author-role="user"],[data-turn="user"],[data-role="user"],[contenteditable="true"],textarea,input,form,nav,aside,pre,code,#cc5-goal-floating-panel';
  const assistantSelector='[data-message-author-role="assistant"],[data-turn="assistant"],[data-role="assistant"]';
  const exact=t=>String(t||"").replace(/[\u200B-\u200D\uFEFF]/g,"").split(/\r?\n/).some(l=>l.trim()===achievement);
  const hasAchievement=()=>{
   if(!achievement)return false;
   const root=document.querySelector("main")||document.body;
   if(!root)return false;
   // Rich-text blocks retain the line even when the enclosing turn includes UI.
   const candidates=root.querySelectorAll(assistantSelector.split(",").map(sel=>sel+" p,"+sel+" li,"+sel+" div,"+sel+" span").join(","));
   for(const e of candidates){
    if(e.closest(userSelector)||!e.closest(assistantSelector))continue;
    if(Array.from(e.children).some(c=>c.matches("p,li,div,span")))continue;
    if(exact(e.innerText||e.textContent))return true;
   }
   // Alternate ChatGPT layouts: assistant Markdown/prose inside a conversation turn.
   for(const e of root.querySelectorAll('.markdown,.prose,[data-testid="assistant-message"]')){
    if(e.closest(userSelector)||!e.closest('[data-testid^="conversation-turn-"],article,'+assistantSelector))continue;
    if(exact(e.innerText||e.textContent))return true;
   }
   return role("assistant").some(e=>!e.closest(userSelector)&&!e.querySelector("pre,code")&&exact(e.innerText||e.textContent));
  };
  const stop=hasAchievement();
  // Some ChatGPT layouts omit data-message-author-role. Match the unique
  // beginning of the posted prompt in conversation text, not the editor.
  const receipt=()=>{
   if(!marker)return false;
   const norm=t=>String(t||"").replace(/\s+/g," ").trim();
   const expected=norm(message);
   const match=e=>{const t=norm(e.innerText||e.textContent);return t.startsWith(marker)&&(expected?t.startsWith(expected):true)};
   if(role("user").some(match))return true;
   const root=document.querySelector("main")||document.body;
   if(!root)return false;
   const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
   for(let n=w.nextNode();n;n=w.nextNode()){
    if(!n.nodeValue?.includes(marker))continue;
    let e=n.parentElement;
    for(let i=0;e&&i<6;i++,e=e.parentElement){
     if(e===root||e.matches("main,body"))break;
     if(e.closest('[contenteditable="true"],textarea,input,form,#prompt-textarea,[data-message-author-role="assistant"],[data-turn="assistant"],[data-role="assistant"],pre,code,nav,aside,#cc5-goal-floating-panel'))break;
     if(vis(e)&&match(e))return true;
    }
   }
   return false;
  };
  const delivered=receipt();
  const cands=Array.from(document.querySelectorAll('#prompt-textarea,[contenteditable="true"][role="textbox"],textarea[placeholder],textarea[aria-label],div[contenteditable="true"][data-placeholder]')).filter(e=>vis(e)&&!e.closest('[data-message-author-role]')&&!e.disabled);
  const c=cands.find(e=>e.id==="prompt-textarea")||(cands.length===1?cands[0]:null);
  const draft=()=>String(c?.value??c?.innerText??"").trim();
  const busy=()=>Array.from(document.querySelectorAll('[data-testid="stop-button"],button[aria-label="หยุด"],button[aria-label="Stop"],button[aria-label="Stop generating"],button[title="หยุด"],button[aria-label*="End voice"],button[aria-label*="Stop recording"],button[aria-label*="หยุดบันทึก"],button[aria-label*="จบการสนทนาด้วยเสียง"]')).some(vis);
  const attachments=()=>Array.from(document.querySelectorAll('[data-testid="remove-attachment"],button[aria-label*="Remove file"],button[aria-label*="Remove attachment"],button[aria-label^="ลบ "]')).some(e=>vis(e)&&!e.closest('[data-message-author-role]'));
  if(!globalThis.__icPreviewInput){globalThis.__icPreviewInput={last:0};for(const t of ["pointermove","pointerdown","keydown","wheel","touchstart","beforeinput","compositionstart"]){document.addEventListener(t,e=>{if(e.isTrusted)globalThis.__icPreviewInput.last=Date.now()},{capture:true,passive:true})}}
  const snapshot={sig,stop,delivered,assistantCount:assistant.length,busy:busy(),draft:!!draft(),ownDraft:!!message&&draft()===message,attachment:attachments()};
  if(op==="probe")return {...snapshot,state:!c?"composer missing":busy()?"busy":"ready"};
  if(op==="yield"){
   if(!c||!message||draft()!==message||attachments())return {...snapshot,state:"wait"};
   c.focus({preventScroll:true});
   if("value" in c){Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value").set.call(c,"");c.dispatchEvent(new Event("input",{bubbles:true}))}
   else{const sel=window.getSelection();const range=document.createRange();range.selectNodeContents(c);sel.removeAllRanges();sel.addRange(range);document.execCommand("delete",false,null)}
   return {...snapshot,state:draft()?"yield_failed":"yielded"};
  }
  const safe=async()=>!hasAchievement()&&location.href.split(/[?#]/)[0]===url&&c&&c.isConnected&&!busy()&&!attachments()&&(await chrome.runtime.sendMessage({type:"iclone-goal-safe",session})).ok;
  if(stop)return {...snapshot,state:"completed"};
  if(delivered)return {...snapshot,state:"sent"};
  if(!await safe())return {...snapshot,state:"wait"};
  if(draft()&&draft()!==message)return {...snapshot,state:"user draft"};
  if(!draft()){
   c.focus({preventScroll:true});
   if("value" in c){Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value").set.call(c,message);c.dispatchEvent(new Event("input",{bubbles:true}))}
   else document.execCommand("insertText",false,message);
  }
  if(draft()!==message)return {...snapshot,state:"draft unknown"};
  // React mounts/enables Send asynchronously after the input event.
  let button=null;
  for(let i=0;i<50;i++){
   if(hasAchievement())return {...snapshot,ownDraft:draft()===message,state:"completed"};
   if(!await safe()||draft()!==message)return {...snapshot,ownDraft:draft()===message,state:"draft waiting"};
   const buttons=Array.from(document.querySelectorAll('button#composer-submit-button,button[data-testid="send-button"],button[aria-label="ส่ง"],button[aria-label="Send"],button[aria-label="Send prompt"],button[aria-label="Send message"],button[title="ส่ง"],button[title="Send"]')).filter(e=>vis(e)&&!e.disabled&&e.getAttribute("aria-disabled")!=="true"&&!/หยุด|stop/i.test((e.getAttribute("aria-label")||"")+" "+(e.getAttribute("title")||"")));
   if(buttons.length===1){button=buttons[0];break}
   await new Promise(r=>setTimeout(r,200));
  }
  if(hasAchievement())return {...snapshot,ownDraft:draft()===message,state:"completed"};
  if(!button||!await safe()||draft()!==message||!button.isConnected)return {...snapshot,ownDraft:draft()===message,state:"draft waiting"};
  if(hasAchievement())return {...snapshot,ownDraft:draft()===message,state:"completed"};
  button.click();
  for(let i=0;i<24;i++){await new Promise(r=>setTimeout(r,500));if(receipt())return {...snapshot,state:"sent"}}
  return {...snapshot,state:draft()?"send unknown":"submitted unconfirmed"};
 }});
 return r[0]?.result||{state:"unknown"};
}
async function goalStartNow(){
 for(let i=0;i<40&&running;i++)await new Promise(r=>setTimeout(r,250));
 await goalTick(true);
}
async function previewPriority(url){
 try{
  const sr=await req("/sleep/status");if(sr.ok){const ss=await sr.json();if(ss.enabled&&(ss.phase!=="work"||ss.url!==url))return {wait:true,status:"Sleep Mode handoff"};}
  const r=await req("/status");if(!r.ok)return {wait:false,unavailable:true};
  const x=await r.json(),j=x.job||{};
  if(j.url===url&&["pending","claimed","needs_review"].includes(j.state))return {wait:true,job:j,status:j.state==="needs_review"?"รอยืนยันภาพพรีวิว — ยังไม่ส่งข้อความติดตาม":"รอส่งภาพพรีวิวก่อน"};
  if(x.generating&&x.bound?.url===url)return {wait:true,status:"iClone กำลังสร้างภาพพรีวิว"};
  return {wait:false};
 }catch{return {wait:false,unavailable:true}}
}
async function goalTick(manual=false){
 if(running)return;running=true;
 let s;
 try{
  s=await goalGet();if(!s?.enabled)return;
  const tabs=(await chrome.tabs.query({url:"https://chatgpt.com/*"})).filter(t=>t.url&&chatURL(t.url)===s.url);
  if(tabs.length!==1){s.status="waiting: bound chat not unique";return}
  const tab=tabs[0];
  const probe=await goalPage(tab,s,"probe",s.pending?.marker||"",s.pending?.message||"");

  if(probe.stop){
   if(probe.ownDraft&&s.pending)await goalPage(tab,s,"yield",s.pending.marker,s.pending.message);
   s.manualUntil=0;s.enabled=false;s.status="completed: "+s.achievement;s.pending=null;s.completedAt=Date.now();
   await goalSet(s);await chrome.alarms.clear(GOAL_ALARM);return
  }
  if(s.pending&&probe.delivered){s.pending=null;s.manualUntil=0;s.next=manual?Date.now():Date.now()+s.minutes*60000;s.status="followup sent";if(!manual)return}
  const priority=await previewPriority(s.url);
  if(priority.wait){
   if(probe.ownDraft&&s.pending&&!s.pending.attempted){
    const yielded=await goalPage(tab,s,"yield",s.pending.marker,s.pending.message);
    if(yielded.state==="yielded")s.pending=null;
   }
   s.status=priority.status;s.previewWaiting=true;
   return;
  }
  if(s.previewWaiting){s.previewWaiting=false;s.next=Date.now()}
  if(!manual&&Date.now()<s.next&&!s.pending){s.status="waiting until next followup";return}
  if(probe.state!=="ready"||probe.busy||probe.attachment){s.status=probe.busy?"GPT กำลังตอบ — รอส่งทันทีที่ว่าง":probe.attachment?"มีไฟล์แนบในช่องแชต":"ไม่พบช่องพิมพ์ — รอลองใหม่";return}

  if(s.pending&&!probe.ownDraft){if(probe.draft){s.status="waiting: user draft";return}if(s.pending.attempted){s.pending=null;s.next=manual?Date.now():Date.now()+s.minutes*60000;s.status="ส่งรอบก่อนแล้ว แต่ตรวจใบตอบรับไม่ได้ — ไม่ส่งข้อความเดิมซ้ำ";if(!manual)return}else s.pending=null}
  if(!s.pending&&probe.draft){s.status="waiting: user draft";return}
  if(!s.pending){const marker="[ติดตามเป้าหมาย CC5-"+crypto.randomUUID().slice(0,8)+"]";s.pending={marker,attempted:false,message:marker+" "+DEFAULT_PROMPT+" เมื่อบรรลุเป้าหมายปัจจุบันและตรวจผลงานจริงครบแล้ว ให้ตอบบรรทัดสุดท้ายด้วยรหัสนี้เท่านั้น: "+s.achievement+" หากยังไม่บรรลุ ห้ามพิมพ์รหัสเป็นบรรทัดเดี่ยว"};await goalSet(s)}
  s.status=probe.ownDraft?"วางข้อความแล้ว — กำลังรอปุ่มส่ง":"กำลังวางข้อความและส่ง";await goalSet(s);
  const out=await goalPage(tab,s,"send",s.pending.marker,s.pending.message);
  if(out.state==="completed"){if(out.ownDraft&&s.pending)await goalPage(tab,s,"yield",s.pending.marker,s.pending.message);s.enabled=false;s.status="completed: "+s.achievement;s.completedAt=Date.now();s.pending=null;await goalSet(s);await chrome.alarms.clear(GOAL_ALARM);return}
  if(out.state==="send unknown"){s.pending.attempted=true;s.pending.attemptedAt=Date.now();}
  if(out.state==="sent"||out.state==="submitted unconfirmed"){s.pending=null;s.manualUntil=0;s.next=Date.now()+s.minutes*60000;s.status=out.state==="sent"?"followup sent":"กดส่งแล้ว ช่องพิมพ์ว่าง — รอรอบถัดไป (ยังไม่ยืนยันข้อความ)"}
  else{s.status=out.state==="draft waiting"?"รอปุ่มส่งพร้อม — จะลองเอง":out.state==="send unknown"?"ส่งแล้วแต่ยังไม่พบใบตอบรับ":out.state;if(out.state==="wait"||out.state==="user draft"){if(!out.ownDraft)s.pending=null}}
 }catch(e){if(s)s.status="error: "+String(e).slice(0,180)}
 finally{try{if(s){const current=await goalGet();if(current?.session===s.session&&current?.revision===s.revision){await goalSet(s)}}}finally{running=false}}
}
goalInit().catch(()=>{});
chrome.runtime.onMessage.addListener((m,sender,reply)=>{
 if(!["iclone-goal-safe","iclone-goal-ready","iclone-achievement-observed"].includes(m?.type))return;
 (async()=>{
  const s=await goalGet(),url=chatURL(sender.tab?.url);
  const ok=!!s?.enabled&&validFor(s,url);
  if(m.type==="iclone-goal-safe"){const p=ok?await previewPriority(url):{wait:false};const current=await goalGet();reply({ok:ok&&current?.enabled&&current.session===m.session&&validFor(current,url)&&!p.wait});return}
  if(ok&&!running){const p=await previewPriority(url);if(p.wait&&p.job){await deliver()}if(!running)void goalTick()}
  reply({ok});
 })().catch(()=>reply({ok:false}));return true
});
