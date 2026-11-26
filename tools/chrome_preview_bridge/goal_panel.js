(()=>{
 if(globalThis.__icGoalPanelV2)return;globalThis.__icGoalPanelV2=true;
 const eligible=()=>location.origin==="https://chatgpt.com"&&/\/c\/[a-zA-Z0-9-]+\/?$/.test(location.pathname);
 let host=null,state=null,busy=false,requesting=false,timer=null;
 function make(){
  document.querySelectorAll("#cc5-goal-floating-panel").forEach(e=>e.remove());
  host=document.createElement("div");host.id="cc5-goal-floating-panel";
  host.style.cssText="position:fixed;right:16px;bottom:110px;z-index:2147483645;width:260px;max-width:calc(100vw - 32px);";
  const root=host.attachShadow({mode:"open"});
  root.innerHTML=`<style>:host{font-family:system-ui,sans-serif}section{box-sizing:border-box;background:#20242c;color:#f4f5f7;border:1px solid #515967;border-radius:12px;padding:12px;box-shadow:0 6px 20px #0005;font-size:12px;line-height:1.5}header{display:flex;align-items:center;gap:7px;font-weight:600;font-size:13px}i{width:8px;height:8px;background:#9ca3af;border-radius:50%;flex:none}p{margin:8px 0 3px;overflow-wrap:anywhere}strong{font-size:20px;font-variant-numeric:tabular-nums}small{color:#c4cbd5}footer{display:flex;gap:6px;margin-top:8px}button{background:#384252;border:1px solid #657184;color:#fff;padding:5px 9px;border-radius:6px;cursor:pointer;font:inherit}button:disabled{opacity:.5;cursor:default}.min{margin-left:auto;padding:0 6px}.compact .details{display:none}</style><section><header><i></i>ติดตามเป้าหมาย · ทุกงาน<button class="min" title="ย่อ/ขยาย">−</button></header><div class="details"><p id="status">กำลังเชื่อมต่อ...</p><strong id="clock">--:--</strong><div><small id="hint"></small></div><footer><button id="start">เริ่มทันที</button><button id="pause">พักติดตาม</button></footer></div></section>`;
  const q=x=>root.querySelector(x);
  q(".min").onclick=()=>{const b=q("section").classList.toggle("compact");q(".min").textContent=b?"+":"−"};
  for(const [id,action] of [["start","resume"],["pause","pause"]])q("#"+id).onclick=async()=>{q("#status").textContent=action==="resume"?"กำลังเริ่มส่งข้อความ...":"กำลังพัก...";try{state=await chrome.runtime.sendMessage({type:"iclone-goal-control",action});}catch(e){state={error:"ส่วนขยายไม่ตอบสนอง"}}render()};
  document.documentElement.append(host);
 }
 function render(){
  if(!host||!state)return;
  const q=x=>host.shadowRoot.querySelector(x);
  const raw=state.status||"",enabled=!!state.enabled;
  const labels={"starting immediately":"กำลังเริ่มส่งข้อความ","waiting until next followup":"รอส่งข้อความรอบถัดไป","followup sent":"ส่งข้อความแล้ว","paused":"พักติดตาม","waiting: user draft":"มีข้อความร่างในช่องแชต","waiting: previous send unverified; no duplicate":"รอยืนยันข้อความก่อนหน้า","waiting: bound chat not unique":"ไม่พบแชตเป้าหมายที่แน่นอน","wait":"รอช่องแชตพร้อม","draft unknown":"ตรวจข้อความร่างไม่สำเร็จ","user draft":"มีข้อความร่างของผู้ใช้","starting":"กำลังเริ่มระบบ"};
  const completed=raw.startsWith("completed:");
  let label=state.error||labels[raw]||raw||"กำลังเชื่อมต่อ";
  if(completed)label="บรรลุเป้าหมาย — หยุดติดตาม";
  q("#status").textContent=label;
  q("i").style.background=completed?"#34d399":enabled?"#60a5fa":"#9ca3af";
  const n=Math.max(0,Math.ceil(((state.next||0)-Date.now())/1000));
  q("#clock").textContent=enabled?String(Math.floor(n/60)).padStart(2,"0")+":"+String(n%60).padStart(2,"0"):"--:--";
  q("#hint").textContent=completed?"Achievement Key ตรงกัน":!enabled?"กดเริ่มเพื่อเปิดการติดตาม":state.pending?"กำลังจัดการข้อความรอบนี้":n>0?"เวลาถึงการติดตามรอบถัดไป":"ครบเวลาแล้ว — รอส่ง";
  q("#pause").disabled=!enabled;
 }
 async function tick(){
  if(!eligible()){if(host){host.remove();host=null}return}
  if(!host)make();
  if(requesting)return;requesting=true;
  try{state=await chrome.runtime.sendMessage({type:"iclone-goal-control",action:"status"});render()}catch(e){if(/context invalidated/i.test(String(e))||!chrome.runtime?.id){clearInterval(timer);if(host)host.remove();host=null;globalThis.__icGoalPanelV2=false}else if(host)host.shadowRoot.querySelector("#status").textContent="รอเชื่อมต่อส่วนขยายใหม่"}finally{requesting=false}
 }
 timer=setInterval(tick,1000);tick();
})();