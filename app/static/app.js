const API = window.location.origin;
let currentTab =  chat;

async function checkHealth() {
  try { const r = await fetch(API + /api/health); const d = await r.json();
    document.getElementById(status).textContent = d.configured ? online : no API key;
    document.getElementById(status).className = d.configured ? online : ;
 return d; } catch(e) { document.getElementById(status).textContent = offline; return null; }
}

function addMessage(role, text, agent) {
 const div = document.createElement(div);
 div.className = msg  + role;
 if (agent) { const a = document.createElement( div); a.className = agent; a.textContent = agent; div.appendChild(a); }
 const p = document.createElement(div); p.textContent = text; div.appendChild(p);
 document.getElementById(messages).appendChild(div);
 div.scrollIntoView({behavior:smooth});
}

async function sendChat() {
 const input = document.getElementById(chat-input);
 const msg = input.value.trim();
 if (!msg) return;
 input.value = ;
  addMessage(user, msg);
  try {
    const r = await fetch(API + /api/chat, { method: POST, headers: {Content-Type:application/json}, body: JSON.stringify({message: msg}) });
    const d = await r.json();
    addMessage(ai, d.reply || No response);
  } catch(e) { addMessage(ai, Error:  + e.message); }
}

async function sendPlan() {
  const goal = document.getElementById( chat-input).value.trim();
  if (!goal) return;
  addMessage(user, Plan:  + goal);
  try {
    const r = await fetch(API +  /api/execute, { method: POST, headers: {Content-Type:application/json}, body: JSON.stringify({goal: goal}) });
    const d = await r.json();
    showPlan(d);
    addMessage(ai, Plan completed:  + d.status);
  } catch(e) { addMessage( ai, Error:  + e.message); }
}

function showPlan(data) {
  const out = document.getElementById( plan-output);
  out.innerHTML = ;
 if (data.tasks) {
 data.tasks.forEach(t => {
 const div = document.createElement(div);
 div.className = task;
 div.innerHTML = <span class=agent-tag> + (t.agent_type||) + </span><br> + (t.task_id||) + :  + (t.description||);
      out.appendChild(div);
    });
  }
}

async function loadAgents() {
  try { const r = await fetch(API +  /api/agents); const d = await r.json();
    const grid = document.createElement(div); grid.className = agents-grid;
    d.agents.forEach(a => {
      const card = document.createElement(div); card.className = agent-card;
      card.innerHTML = <h4> + a.name + </h4><p> + a.description + </p><div class=caps> + a.capabilities.map(c => <span class=cap>+c+</span>).join() + </div>;
 grid.appendChild(card);
 });
 const main = document.querySelector(main);
 main.innerHTML = ; main.appendChild(grid);
  } catch(e) {}
}

async function loadMemory() {
  try { const r = await fetch(API + /api/memory); const d = await r.json();
    const main = document.querySelector(main);
    main.innerHTML = ;
 d.items.forEach(i => {
 const div = document.createElement(div); div.className = memory-item;
 div.innerHTML = <div class=key> + i.key + </div><div class=val> + i.content + </div>;
 main.appendChild(div);
 });
 } catch(e) {}
}

function switchTab(tab) {
 currentTab = tab;
 document.querySelectorAll(.tab).forEach(t => t.classList.toggle(active, t.dataset.tab === tab));
 if (tab === chat) {
 document.querySelector(main).innerHTML = ;
    const mc = document.createElement(div); mc.id = chat-container;
    mc.innerHTML = <div id=messages></div><form id=chat-form><input id=chat-input type=text placeholder=\What would you like to do?" autocomplete=off><button type=submit>Send</button></form>;
 document.querySelector(main).appendChild(mc);
 document.getElementById(chat-form).addEventListener(submit, e => { e.preventDefault(); currentTab === plan ? sendPlan() : sendChat(); });
 } else if (tab === plan) {
 document.querySelector(main).innerHTML = <div id=plan-output></div>;
 const inp = document.getElementById(chat-input);
 if (inp) sendPlan();
 } else if (tab === agents) { loadAgents(); }
 else if (tab === memory) { loadMemory(); }
}

document.addEventListener(DOMContentLoaded, () => {
 checkHealth();
 document.getElementById(chat-form).addEventListener(submit, e => { e.preventDefault(); sendChat(); });
 document.querySelectorAll(.tab).forEach(t => t.addEventListener(click, () => switchTab(t.dataset.tab)));
});

if (serviceWorker in navigator) { navigator.serviceWorker.register(/sw.js); }