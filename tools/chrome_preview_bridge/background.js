importScripts("config.local.js");
const BASE="http://127.0.0.1:18764";
const KEY=LOCAL_PREVIEW_KEY;
const IDLE_SECONDS=15;
let running=false;
const req=(path,body)=>fetch(BASE+path,{cache:"no-store",headers:{"X-Preview-Key":KEY,"Content-Type":"application/json"},...(body?{method:"POST",body:JSON.stringify(body)}:{})});
async function change(j,phase){const r=await req("/stage",{id:j.id,phase});if(!r.ok)throw Error("phase rejected "+phase)}
async function note(j,result){await req("/diagnostic",{id:j.id,result})}
async function receipt(j,state,result){await req("/receipt",{id:j.id,state,result})}
async function idle(){return await chrome.idle.queryState(IDLE_SECONDS)==="idle"}
function start(){chrome.alarms.create("iclone-preview",{periodInMinutes:0.5});selfUpdate();deliver()}
// The relay copies newer files into this folder; reload once per new version (no manual reload, no loop).
async function selfUpdate(){try{
 const own=chrome.runtime.getManifest().version,v=(await (await req("/ext/version?have="+encodeURIComponent(own))).json()).version;
 const cmp=(a,b)=>{a=String(a).split(".").map(Number);b=String(b).split(".").map(Number);for(let i=0;i<Math.max(a.length,b.length);i++){if((a[i]||0)!==(b[i]||0))return (a[i]||0)-(b[i]||0)}return 0},newer=cmp(v,own)>0;
 const k="icloneReloadedFor";if(!newer||(await chrome.storage.local.get(k))[k]===v)return;
 await chrome.storage.local.set({[k]:v});chrome.runtime.reload();
}catch{}}
chrome.runtime.onInstalled.addListener(start);
chrome.runtime.onStartup.addListener(start);
chrome.alarms.onAlarm.addListener(a=>{if(a.name==="iclone-preview"){selfUpdate();deliver()}});
chrome.idle.setDetectionInterval(IDLE_SECONDS);
chrome.idle.onStateChanged.addListener(s=>{if(s==="idle")deliver()});
chrome.runtime.onMessage.addListener((m,s,reply)=>{if(m?.type==="iclone-idle"){idle().then(ok=>reply({ok})).catch(()=>reply({ok:false}));return true}});
async function page(tab,j,op,bytes=[]){
 const r=await chrome.scripting.executeScript({target:{tabId:tab.id},args:[j.url,j.id,j.kind,op,bytes,!!j.sleep],func:async(url,id,kind,op,bytes,sleepMode)=>{
  const name="iclone-preview-"+id.slice(0,8)+".jpg", marker="[iClone Preview "+id.slice(0,8)+"]";
  const message=marker+(kind==="scene_review"?" สำรวจฉากจริงจากภาพนี้ อ่าน scene_manifest และตรวจภาพต้นฉบับทั้งหมด วิเคราะห์มุมฉาก พร็อพที่ขาด และ blocking ก่อนวางแผนกล้องรอบสอง รักษา approval ตามโหมด":sleepMode?" ตรวจภาพจริงตามขั้น Preview และ Sleep Mode ที่ได้รับอนุญาต แก้ข้อผิดพลาดและตรวจซ้ำก่อนใช้ sleep-approve ห้ามข้าม QA":kind==="test"?" ทดสอบระบบจับภาพ iClone และส่งเข้าแชตอัตโนมัติหนึ่งครั้ง ตรวจว่าภาพมาถึงแล้วเท่านั้น ไม่ต้องส่งซ้ำหรือเริ่มงานใหม่":kind==="screen_review"?" ตรวจภาพหน้าต่าง iClone จริงเพื่อวิเคราะห์งานหรือปัญหาปัจจุบัน แก้เฉพาะส่วนที่จำเป็น ห้ามเรนเดอร์ก่อนอนุมัติ":" ตรวจภาพพรีวิวของท่อนปัจจุบันตามบทและกฎงาน แก้ต่อถ้ายังไม่ผ่าน ห้ามเรนเดอร์ก่อนอนุมัติ");
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  if(!globalThis.__icPreviewInput){globalThis.__icPreviewInput={last:0};for(const t of ["pointermove","pointerdown","keydown","wheel","touchstart","beforeinput","compositionstart"]){document.addEventListener(t,e=>{if(e.isTrusted)globalThis.__icPreviewInput.last=Date.now()},{capture:true,passive:true})}}
  const visible=e=>e&&e.getClientRects().length>0;
  const candidates=Array.from(document.querySelectorAll('#prompt-textarea,[contenteditable="true"][role="textbox"],textarea[placeholder],textarea[aria-label],div[contenteditable="true"][data-placeholder]')).filter(e=>visible(e)&&!e.closest('[data-message-author-role]')&&!e.disabled);
  const c=candidates.find(e=>e.id==="prompt-textarea")||(candidates.length===1?candidates[0]:null);
  const draft=()=>String(c?.value??c?.innerText??"").trim();
  const seen=()=>{
   const norm=t=>String(t||"").replace(/\s+/g," ").trim();
   const match=e=>norm(e.innerText||e.textContent).startsWith(norm(message));
   if(Array.from(document.querySelectorAll('[data-message-author-role="user"],[data-turn="user"],article[data-role="user"]')).some(match))return true;
   const root=document.querySelector("main")||document.body;
   if(!root)return false;
   const w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);
   for(let n=w.nextNode();n;n=w.nextNode()){
    if(!n.nodeValue?.includes(marker))continue;
    for(let e=n.parentElement,i=0;e&&e!==root&&i<6;e=e.parentElement,i++){
     if(e.closest('[contenteditable="true"],textarea,input,form,#prompt-textarea,[data-message-author-role="assistant"],[data-turn="assistant"],[data-role="assistant"],pre,code,nav,aside,#cc5-goal-floating-panel'))break;
     if(visible(e)&&match(e))return true;
    }
   }
   return false;
  };
  const own=()=>Array.from(document.querySelectorAll("[title],[aria-label],img")).some(e=>visible(e)&&!e.closest('[data-message-author-role]')&&[e.title,e.getAttribute("aria-label"),e.getAttribute("alt")].some(v=>v&&v.includes(name)));
  const foreign=()=>Array.from(document.querySelectorAll('[data-testid="remove-attachment"],button[aria-label*="Remove file"],button[aria-label*="Remove attachment"],button[aria-label^="ลบ "]')).some(e=>visible(e)&&!e.closest('[data-message-author-role]')&&!(e.getAttribute("aria-label")||"").includes(name));
  const busy=()=>Array.from(document.querySelectorAll('[data-testid="stop-button"],button[aria-label="หยุด"],button[aria-label="Stop"],button[aria-label="Stop generating"],button[title="หยุด"],button[aria-label*="End voice"],button[aria-label*="Stop recording"],button[aria-label*="หยุดบันทึก"],button[aria-label*="จบการสนทนาด้วยเสียง"]')).some(visible);
  const safe=async()=>location.href.split(/[?#]/)[0]===url&&c&&c.isConnected&&!busy()&&!foreign()&&Date.now()-globalThis.__icPreviewInput.last>3000&&(await chrome.runtime.sendMessage({type:"iclone-idle"})).ok;
  if(location.href.split(/[?#]/)[0]!==url)return "wrong_chat";
  if(seen())return "sent";
  if(!c)return "composer_missing";
  if(op==="probe"){
   if(busy())return "busy";
   if(foreign())return "other_attachment";
   if(own()&&draft()===message)return "drafted";
   if(own()&&!draft())return "attached";
   if(!own()&&!draft())return "empty";
   return "user_draft";
  }
  if(!await safe())return "wait";
  if(op==="attach"){
   if(draft()||own())return "wait";
   const input=Array.from(document.querySelectorAll("input[type=file]")).find(e=>!e.disabled&&(!e.accept||/image|\*/.test(e.accept)));
   const dt=new DataTransfer();dt.items.add(new File([new Uint8Array(bytes)],name,{type:"image/jpeg"}));
   if(input){input.files=dt.files;input.dispatchEvent(new Event("change",{bubbles:true}))}else c.dispatchEvent(new ClipboardEvent("paste",{clipboardData:dt,bubbles:true,cancelable:true}));
   for(let k=0;k<40;k++){await sleep(500);if(own())return "attached";if(seen())return "sent"}
   return "attachment_unknown";
  }
  if(op==="draft"){
   if(!own()||draft())return "wait";
   c.focus({preventScroll:true});
   if("value" in c){Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype,"value").set.call(c,message);c.dispatchEvent(new Event("input",{bubbles:true}))}
   else document.execCommand("insertText",false,message);
   return draft()===message?"drafted":"draft_unknown";
  }
  if(op==="send"){
   if(!own()||draft()!==message)return "wait";
   const selector='button#composer-submit-button,button[data-testid="send-button"],button[aria-label="ส่ง"],button[aria-label="Send"],button[aria-label="Send prompt"],button[aria-label="Send message"],button[title="ส่ง"],button[title="Send"]';
   const buttons=Array.from(document.querySelectorAll(selector)).filter(e=>visible(e)&&!e.disabled&&e.getAttribute("aria-disabled")!=="true"&&!/หยุด|stop/i.test((e.getAttribute("aria-label")||"")+" "+(e.getAttribute("title")||"")));
   if(buttons.length!==1)return "button_wait";
   if(!await safe()||draft()!==message||!own())return "wait";
   buttons[0].click();
   for(let k=0;k<30;k++){await sleep(500);if(seen())return "sent"}
   return "send_unknown";
  }
  return "unknown";
 }});
 return r[0]?.result||"unknown";
}
async function deliver(){
 if(running)return;running=true;
 let j;
 try{
  const r=await req("/pending");if(!r.ok)return;j=await r.json();
  if(!j.id){
   const sr=await req("/status");if(!sr.ok)return;const st=await sr.json();
   if(st.job?.state!=="needs_review"&&!(st.job?.state==="claimed"&&st.job?.phase==="sending"))return;
   const recover=st.job;
   const ts=(await chrome.tabs.query({url:"https://chatgpt.com/*"})).filter(t=>t.url?.split(/[?#]/)[0]===recover.url);
   if(ts.length===1&&await page(ts[0],recover,"probe")==="sent")await receipt(recover,"sent","posted preview marker verified");
   return;
  }
  if(!await idle()){await note(j,"waiting: mouse or keyboard active");return}
  const tabs=(await chrome.tabs.query({url:"https://chatgpt.com/*"})).filter(t=>t.url&&t.url.split(/[?#]/)[0]===j.url);
  if(tabs.length!==1){await note(j,"waiting: bound chat not unique");return}
  const tab=tabs[0];
  let p=await page(tab,j,"probe");
  if(p==="sent"){if(j.state==="claimed")await receipt(j,"sent","marker observed");return}
  if(j.phase==="recover"){
   if(p==="drafted"||p==="attached"){await change(j,p);j.phase=p}
   else if(p==="empty"){await change(j,"pending");return}
   else {await note(j,"waiting: "+p);return}
  }
  if(j.state==="pending"){
   if(p!=="empty"){await note(j,"waiting: "+p);return}
   if(!await idle())return;
   const q=await req("/claim",{id:j.id});if(!q.ok)return;j.state="claimed";j.phase="attach";
   const im=await req("/image/"+j.id);if(!im.ok){await receipt(j,"needs_review","image unavailable");return}
   p=await page(tab,j,"attach",Array.from(new Uint8Array(await im.arrayBuffer())));
   if(p==="wait"){await change(j,"pending");return}
   if(p==="sent"){await receipt(j,"sent","marker observed");return}
   if(p!=="attached"){await receipt(j,"needs_review",p);return}
   await change(j,"attached");j.phase="attached";
  }
  if(j.phase==="attached"){
   if(!await idle()){await note(j,"waiting: user active after attachment");return}
   p=await page(tab,j,"probe");
   if(p==="sent"){await receipt(j,"sent","marker observed");return}
   if(p==="drafted"){await change(j,"drafted");j.phase="drafted"}
   else if(p==="attached"){
    p=await page(tab,j,"draft");
    if(p==="wait"){await note(j,"waiting: user active");return}
    if(p!=="drafted"){await receipt(j,"needs_review",p);return}
    await change(j,"drafted");j.phase="drafted";
   }else{await note(j,"waiting: "+p);return}
  }
  if(j.phase==="drafted"){
   if(!await idle()){await note(j,"waiting: user active before send");return}
   p=await page(tab,j,"probe");
   if(p==="sent"){await receipt(j,"sent","marker observed");return}
   if(p!=="drafted"){await note(j,"waiting: "+p);return}
   await change(j,"sending");j.phase="sending";
   p=await page(tab,j,"send");
   if(p==="wait"||p==="button_wait"){await change(j,"drafted");await note(j,"waiting: "+p);return}
   if(p==="sent"){await receipt(j,"sent","marker observed");return}
   await receipt(j,"needs_review",p);
  }
 }catch(e){if(j?.id){try{if(j.phase==="sending"||j.phase==="attach")await receipt(j,"needs_review",String(e));else await note(j,String(e))}catch{}}}
 finally{running=false}
}

importScripts("goal_tracker.js");

importScripts("sleep_mode.js");


chrome.runtime.onMessage.addListener((m,sender,reply)=>{
 if(m?.type!=="iclone-handoff-observed")return;
 (async()=>{
  const url=sender.tab?.url?.split(/[?#]/)[0];
  if(!url||!/^https:\/\/chatgpt\.com\/(?:.*\/)?c\/[a-zA-Z0-9-]+\/?$/.test(url)||!(/^[a-f0-9]{32}$/.test(m.id)))return {ok:false};
  const r=await req("/handoff/bind",{id:m.id,url});
  if(!r.ok)return {ok:false};
  return {ok:true};
 })().then(reply).catch(()=>reply({ok:false}));return true;
});
