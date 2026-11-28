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
async function goalControl(action){if(action==="resume")document.querySelector("#goalstatus").textContent="กำลังส่งข้อความแรกทันที...";const s=await chrome.runtime.sendMessage({type:"iclone-goal-control",action});document.querySelector("#goalstatus").textContent=(s?.enabled?"เปิด — ":"หยุด — ")+(s?.status||(s?.error?thai(s.error):"")||"ไม่ทราบสถานะ")+(s?.achievement?"\nStop key: "+s.achievement:"")}
document.querySelector("#goalpause").onclick=()=>goalControl("pause");
document.querySelector("#goalresume").onclick=()=>goalControl("resume");
goalControl("status").catch(()=>document.querySelector("#goalstatus").textContent="ตัวติดตามยังไม่พร้อม ลองปิดแล้วเปิด popup ใหม่");
setInterval(()=>goalControl("status").catch(()=>{}),1000);
async function copyPrompt(mode){
 const el=document.querySelector("#copystatus"),btn=document.querySelector("#copy-"+mode);
 btn.disabled=true;el.textContent="กำลังอ่านข้อมูลจากโปรเจกต์...";
 try{
  const res=await fetch("http://127.0.0.1:18764/handoff/create",{method:"POST",headers:{"X-Preview-Key":PREVIEW_KEY,"Content-Type":"application/json"},cache:"no-store",body:JSON.stringify({kind:mode})});
  if(!res.ok)throw Error("อ่านข้อมูลไม่ได้ ("+res.status+")");
  const data=await res.json();
  if(!data.prompt)throw Error("ไม่พบข้อมูล Prompt");
  await navigator.clipboard.writeText(data.prompt);
  el.textContent="คัดลอกแล้ว — วางและส่งในแชตใหม่ ภาพจาก iClone จะส่งเข้าแชตนั้นเอง";
 }catch(e){el.textContent="คัดลอกไม่สำเร็จ: "+thai(e)}
 finally{btn.disabled=false}
}
for(const mode of ["new","continue"])document.querySelector("#copy-"+mode).onclick=()=>copyPrompt(mode);
