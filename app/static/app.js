const API = window.location.origin;
let currentTab = "chat";
let busy = false;

function $(id) { return document.getElementById(id); }

async function api(path, options) {
  const res = await fetch(API + path, options);
  let data = null;
  const ct = res.headers.get("content-type") || "";
  if (ct.includes("application/json")) {
    data = await res.json();
  } else {
    data = { detail: await res.text() };
  }
  if (!res.ok) {
    const msg = (data && (data.detail || data.message)) || res.statusText;
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

async function checkHealth() {
  const el = $("status");
  try {
    const d = await api("/api/health");
    const model = d.model ? String(d.model).split("/").pop() : "";
    if (d.configured) {
      el.textContent = "online" + (model ? " · " + model : "");
      el.className = "online";
      el.title = "Model: " + (d.model || "unknown");
    } else {
      el.textContent = "no API key";
      el.className = "warn";
      el.title = "Set OPENROUTER_API_KEY";
    }
    return d;
  } catch (e) {
    el.textContent = "offline";
    el.className = "err";
    return null;
  }
}

function addMessage(role, text, agent) {
  const box = $("messages");
  if (!box) return;
  const div = document.createElement("div");
  div.className = "msg " + role;
  if (agent) {
    const a = document.createElement("div");
    a.className = "agent";
    a.textContent = agent;
    div.appendChild(a);
  }
  const p = document.createElement("div");
  p.textContent = text;
  div.appendChild(p);
  box.appendChild(div);
  div.scrollIntoView({ behavior: "smooth", block: "end" });
}

function setBusy(on) {
  busy = on;
  ["send-btn", "chat-input", "plan-input"].forEach(function (id) {
    const el = $(id);
    if (el) el.disabled = on;
  });
  document.querySelectorAll("#plan-form button").forEach(function (b) {
    b.disabled = on;
  });
}

async function sendChat(e) {
  if (e) e.preventDefault();
  if (busy) return;
  const input = $("chat-input");
  const msg = (input.value || "").trim();
  if (!msg) return;
  input.value = "";
  addMessage("user", msg);
  setBusy(true);
  try {
    const d = await api("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    });
    addMessage("ai", d.reply || d.response || "No response");
  } catch (err) {
    addMessage("ai", "Error: " + err.message);
  } finally {
    setBusy(false);
    input.focus();
  }
}

function renderPlan(data) {
  const out = $("plan-output");
  if (!out) return;
  out.innerHTML = "";
  const head = document.createElement("div");
  head.className = "plan-head";
  head.innerHTML =
    "<strong>Goal:</strong> " +
    escapeHtml(data.goal || "") +
    " <span class=\"badge\">" +
    escapeHtml(data.status || "") +
    "</span>";
  out.appendChild(head);

  const tasks = data.tasks || [];
  if (!tasks.length) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent =
      "No tasks returned. Set OPENROUTER_API_KEY if the LLM is unconfigured.";
    out.appendChild(empty);
    return;
  }

  tasks.forEach(function (t) {
    const div = document.createElement("div");
    div.className = "task";
    const agent = t.agent_type || t.agent || "";
    const desc = t.description || "";
    const tid = t.task_id || t.id || "";
    let body = "<span class=\"agent-tag\">" + escapeHtml(agent) + "</span>";
    body += "<div class=\"task-id\">" + escapeHtml(tid) + "</div>";
    body += "<div>" + escapeHtml(desc) + "</div>";
    if (t.result) {
      const content =
        typeof t.result === "object"
          ? t.result.content || t.result.findings || JSON.stringify(t.result, null, 2)
          : String(t.result);
      body += "<pre class=\"result\">" + escapeHtml(String(content).slice(0, 4000)) + "</pre>";
    }
    if (t.verification) {
      body +=
        "<div class=\"verify\">verify: " +
        (t.verification.passed ? "pass" : "issues") +
        " (" +
        (t.verification.score != null ? t.verification.score : "?") +
        ")</div>";
    }
    div.innerHTML = body;
    out.appendChild(div);
  });
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function runPlan(mode) {
  if (busy) return;
  const input = $("plan-input");
  const goal = (input.value || "").trim();
  if (!goal) return;
  setBusy(true);
  const out = $("plan-output");
  if (out) out.innerHTML = "<p class=\"muted\">Working...</p>";
  try {
    const path = mode === "execute" ? "/api/execute" : "/api/plan";
    const d = await api(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ goal: goal }),
    });
    renderPlan(d);
  } catch (err) {
    if (out) out.innerHTML = "<p class=\"err-text\">Error: " + escapeHtml(err.message) + "</p>";
  } finally {
    setBusy(false);
  }
}

