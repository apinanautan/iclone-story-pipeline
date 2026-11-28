const ss=document.querySelector("#sleep-status");
let currentPart=null;
async function sleepControl(action,scope="all"){
 const confirmed=action==="start"?confirm(scope==="current"?"เริ่มจากท่อน "+currentPart+" จนจบแผน ไม่ย้อนทำท่อนก่อนหน้า อนุญาตให้ AI ตรวจและเรนเดอร์เอง ไม่ส่ง Drive อัตโนมัติ ใช่หรือไม่?":"เปิด Sleep Mode ทำทุกท่อนที่ยังไม่ผ่านจนจบแผน หากต้องย้อนท่อนก่อนหน้า ระบบจะป้องกันการเปิดทับงานปัจจุบัน อนุญาตให้ AI ตรวจและเรนเดอร์เอง ไม่ส่ง Drive อัตโนมัติ ใช่หรือไม่?"):false;
 if(action==="start"&&!confirmed)return;
 const r=await chrome.runtime.sendMessage({type:"iclone-sleep-control",action,confirmed,scope});
 currentPart=r?.current_part||currentPart;document.querySelector("#sleep-current").disabled=!currentPart||!!r?.enabled||r?.ready===false||!!r?.error;document.querySelector("#sleep-current").textContent=currentPart?"เริ่มจากท่อน "+currentPart+" จนจบแผน":"เริ่มจากท่อนปัจจุบันจนจบแผน";
 document.querySelector("#sleep-start").disabled=!!r?.enabled||r?.ready===false||!!r?.error; document.querySelector("#sleep-pause").disabled=!r?.enabled; ss.textContent=r?.error||(r?.ready===false?("ยังเปิดไม่ได้: "+r.reason):"")||((r?.enabled?"เปิด — ":"ปิด — ")+(r?.phase||"ยังไม่เริ่ม")+(r?.part?" | ท่อน "+r.part:"")+(r?.local?.status?"\n"+r.local.status:""));
}
document.querySelector("#sleep-start").onclick=()=>sleepControl("start").catch(e=>ss.textContent=String(e));
document.querySelector("#sleep-current").onclick=()=>sleepControl("start","current").catch(e=>ss.textContent=String(e));
document.querySelector("#sleep-pause").onclick=()=>sleepControl("pause").catch(e=>ss.textContent=String(e));
sleepControl("status").catch(e=>{ss.textContent=String(e);document.querySelector("#sleep-start").disabled=true});
setInterval(()=>sleepControl("status").catch(()=>{}),2000);
