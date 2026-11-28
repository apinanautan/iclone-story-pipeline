// Sleep = two buttons only; the story and its parts come from whatever story is open now (user 2026-11-28:
// many stories, each with its own number of parts; never show a fixed plan)
const ss=document.querySelector("#sleep-status"),go=document.querySelector("#sleep-start"),stop=document.querySelector("#sleep-pause");
async function sleepControl(action){
 let story="";
 if(action==="start"){const s=await chrome.runtime.sendMessage({type:"iclone-sleep-control",action:"status"});story=s?.current_story||"";
  if(!confirm("ทำเรื่อง \""+story+"\" ทุกท่อนที่ยังไม่ผ่านจนจบเรื่องเอง AI ตรวจและเรนเดอร์เอง ไม่ส่ง Drive เอง เริ่มเลยไหม?"))return}
 const r=await chrome.runtime.sendMessage({type:"iclone-sleep-control",action,confirmed:action==="start",scope:"all"});
 // while running: the story Sleep works on; while stopped: the story open now (an old run's name would be stale)
 story=(r?.enabled?r?.story:r?.current_story)||story;
 go.disabled=!!r?.enabled||r?.ready===false||!!r?.error;stop.disabled=!r?.enabled;
 const PH={work:"กำลังทำท่อน",handoff:"กำลังเปิดแชตใหม่ให้ท่อนถัดไป",done:"จบเรื่องแล้ว"};
 ss.textContent=(story?"เรื่อง: "+story+"\n":"")+(r?.error?thai(r.error):r?.ready===false?"ยังเริ่มไม่ได้: "+r.reason:r?.enabled?"ทำงานอยู่ — "+(PH[r.phase]||r.phase||"")+(r?.part?" "+r.part:"")+(r?.local?.status?"\nล่าสุด: "+thai(r.local.status):""):"หยุดอยู่");
}
go.onclick=()=>sleepControl("start").catch(e=>ss.textContent=thai(e));
stop.onclick=()=>sleepControl("pause").catch(e=>ss.textContent=thai(e));
sleepControl("status").catch(e=>{ss.textContent=thai(e);go.disabled=true});
setInterval(()=>sleepControl("status").catch(()=>{}),2000);
