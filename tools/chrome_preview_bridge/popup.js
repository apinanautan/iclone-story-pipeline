const PREVIEW_KEY=LOCAL_PREVIEW_KEY;
// Plain Thai for every error (user 2026-11-28: raw "TypeError: Failed to fetch" means nothing to the user)
const thai=e=>{const m=String(e?.message||e);return /fetch|NetworkError/i.test(m)?"ต่อโปรแกรมในเครื่องไม่ได้: เปิดหน้าต่าง Ai-iclone (ตัวเชื่อมเปิดเอง) แล้วลองใหม่":m.replace(/^(Type)?Error:\s*/,"")};
const STEP={pending:"รอส่ง",claimed:"กำลังส่ง",sent:"ส่งแล้ว",needs_review:"ต้องตรวจในแชต"};
async function showTop(){
 const el=document.querySelector("#top");
 try{
  const r=await fetch("http://127.0.0.1:18764/status",{headers:{"X-Preview-Key":PREVIEW_KEY},cache:"no-store",signal:AbortSignal.timeout(2000)});
  if(!r.ok)throw Error(r.status===403?"คีย์ไม่ตรงกับโปรแกรมในเครื่อง":"โปรแกรมในเครื่องตอบ "+r.status);
  const d=await r.json(),[tab]=await chrome.tabs.query({active:true,currentWindow:true});
  const cut=u=>String(u||"").replace(/[?#].*$/,"").replace(/\/$/,""),here=d.bound?.url&&cut(d.bound.url)===cut(tab?.url);
  el.innerHTML="";const line=(t,c)=>{const s=document.createElement("div");s.textContent=t;if(c)s.className=c;el.append(s)};
  line("✓ เชื่อมโปรแกรมในเครื่องแล้ว","ok");
  line("งานตอนนี้: "+(d.now?.story?d.now.story+" ท่อน "+d.now.part:"ยังไม่ได้เลือกเรื่อง"));
  line("แชตที่รับภาพ: "+(!d.bound?.url?"ยังไม่ผูก":here?"แชตนี้ ✓ ("+d.bound.story+")":"แชตอื่น ("+d.bound.story+")"),d.bound?.url&&!here?"bad":"");
  if(d.job?.state)line("ภาพล่าสุด: "+(STEP[d.job.state]||d.job.state)+(d.generating?" · กำลังทำภาพใหม่":""));
 }catch(e){el.innerHTML="";const s=document.createElement("div");s.className="bad";s.textContent="✗ "+thai(e);el.append(s)}
}
showTop();setInterval(showTop,2000);
const status = document.querySelector("#status");
document.querySelector("#attach").onclick=async()=>{
  try{
    status.textContent="กำลังแนบภาพ...";
    const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
    if(!tab?.url || !/^https:\/\/chatgpt\.com\/(?:.*\/)?c\//.test(tab.url)) throw Error("เปิดแชต ChatGPT ที่ต้องการก่อน");
    const res=await fetch("http://127.0.0.1:18764/preview",{headers:{"X-Preview-Key":PREVIEW_KEY},cache:"no-store"});
    if(!res.ok)throw Error("Preview relay: "+res.status);
    const bytes=Array.from(new Uint8Array(await res.arrayBuffer()));
    const result=await chrome.scripting.executeScript({target:{tabId:tab.id},args:[bytes],func:(bytes)=>{
      if(!/\/c\/[^/]+\/?$/.test(location.pathname))return "แชตไม่ตรง";
      const composer=document.querySelector("#prompt-textarea");
      if(!composer)return "ไม่พบช่องแชต";
      if(document.querySelector('[data-testid="stop-button"]'))return "AI กำลังตอบอยู่";
      if(composer.innerText.trim())return "มีข้อความร่างอยู่ จึงไม่แก้ไข";
      const input=Array.from(document.querySelectorAll('input[type=file]')).find(e=>!e.disabled&&(!e.accept||/image|\*/.test(e.accept)));
      if(!input)return "ไม่พบช่องแนบไฟล์";
      const dt=new DataTransfer();
      dt.items.add(new File([new Uint8Array(bytes)],"iclone-preview.jpg",{type:"image/jpeg"}));
      input.files=dt.files;input.dispatchEvent(new Event("change",{bubbles:true}));
      return "ส่งภาพเข้าองค์ประกอบแนบไฟล์แล้ว ตรวจรูปก่อนกดส่ง";
    }});
    status.textContent=result[0]?.result||"ไม่พบผลการแนบ";
  }catch(e){status.textContent=thai(e);}
};
async function goalControl(action){if(action==="resume")document.querySelector("#goalstatus").textContent="กำลังส่งข้อความแรกทันที...";const s=await chrome.runtime.sendMessage({type:"iclone-goal-control",action});document.querySelector("#goalstatus").textContent=(s?.enabled?"เปิด — ":"หยุด — ")+(s?.status||(s?.error?thai(s.error):"")||"ไม่ทราบสถานะ")+(s?.achievement?"\nStop key: "+s.achievement:"")}
document.querySelector("#goalpause").onclick=()=>goalControl("pause");
document.querySelector("#goalresume").onclick=()=>goalControl("resume");
goalControl("status").catch(()=>document.querySelector("#goalstatus").textContent="ตัวติดตามยังไม่พร้อม ลองปิดแล้วเปิด popup ใหม่");
setInterval(()=>goalControl("status").catch(()=>{}),1000);
async function copyPrompt(mode){
 const el=document.querySelector("#copystatus"),btn=document.querySelector("#copy-"+mode);
 btn.disabled=true;el.textContent="กำลังอ่านข้อมูลจากโปรเจกต์...";
 try{
  const next=mode==="continue";
  const res=await fetch("http://127.0.0.1:18764/"+(next?"handoff/create":"prompt/new"),{headers:{"X-Preview-Key":PREVIEW_KEY,"Content-Type":"application/json"},cache:"no-store",...(next?{method:"POST",body:JSON.stringify({})}:{})});
  if(!res.ok)throw Error("อ่านข้อมูลไม่ได้ ("+res.status+")");
  const data=await res.json();
  if(!data.prompt)throw Error("ไม่พบข้อมูล Prompt");
  await navigator.clipboard.writeText(data.prompt);
  el.textContent="คัดลอกแล้ว — วางและส่งในแชตที่ต้องการ"+(next?" เพื่อผูกการส่งภาพอัตโนมัติ":"");
 }catch(e){el.textContent="คัดลอกไม่สำเร็จ: "+thai(e)}
 finally{btn.disabled=false}
}
for(const mode of ["new","continue"])document.querySelector("#copy-"+mode).onclick=()=>copyPrompt(mode);
document.querySelector("#bind").onclick=async()=>{
 const el=document.querySelector("#bindstatus");
 try{
  const [tab]=await chrome.tabs.query({active:true,currentWindow:true});
  if(!tab?.url||!/^https:\/\/chatgpt\.com\/(?:.*\/)?c\/[a-zA-Z0-9-]+\/?(?:[?#].*)?$/.test(tab.url))throw Error("เปิดแชตเป้าหมายก่อน");
  const res=await fetch("http://127.0.0.1:18764/bind",{method:"POST",headers:{"X-Preview-Key":PREVIEW_KEY,"Content-Type":"application/json"},body:JSON.stringify({url:tab.url})});
  if(!res.ok)throw Error("ผูกไม่ได้: ตรวจว่ามีเรื่องปัจจุบันและไม่มีภาพค้าง ("+res.status+")");
  const b=await res.json();el.textContent="ผูกแชตนี้แล้ว: "+b.story;
 }catch(e){el.textContent=thai(e)}
};