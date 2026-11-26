const ss=document.querySelector("#sleep-status");
async function sleepControl(action){
 const confirmed=action==="start"?confirm("เปิด Sleep Mode สำหรับเรื่องที่ผูกไว้ ทำทุกท่อนที่ยังไม่ผ่านจนจบแผน อนุญาตให้ AI ตรวจและเรนเดอร์เอง ไม่ส่ง Drive อัตโนมัติ ใช่หรือไม่?"):false;
 if(action==="start"&&!confirmed)return;
 const r=await chrome.runtime.sendMessage({type:"iclone-sleep-control",action,confirmed});
 ss.textContent=r?.error||((r?.enabled?"เปิด — ":"ปิด — ")+(r?.phase||"ยังไม่เริ่ม")+(r?.part?" | ท่อน "+r.part:"")+(r?.local?.status?"\n"+r.local.status:""));
}
document.querySelector("#sleep-start").onclick=()=>sleepControl("start").catch(e=>ss.textContent=String(e));
document.querySelector("#sleep-pause").onclick=()=>sleepControl("pause").catch(e=>ss.textContent=String(e));
sleepControl("status").catch(e=>ss.textContent=String(e));
setInterval(()=>sleepControl("status").catch(()=>{}),2000);
