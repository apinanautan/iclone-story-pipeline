/* Generic context-driven follow-up, one explicitly selected chat at a time. */
const GOAL_KEY="icloneGoalTracker";
const GOAL_ALARM="iclone-goal-followup";
const LEGACY_URL=null;
const FOLLOWUP_PROMPTS=["ตรวจเป้าหมายล่าสุดของผู้ใช้และสถานะจริง แล้วลงมือทำขั้นที่ยังไม่เสร็จทันที ใช้เครื่องมือจริง ไม่ย้อนทำงานที่ผู้ใช้เปลี่ยนเป้าหมายแล้ว", "ทบทวนผลการลงมือครั้งก่อน ถ้าไม่มีความคืบหน้า ให้ค้นสาเหตุจากข้อผิดพลาดและหลักฐาน แล้วแก้ด้วยวิธีที่แตกต่างจากเดิม", "เลือกขั้นตอนที่สร้างความคืบหน้าได้จริงที่สุดจากเป้าหมายปัจจุบัน ลงมือทำ ตรวจผล แล้วทำขั้นถัดไปที่ได้รับอนุญาต ไม่ตอบเพียงว่าจะทำ", "ตรวจว่ากำลังยึดข้อมูลเก่า ไฟล์ผิด งานผิด หรือเป้าหมายผิดหรือไม่ ให้คำสั่งจริงล่าสุดของผู้ใช้เหนือบริบทเก่า แก้ความไม่ตรงกันก่อนลงมือ", "ตรวจความพร้อมของเครื่องมือ หากวิธีเดิมล้มเหลว ให้ใช้ทางเลือกที่รองรับและได้รับอนุญาตจริง ไม่ลองคำสั่งเดิมแบบไร้หลักฐาน", "แยกสิ่งที่สำเร็จแล้วออกจากสิ่งที่ยังติด ห้ามเริ่มงานที่เสร็จแล้วใหม่โดยพลการ แก้เฉพาะส่วนที่ทำให้เป้าหมายปัจจุบันเดินหน้าต่อไม่ได้", "ใช้หลักฐานจากผลลัพธ์จริงเพื่อตัดสินขั้นถัดไป อ่านรายละเอียดข้อผิดพลาด แก้ต้นเหตุ ทดสอบเฉพาะจุด แล้วตรวจความคืบหน้าจริง", "หยุดวงจรการคิดหรือรายงานซ้ำโดยไม่มีการเปลี่ยนแปลง เลือกการกระทำที่ทำได้จริงและไม่ซ้ำวิธีที่เพิ่งล้มเหลว ตรวจผลก่อนดำเนินต่อ", "ประเมินงานค้างกับเป้าหมายล่าสุดใหม่โดยไม่เปลี่ยนขอบเขตเอง ทำงานที่ไม่ติดเงื่อนไขได้ก่อนอย่างปลอดภัย แก้อุปสรรคที่จำเป็น", "ตรวจผลลัพธ์เทียบกับสิ่งที่ผู้ใช้ต้องการ ถ้ายังขาดให้แก้จุดนั้นด้วยเครื่องมือจริง ถ้าติดข้อจำกัดที่แก้ไม่ได้ให้ระบุข้อจำกัดเฉพาะและหยุดการวนซ้ำ"];
const FOLLOWUP_RULES=" ยึดคำสั่งจริงล่าสุดของผู้ใช้ ไม่ตีความข้อความติดตามว่าเป็นคำสั่งเปลี่ยนเป้าหมาย ห้ามข้ามจุดรออนุมัติหรือข้อจำกัด ห้ามอ้างว่าสำเร็จโดยไม่มีหลักฐาน หากติดจริงให้บอกเฉพาะสิ่งที่ติด ไม่ทำซ้ำโดยไม่เปลี่ยนวิธี ข้อความติดตามนี้เป็นคำสั่งให้ AI ลงมือทำงานต่อเองตามสิทธิ์และขอบเขตที่ผู้ใช้ให้ไว้ ไม่ใช่คำสั่งให้ผู้ใช้ลงมือแทน ห้ามโยนคำสั่ง CLI/PowerShell/Python การพิมพ์ข้อความ การกดปุ่ม หรือขั้นตอนแก้ไขกลับไปให้ผู้ใช้ทำ หากมีเครื่องมือที่ทำได้ ให้เรียกใช้เอง ตรวจผลจริง แล้วทำขั้นถัดไปทันที ไม่ต้องขอให้ผู้ใช้พิมพ์ ลองใหม่ หรืออนุญาตซ้ำสำหรับการแก้ไขและลองใหม่ที่อยู่ในขอบเขตเดิม เมื่อเจอข้อผิดพลาดให้แก้ต้นเหตุหรือเลือกวิธีที่ได้รับอนุญาตแตกต่างจากเดิมก่อนลองใหม่ ไม่วนคำสั่งเดิมที่ไม่เกิดผล ขอผู้ใช้เฉพาะการอนุมัติที่จำเป็นจริง การให้สิทธิ์ที่เครื่องมือกำหนด หรือข้อมูลที่หาเองไม่ได้; หากทำไม่ได้จริงให้แจ้งข้อจำกัดที่พิสูจน์แล้ว ไม่อ้างว่างานสำเร็จ หลักทำงานแบบเดินหน้า: ขั้นตอนที่ลงมือเสร็จและตรวจผ่านแล้วถือว่าจบ ให้เก็บผลงานและหลักฐานเดิม ห้ามย้อนทำซ้ำ เซฟซ้ำ เรนเดอร์ซ้ำ หรือรีเซ็ตสถานะผ่านเพื่อเริ่มใหม่โดยไม่มีเหตุผลจากหลักฐานจริง. เมื่อพบข้อผิดพลาด ให้ระบุจุดที่เสียจากผลจริง แก้เฉพาะจุดนั้นและตรวจซ้ำเฉพาะส่วนที่ได้รับผลกระทบโดยตรงตาม dependency ของ validator. รักษาส่วนอื่นที่ผ่านแล้ว ไม่รื้อทั้งงานหรือย้อนท่อนเก่า. เมื่อแก้ผ่านให้เดินหน้าจากขั้นที่ยังไม่เสร็จทันที. หากผู้ใช้สั่งเปลี่ยนงานให้ยึดคำสั่งล่าสุด ห้ามปลอมผลผ่านหรือข้ามจุดอนุมัติจริง. จำนวนรอบติดตามที่ส่งไปไม่ใช่เหตุผลให้หยุดงาน หากมีขั้นที่ล้มเหลว ให้ตรวจหลักฐานและแก้เฉพาะจุดนั้นเองด้วยวิธีที่ต่างจากที่ล้มเหลว ไม่ย้อนทำส่วนที่ผ่านแล้ว. ถ้าไม่มีวิธีที่ปลอดภัยหรือมีจุดอนุมัติจริง ให้ระบุข้อจำกัดนั้นอย่างชัดเจนและอย่าลองวิธีเดิมซ้ำ.";
async function nextFollowup(){
 const k="icloneFollowupCursor",o=await chrome.storage.local.get(k);
 const i=(Number.isInteger(o[k])&&o[k]>=0?o[k]:0)%FOLLOWUP_PROMPTS.length;
 await chrome.storage.local.set({[k]:(i+1)%FOLLOWUP_PROMPTS.length});
 return FOLLOWUP_PROMPTS[i]+FOLLOWUP_RULES;
}