async function loadAgents() {
  const grid = $("agents-grid");
  if (!grid) return;
  grid.innerHTML = "<p class=\"muted\">Loading...</p>";
  try {
    const d = await api("/api/agents");
    grid.innerHTML = "";
    (d.agents || []).forEach(function (a) {
      const card = document.createElement("div");
      card.className = "agent-card";
      const caps = (a.capabilities || [])
        .map(function (c) {
          return "<span class=\"cap\">" + escapeHtml(c) + "</span>";
        })
        .join("");
      card.innerHTML =
        "<h4>" +
        escapeHtml(a.name || a.type) +
        "</h4><p>" +
        escapeHtml(a.description || "") +
        "</p><div class=\"caps\">" +
        caps +
        "</div>";
      grid.appendChild(card);
    });
  } catch (err) {
    grid.innerHTML = "<p class=\"err-text\">" + escapeHtml(err.message) + "</p>";
  }
}

async function loadMemory() {
  const list = $("memory-list");
  if (!list) return;
  list.innerHTML = "<p class=\"muted\">Loading...</p>";
  try {
    const d = await api("/api/memory");
    list.innerHTML = "";
    const items = d.items || [];
    if (!items.length) {
      list.innerHTML = "<p class=\"muted\">No memories yet.</p>";
      return;
    }
    items.forEach(function (i) {
      const div = document.createElement("div");
      div.className = "memory-item";
      div.innerHTML =
        "<div class=\"key\">" +
        escapeHtml(i.key) +
        "</div><div class=\"val\">" +
        escapeHtml(i.content) +
        "</div><button type=\"button\" class=\"link-btn\" data-key=\"" +
        escapeHtml(i.key) +
        "\">Forget</button>";
      list.appendChild(div);
    });
    list.querySelectorAll(".link-btn").forEach(function (btn) {
      btn.addEventListener("click", async function () {
        try {
          await api("/api/memory/" + encodeURIComponent(btn.dataset.key), {
            method: "DELETE",
          });
          loadMemory();
        } catch (err) {
          alert(err.message);
        }
      });
    });
  } catch (err) {
    list.innerHTML = "<p class=\"err-text\">" + escapeHtml(err.message) + "</p>";
  }
}

async function addMemory(e) {
  e.preventDefault();
  const key = ($("mem-key").value || "").trim();
  const content = ($("mem-content").value || "").trim();
  if (!key || !content) return;
  try {
    await api("/api/memory", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ key: key, content: content, category: "preference" }),
    });
    $("mem-key").value = "";
    $("mem-content").value = "";
    loadMemory();
  } catch (err) {
    alert(err.message);
  }
}

function switchTab(tab) {
  currentTab = tab;
  document.querySelectorAll(".tab").forEach(function (t) {
    t.classList.toggle("active", t.dataset.tab === tab);
  });
  document.querySelectorAll(".view").forEach(function (v) {
    v.classList.toggle("active", v.id === "view-" + tab);
  });
  if (tab === "agents") loadAgents();
  if (tab === "memory") loadMemory();
}

document.addEventListener("DOMContentLoaded", function () {
  checkHealth();
  setInterval(checkHealth, 60000);

  const chatForm = $("chat-form");
  if (chatForm) chatForm.addEventListener("submit", sendChat);

  const planForm = $("plan-form");
  if (planForm) {
    planForm.addEventListener("submit", function (e) {
      e.preventDefault();
      const mode =
        (e.submitter && e.submitter.dataset && e.submitter.dataset.mode) || "plan";
      runPlan(mode);
    });
  }

  const memForm = $("memory-form");
  if (memForm) memForm.addEventListener("submit", addMemory);

  document.querySelectorAll(".tab").forEach(function (t) {
    t.addEventListener("click", function () {
      switchTab(t.dataset.tab);
    });
  });
});

if ("serviceWorker" in navigator) {
  navigator.serviceWorker.register("/sw.js").catch(function () {});
}