const chatURL=x=>{try{const u=new URL(x);return u.origin==="https://chatgpt.com"&&/\/c\/[a-zA-Z0-9-]+\/?$/.test(u.pathname)?u.origin+u.pathname.replace(/\/$/,""):null}catch{return null}};
const goalGet=async()=>{const o=await chrome.storage.local.get(GOAL_KEY);return o[GOAL_KEY]||null};
const goalSet=async(s)=>{await chrome.storage.local.set({[GOAL_KEY]:s})};
const newSession=(url,enabled=false)=>({schema:2,url,session:crypto.randomUUID(),achievement:"ACHIEVEMENT: "+crypto.randomUUID().slice(0,12).toUpperCase(),enabled,mode:"manual",minutes:0.5,next:Date.now(),pending:null,status:enabled?"starting immediately":"paused"});
const validFor=(s,url)=>s?.url===url;
// Explicit stop signal, fail-open if the local relay is down; no Preview dependency.
let directStopBusy=null;
async function signalCall(path,body){
 const r=await fetch(BASE+path,{method:"POST",headers:{"X-Preview-Key":KEY,"Content-Type":"application/json"},body:JSON.stringify(body),cache:"no-store",signal:AbortSignal.timeout(700)});
 if(!r.ok)throw Error("stop mailbox "+r.status);
 return r.json();
}
async function directStop(s){
 if(!s?.achievement||!s.url)return false;
 if(directStopBusy){await directStopBusy;const cur=await goalGet();return cur?.session!==s.session||!cur?.enabled;}
 const task=(async()=>{
  try{
   const d=await signalCall("/goal/signal",{code:s.achievement});
   if(!["requested","stopped"].includes(d.state))return false;
   let cur=await goalGet();
   if(cur?.session!==s.session||cur.achievement!==s.achievement)return false;
   if(cur.enabled){
    if(cur.pending&&!cur.pending.attempted){
     try{const tabs=(await chrome.tabs.query({url:"https://chatgpt.com/*"})).filter(t=>chatURL(t.url)===cur.url);
      if(tabs.length===1)await goalPage(tabs[0],cur,"yield",cur.pending.marker,cur.pending.message)}catch{}
    }
    const latest=await goalGet();
    if(latest?.session!==cur.session||latest.achievement!==cur.achievement)return false;
    cur=latest;cur.enabled=false;cur.revision=(cur.revision||0)+1;cur.status="completed by local script: "+cur.achievement;cur.completedAt=Date.now();cur.pending=null;cur.next=0;
    await goalSet(cur);await chrome.alarms.clear(GOAL_ALARM);
   }
   const verified=await goalGet();
   if(verified?.session!==s.session||verified.enabled)return false;
   if(await chrome.alarms.get(GOAL_ALARM))await chrome.alarms.clear(GOAL_ALARM);
   if(await chrome.alarms.get(GOAL_ALARM))return false;
   if(d.state==="requested")await signalCall("/goal/signal-ack",{code:s.achievement,id:d.id,session:s.session});
   return true;
  }catch{return false}
 })();
 directStopBusy=task;
 try{return await task}finally{if(directStopBusy===task)directStopBusy=null}
}
async function relayGoal(s,path="/goal/check",extra={}){
 if(!s?.enabled||!s.url)return false;
 if(await directStop(s))return true;
 if(s.mode!=="sleep")return false;
 let g;
 try{const r=await req(path,{url:s.url,...extra});if(!r.ok)throw Error("HTTP "+r.status);g=await r.json()}
 catch(e){g={wait:true,reason:"Relay unavailable; no follow-up sent"}}
 if(!g.stop&&!g.wait)return false;
 const cur=await goalGet();
 if(cur?.session!==s.session||!cur.enabled)return true;
 if(g.stop){
   // Stop state wins over in-flight timer callbacks.
   if(cur.pending&&!cur.pending.attempted){
    try{const tabs=(await chrome.tabs.query({url:"https://chatgpt.com/*"})).filter(t=>chatURL(t.url)===cur.url);
     if(tabs.length===1)await goalPage(tabs[0],cur,"yield",cur.pending.marker,cur.pending.message)}catch{}
   }
   const latest=await goalGet();if(latest?.session!==cur.session||!latest.enabled)return true;
   latest.enabled=false;latest.revision=(latest.revision||0)+1;latest.status="หยุดติดตาม — "+g.reason;latest.pending=null;latest.next=0;
   await goalSet(latest);await chrome.alarms.clear(GOAL_ALARM);
 }else{
   cur.status="รอ — "+g.reason;await goalSet(cur);
 }
 return true;
}
async function stopFromRelay(s){return relayGoal(s)}
async function goalInit(){
 let s=await goalGet();
 if(s?.schema!==2){const old=s;s=newSession(LEGACY_URL,false);s.next=old?.next||Date.now();await goalSet(s)}
 if(s.minutes!==0.5){const old=Number(s.minutes)||3;if(s.enabled&&s.next>Date.now())s.next=Math.max(Date.now(),s.next+(0.5-old)*60000);s.minutes=0.5;await goalSet(s)}
 if(!s.mode){
  // Migrate old sessions once, preserving an explicitly enabled Sleep session.
  let mode="manual";
  try{const r=await req("/sleep/status");if(r.ok){const ss=await r.json();if(ss.enabled&&ss.url===s.url)mode="sleep"}}catch{}
  const cur=await goalGet();
  if(cur?.session===s.session&&cur.revision===s.revision){s=cur;s.mode=mode;await goalSet(s)}
 }
 if(s.mode==="manual"&&!s.enabled&&s.url&&!s.completedAt&&String(s.status||"").startsWith("หยุดติดตาม — Preview unchanged after two follow-ups;")){
  const cur=await goalGet();
  if(cur?.session===s.session&&cur.revision===s.revision&&cur.status===s.status){
   s.enabled=true;s.next=Date.now();s.status="waiting until next followup";s.pending=null;s.revision=(s.revision||0)+1;await goalSet(s);
  }
 }
 if(await directStop(s)||await stopFromRelay(s))s=await goalGet();
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
    current.revision=(current.revision||0)+1;current.enabled=false;current.status="completed: "+current.achievement;current.pending=null;current.completedAt=Date.now();
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
  if(m.action==="status"){if(validFor(s,url)&&(s.enabled?await stopFromRelay(s):await directStop(s)))s=await goalGet();return validFor(s,url)?s:{enabled:false,status:s?.enabled?"กำลังติดตามอีกแชต — พักแชตนั้นก่อน":"พร้อมเริ่มติดตาม"};}
  if(m.action==="pause"){
   if(!validFor(s,url))return {enabled:false,status:"ไม่ได้ติดตามแชตนี้"};
   s.enabled=false;s.status="paused";s.revision=(s.revision||0)+1;await goalSet(s);await chrome.alarms.clear(GOAL_ALARM);return s;
  }
  if(m.action==="resume"){
   if(s?.enabled&&!validFor(s,url))return {enabled:false,status:"กำลังติดตามอีกแชต — พักแชตนั้นก่อน"};
   if(s?.mode==="sleep"&&s.enabled)return s; // Sleep has its own controls; manual tracking never depends on Relay.
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
  // Match a complete standalone line only in an actual assistant turn.
  // Different ChatGPT layouts put the role on either the message or its ancestor.
  const excluded='[data-message-author-role="user"],[data-turn="user"],[data-role="user"],[contenteditable="true"],textarea,input,nav,aside,pre,code,#cc5-goal-floating-panel,[hidden],[aria-hidden="true"]';
  const roles='[data-message-author-role],[data-turn],[data-role]';
  const assistantSelector='[data-message-author-role="assistant"],[data-turn="assistant"],[data-role="assistant"],[data-testid="assistant-message"]';
  const normalize=t=>String(t??"").normalize("NFKC").replace(/[\u200B-\u200F\u202A-\u202E\u2060-\u206F\uFEFF]/g,"").replace(/[\u2010-\u2015\u2212]/g,"-").trim();
  const exact=t=>String(t??"").split(/\r?\n/).some(l=>normalize(l)===normalize(achievement));
  const isAssistant=e=>{
   if(e.closest(excluded))return false;
   const owner=e.closest(roles);
   if(owner&&["user","system","tool"].some(x=>[owner.getAttribute("data-message-author-role"),owner.getAttribute("data-turn"),owner.getAttribute("data-role")].includes(x)))return false;
   if(e.closest(assistantSelector))return true;
   const turn=e.closest('[data-testid^="conversation-turn-"],article');
   if(!turn)return false;
   const headings=[...turn.querySelectorAll('h1,h2,h3,h4,h5,h6,[role="heading"]')];
   return headings.some(h=>/^(ChatGPT (said|says):?|ChatGPT กล่าว(?:ว่า)?[:：]?|ChatGPT พูดว่า[:：]?)$/i.test(normalize(h.textContent)))&&!headings.some(h=>/^(You said:?|คุณพูดว่า[:：]?|คุณกล่าวว่า[:：]?)$/i.test(normalize(h.textContent)));
  };
  const hasAchievement=()=>{
   if(!achievement)return false;
   // Do not depend on a particular main container, markdown class or leaf layout.
   const nodes=document.querySelectorAll(assistantSelector+', [data-testid^="conversation-turn-"] p, article p, .markdown p, .prose p, [data-testid^="conversation-turn-"] li, article li, [data-testid^="conversation-turn-"] div, article div');
   for(const e of nodes){
    if(!isAssistant(e)||e.querySelector(excluded))continue;
    // innerText preserves line breaks; textContent covers split inline spans.
    if(exact(e.innerText)||exact(e.textContent))return true;
   }
   // A role container may contain controls/code; inspect its individual blocks instead.
   for(const owner of document.querySelectorAll(assistantSelector)){
    if(!isAssistant(owner))continue;
    for(const e of owner.querySelectorAll('p,li,div,blockquote')){
     if(isAssistant(e)&&!e.querySelector(excluded)&&(exact(e.innerText)||exact(e.textContent)))return true;
    }
   }
   return false;
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
  for(let i=0;i<24;i++){await new Promise(r=>setTimeout(r,500));if(hasAchievement())return {...snapshot,state:"completed"};if(receipt())return {...snapshot,state:"sent"}}
  return {...snapshot,state:draft()?"send unknown":"submitted unconfirmed"};
 }});
 return r[0]?.result||{state:"unknown"};
}
async function goalStartNow(){
 for(let i=0;i<40&&running;i++)await new Promise(r=>setTimeout(r,250));
 await goalTick(true);
}
async function previewPriority(url,mode){
 // A preview for this exact conversation must precede follow-up text in BOTH modes.
 // Unbound manual chats still work independently of Preview and Relay.
 try{
  if(mode==="sleep"){const sr=await req("/sleep/status");if(sr.ok){const ss=await sr.json();if(ss.enabled&&(ss.phase!=="work"||ss.url!==url))return {wait:true,status:"Sleep Mode handoff"};}}
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
  s=await goalGet();if(!s?.enabled||await stopFromRelay(s))return;
  const tabs=(await chrome.tabs.query({url:"https://chatgpt.com/*"})).filter(t=>t.url&&chatURL(t.url)===s.url);
  if(tabs.length!==1){s.status="waiting: bound chat not unique";return}
  const tab=tabs[0];
  const probe=await goalPage(tab,s,"probe",s.pending?.marker||"",s.pending?.message||"");

  if(probe.stop){
   if(probe.ownDraft&&s.pending)await goalPage(tab,s,"yield",s.pending.marker,s.pending.message);
   s.revision=(s.revision||0)+1;s.manualUntil=0;s.enabled=false;s.status="completed: "+s.achievement;s.pending=null;s.completedAt=Date.now();
   await goalSet(s);await chrome.alarms.clear(GOAL_ALARM);return
  }
  if(s.pending&&probe.delivered){s.pending=null;s.manualUntil=0;s.next=manual?Date.now():Date.now()+s.minutes*60000;s.status="followup sent";if(!manual)return}
  const priority=await previewPriority(s.url,s.mode);
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
  if(!s.pending){const marker="[ติดตามเป้าหมาย CC5-"+crypto.randomUUID().slice(0,8)+"]";s.pending={marker,attempted:false,message:marker+" "+(await nextFollowup())+" เมื่อบรรลุเป้าหมายและตรวจผลจริงครบแล้ว ให้ใช้เครื่องมือควบคุมคอมพิวเตอร์ที่เชื่อมอยู่ค้นหาโฟลเดอร์ iClone Story Pipeline แล้วเรียก py -3 -B tools/chrome_preview_bridge/goal_signal.py "+s.achievement.split(": ")[1]+" ด้วยตัวเอง (ไม่ให้ผู้ใช้รัน). ตรวจผล state=stopped ซึ่งเป็นใบตอบรับจากส่วนขยายจริง ไม่ใช่แค่เขียนไฟล์. หากไม่มีใบตอบรับ ห้ามอ้างว่าหยุดแล้ว ให้ตรวจ Relay/เครื่องมือและแก้เฉพาะจุดที่ติด. จากนั้นตอบบรรทัดสุดท้ายด้วยรหัสนี้: "+s.achievement+" หากยังไม่บรรลุ ห้ามเรียกสคริปต์หยุดหรือพิมพ์รหัสเป็นบรรทัดเดี่ยว"};const current=await goalGet();if(!current?.enabled||current.session!==s.session||current.revision!==s.revision)return;await goalSet(s)}
  if(await relayGoal(s,"/goal/attempt",{session:s.session,marker:s.pending.marker}))return;
  const latest=await goalGet();if(!latest?.enabled||latest.session!==s.session||latest.revision!==s.revision||latest.completedAt)return;
  s.status=probe.ownDraft?"วางข้อความแล้ว — กำลังรอปุ่มส่ง":"กำลังวางข้อความและส่ง";await goalSet(s);
  const out=await goalPage(tab,s,"send",s.pending.marker,s.pending.message);
  if(out.state==="completed"){if(out.ownDraft&&s.pending)await goalPage(tab,s,"yield",s.pending.marker,s.pending.message);s.revision=(s.revision||0)+1;s.enabled=false;s.status="completed: "+s.achievement;s.completedAt=Date.now();s.pending=null;await goalSet(s);await chrome.alarms.clear(GOAL_ALARM);return}
  if(out.state==="send unknown"){s.pending.attempted=true;s.pending.attemptedAt=Date.now();}
  if(out.state==="sent"||out.state==="submitted unconfirmed"){s.pending=null;s.manualUntil=0;s.next=Date.now()+s.minutes*60000;s.status=out.state==="sent"?"followup sent":"กดส่งแล้ว ช่องพิมพ์ว่าง — รอรอบถัดไป (ยังไม่ยืนยันข้อความ)"}
  else{s.status=out.state==="draft waiting"?"รอปุ่มส่งพร้อม — จะลองเอง":out.state==="send unknown"?"ส่งแล้วแต่ยังไม่พบใบตอบรับ":out.state;if(out.state==="wait"||out.state==="user draft"){if(!out.ownDraft)s.pending=null}}
 }catch(e){if(s)s.status="error: "+String(e).slice(0,180)}
 finally{try{if(s){const current=await goalGet();if(current?.session===s.session&&current?.revision===s.revision&&!current.completedAt){await goalSet(s)}}}finally{running=false}}
}
goalInit().catch(()=>{});
chrome.runtime.onMessage.addListener((m,sender,reply)=>{
 if(!["iclone-goal-safe","iclone-goal-ready","iclone-achievement-observed"].includes(m?.type))return;
 (async()=>{
  const s=await goalGet(),url=chatURL(sender.tab?.url);
  const ok=!!s?.enabled&&validFor(s,url);
  if(m.type==="iclone-goal-safe"){if(ok&&await stopFromRelay(s)){reply({ok:false});return}const p=ok?await previewPriority(url,s.mode):{wait:false};const current=await goalGet();reply({ok:ok&&current?.enabled&&current.session===m.session&&validFor(current,url)&&!p.wait});return}
  if(ok&&!running){const p=await previewPriority(url,s.mode);if(p.wait&&p.job){await deliver()}if(!running)void goalTick()}
  reply({ok});
 })().catch(()=>reply({ok:false}));return true
});
