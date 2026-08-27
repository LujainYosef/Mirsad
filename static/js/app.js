"use strict";

/* ===========================================================
   i18n
   =========================================================== */
const I18N = {
  ar: {
    lang_toggle_label: "EN",
    tagline: "بعين مِرصاد، للمحتالين بالمرصاد",
    hero_title: "تحقيق أمني فوري، مبني على الأدلة",
    hero_sub: "ارفع بريدًا احتياليًا، رابطًا مشبوهًا، ملف سجلّات SIEM، أو لقطة شاشة — ويتولى مِرصاد تحليلها كمحقق أمني بمستوى L2/L3: ماذا حدث، ما مدى خطورته، وما الخطوة التالية.",
    dz_text: "اسحب الملفات هنا أو اضغط للاختيار",
    dz_hint: "PDF · صور/لقطات شاشة · TXT/LOG/CSV/EML — حتى 10MB لكل ملف",
    or_divider: "أو",
    text_placeholder: "ألصق نص البريد الإلكتروني، سطور السجلّات، أو أي دليل نصّي هنا...",
    url_placeholder: "أو أدخل رابطًا مشبوهًا للتحقيق فيه (اختياري)",
    untrusted_note: "كل ما يتم رفعه يُعامل كدليل غير موثوق للتحليل فقط، ولا يُنفَّذ أي ملف على الإطلاق.",
    submit_btn: "ابدأ التحقيق",
    scan_text: "جارٍ فحص الأدلة وبناء التحقيق…",
    export_btn: "تصدير التقرير",
    h_confirmed: "الأدلة المؤكدة",
    h_events: "الأحداث المشبوهة",
    h_iocs: "مؤشرات الاختراق (IOCs)",
    ioc_type: "النوع", ioc_value: "القيمة", ioc_context: "السياق",
    h_timeline: "الجدول الزمني",
    h_hypotheses: "الفرضيات",
    h_gaps: "الثغرات في الأدلة",
    h_steps: "خطوات التحقيق التالية",
    h_recs: "التوصيات الدفاعية",
    h_notes: "ملاحظات المحلل",
    new_case_btn: "تحقيق جديد",
    chat_fab: "اسأل المحقق",
    chat_title: "محادثة مع المحقق",
    chat_placeholder: "اسأل عن نتائج التحقيق...",
    footer_note: "مِرصاد لا يتخذ أي إجراء تلقائي على أنظمتك — كل النتائج توصيات لدعم القرار الأمني.",
    empty_note: "لا يوجد",
    err_generic: "حدث خطأ أثناء التحقيق. يرجى المحاولة مرة أخرى.",
    err_need_input: "يرجى إرفاق ملف، أو لصق نص، أو إدخال رابط قبل بدء التحقيق.",
    model_warning: "تعذّر التحقق الكامل من مخرجات النموذج لهذه الحالة؛ يُعرض تحليل احتياطي حذر أدناه.",
    thinking: "المحقق يكتب…",
  },
  en: {
    lang_toggle_label: "AR",
    tagline: "With Mirsad's watchful eye, fraudsters are under watch.",
    hero_title: "Instant, evidence-driven security investigation",
    hero_sub: "Upload a phishing email, a suspicious link, a SIEM export, or a screenshot — Mirsad investigates it like an L2/L3 security analyst: what happened, how severe it is, and what to do next.",
    dz_text: "Drag files here or click to browse",
    dz_hint: "PDF · Screenshots/images · TXT/LOG/CSV/EML — up to 10MB per file",
    or_divider: "or",
    text_placeholder: "Paste an email body, log lines, or any textual evidence here...",
    url_placeholder: "Or enter a suspicious URL to investigate (optional)",
    untrusted_note: "Everything uploaded is treated as untrusted evidence for analysis only — no file is ever executed.",
    submit_btn: "Start investigation",
    scan_text: "Scanning evidence and building the investigation…",
    export_btn: "Export report",
    h_confirmed: "Confirmed evidence",
    h_events: "Suspicious events",
    h_iocs: "Indicators of compromise (IOCs)",
    ioc_type: "Type", ioc_value: "Value", ioc_context: "Context",
    h_timeline: "Timeline",
    h_hypotheses: "Hypotheses",
    h_gaps: "Evidence gaps",
    h_steps: "Next investigation steps",
    h_recs: "Defensive recommendations",
    h_notes: "Analyst notes",
    new_case_btn: "New investigation",
    chat_fab: "Ask the investigator",
    chat_title: "Chat with the investigator",
    chat_placeholder: "Ask about the investigation...",
    footer_note: "Mirsad never takes automated action on your systems — every result is a recommendation to support your security decision.",
    empty_note: "None",
    err_generic: "Something went wrong during the investigation. Please try again.",
    err_need_input: "Please attach a file, paste text, or enter a URL before starting.",
    model_warning: "The model's output could not be fully validated for this case; a cautious fallback analysis is shown below.",
    thinking: "Investigator is typing…",
  },
};

let state = {
  lang: "ar",
  theme: "dark",
  files: [],
  caseId: null,
};

/* ===========================================================
   i18n / theme wiring
   =========================================================== */
function applyLanguage(lang) {
  state.lang = lang;
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.body.style.fontFamily = lang === "ar" ? "var(--font-arabic)" : "var(--font-latin)";
  const dict = I18N[lang];
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (dict[key]) el.textContent = dict[key];
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    const key = el.getAttribute("data-i18n-placeholder");
    if (dict[key]) el.setAttribute("placeholder", dict[key]);
  });
  document.title = lang === "ar" ? "مِرصاد — محقّق الأمن السيبراني الذكي" : "Mirsad — AI Security Investigator";
  localStorage.setItem("mirsad_lang", lang);
}

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute("data-theme", theme);
  localStorage.setItem("mirsad_theme", theme);
}

function t(key) {
  return I18N[state.lang][key] || key;
}

/* ===========================================================
   Init
   =========================================================== */
document.addEventListener("DOMContentLoaded", () => {
  const savedLang = localStorage.getItem("mirsad_lang") || "ar";
  const savedTheme = localStorage.getItem("mirsad_theme") || "dark";
  applyLanguage(savedLang);
  applyTheme(savedTheme);

  document.getElementById("lang-toggle").addEventListener("click", () => {
    applyLanguage(state.lang === "ar" ? "en" : "ar");
  });
  document.getElementById("theme-toggle").addEventListener("click", () => {
    applyTheme(state.theme === "dark" ? "light" : "dark");
  });

  setupUpload();
  setupSubmit();
  setupChat();
});

/* ===========================================================
   Upload handling
   =========================================================== */
function setupUpload() {
  const dropzone = document.getElementById("dropzone");
  const input = document.getElementById("file-input");

  dropzone.addEventListener("click", () => input.click());
  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); input.click(); }
  });
  input.addEventListener("change", () => addFiles(Array.from(input.files)));

  ["dragenter", "dragover"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.add("dragover"); })
  );
  ["dragleave", "drop"].forEach((evt) =>
    dropzone.addEventListener(evt, (e) => { e.preventDefault(); dropzone.classList.remove("dragover"); })
  );
  dropzone.addEventListener("drop", (e) => {
    const dropped = Array.from(e.dataTransfer.files || []);
    addFiles(dropped);
  });
}

function addFiles(newFiles) {
  const MAX_FILES = 5;
  for (const f of newFiles) {
    if (state.files.length >= MAX_FILES) break;
    state.files.push(f);
  }
  renderFileList();
}

function renderFileList() {
  const list = document.getElementById("file-list");
  list.innerHTML = "";
  state.files.forEach((f, idx) => {
    const chip = document.createElement("div");
    chip.className = "file-chip";
    const sizeKb = (f.size / 1024).toFixed(0);
    chip.innerHTML = `<span>${escapeHtml(f.name)} · ${sizeKb}KB</span>`;
    const btn = document.createElement("button");
    btn.type = "button";
    btn.textContent = "×";
    btn.addEventListener("click", () => { state.files.splice(idx, 1); renderFileList(); });
    chip.appendChild(btn);
    list.appendChild(chip);
  });
}

/* ===========================================================
   Submit investigation
   =========================================================== */
function setupSubmit() {
  document.getElementById("submit-btn").addEventListener("click", submitInvestigation);
}

async function submitInvestigation() {
  const text = document.getElementById("text-input").value.trim();
  const url = document.getElementById("url-input").value.trim();
  hideError();

  if (!text && !url && state.files.length === 0) {
    showError(t("err_need_input"));
    return;
  }

  const btn = document.getElementById("submit-btn");
  btn.disabled = true;
  document.getElementById("input-card").hidden = true;
  document.getElementById("dashboard").hidden = true;
  document.getElementById("scan-state").hidden = false;

  const form = new FormData();
  form.append("text", text);
  form.append("url", url);
  form.append("language", state.lang);
  state.files.forEach((f) => form.append("files", f));

  try {
    const res = await fetch("/api/investigate", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.detail || t("err_generic"));
    }
    state.caseId = data.case_id;
    renderDashboard(data);
    document.getElementById("chat-fab").hidden = false;
  } catch (err) {
    document.getElementById("input-card").hidden = false;
    showError(err.message || t("err_generic"));
  } finally {
    btn.disabled = false;
    document.getElementById("scan-state").hidden = true;
  }
}

function showError(msg) {
  const el = document.getElementById("error-banner");
  el.textContent = msg;
  el.hidden = false;
}
function hideError() {
  document.getElementById("error-banner").hidden = true;
}

/* ===========================================================
   Dashboard rendering
   =========================================================== */
function verdictClass(v) {
  return { Safe: "v-safe", Suspicious: "v-suspicious", Malicious: "v-malicious", Inconclusive: "v-inconclusive" }[v] || "v-inconclusive";
}

function fillList(id, items, renderItem) {
  const ul = document.getElementById(id);
  ul.innerHTML = "";
  if (!items || items.length === 0) {
    const li = document.createElement("li");
    li.className = "empty-note";
    li.textContent = t("empty_note");
    ul.appendChild(li);
    return;
  }
  items.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = renderItem(item);
    ul.appendChild(li);
  });
}

function renderDashboard(data) {
  const r = data.result;

  document.getElementById("dashboard").hidden = false;

  const verdictBadge = document.getElementById("verdict-badge");
  verdictBadge.textContent = r.verdict;
  verdictBadge.className = "badge verdict " + verdictClass(r.verdict);

  document.getElementById("severity-badge").textContent = `${r.severity}`;
  document.getElementById("confidence-badge").textContent = `${r.confidence}`;

  document.getElementById("case-summary").textContent = r.case_summary;

  const warn = document.getElementById("model-warning");
  if (data.raw_model_error) {
    warn.hidden = false;
    warn.textContent = t("model_warning");
  } else {
    warn.hidden = true;
  }

  fillList("list-confirmed", r.confirmed_evidence, (e) =>
    `<strong>${escapeHtml(e.label)}</strong><span class="sub">${escapeHtml(e.detail)}</span>`
  );

  fillList("list-events", r.suspicious_events, (e) =>
    `<strong>${escapeHtml(e.title)}</strong><span class="sub">${escapeHtml(e.description)}</span>`
  );

  fillList("list-hypotheses", r.hypotheses, (h) =>
    `<strong>${escapeHtml(h.statement)}</strong><span class="sub">${escapeHtml(h.requires_validation)}</span>`
  );

  fillList("list-gaps", r.evidence_gaps, (g) => escapeHtml(g));
  fillList("list-steps", r.next_investigation_steps, (s) => escapeHtml(s));
  fillList("list-recs", r.recommendations, (s) => escapeHtml(s));

  const iocBody = document.getElementById("ioc-tbody");
  iocBody.innerHTML = "";
  if (!r.iocs || r.iocs.length === 0) {
    iocBody.innerHTML = `<tr><td colspan="3" class="empty-note">${t("empty_note")}</td></tr>`;
  } else {
    r.iocs.forEach((ioc) => {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${escapeHtml(ioc.type)}</td><td>${escapeHtml(ioc.value)}</td><td>${escapeHtml(ioc.context || "")}</td>`;
      iocBody.appendChild(tr);
    });
  }

  const timeline = document.getElementById("timeline-list");
  timeline.innerHTML = "";
  if (!r.timeline || r.timeline.length === 0) {
    timeline.innerHTML = `<li class="empty-note">${t("empty_note")}</li>`;
  } else {
    r.timeline.forEach((ev) => {
      const li = document.createElement("li");
      li.innerHTML = `${ev.timestamp ? `<span class="ts">${escapeHtml(ev.timestamp)}</span>` : ""}${escapeHtml(ev.description)}`;
      timeline.appendChild(li);
    });
  }

  document.getElementById("analyst-notes").textContent = r.analyst_notes || t("empty_note");

  document.getElementById("export-btn").onclick = () => window.print();
  document.getElementById("new-case-btn").onclick = resetToInput;

  document.getElementById("dashboard").scrollIntoView({ behavior: "smooth", block: "start" });
}

function resetToInput() {
  state.files = [];
  state.caseId = null;
  document.getElementById("text-input").value = "";
  document.getElementById("url-input").value = "";
  renderFileList();
  document.getElementById("dashboard").hidden = true;
  document.getElementById("input-card").hidden = false;
  document.getElementById("chat-fab").hidden = true;
  document.getElementById("chat-panel").hidden = true;
  document.getElementById("chat-messages").innerHTML = "";
  window.scrollTo({ top: 0, behavior: "smooth" });
}

/* ===========================================================
   Chat
   =========================================================== */
function setupChat() {
  document.getElementById("chat-fab").addEventListener("click", () => {
    document.getElementById("chat-panel").hidden = false;
    document.getElementById("chat-fab").hidden = true;
    document.getElementById("chat-input").focus();
  });
  document.getElementById("chat-close").addEventListener("click", () => {
    document.getElementById("chat-panel").hidden = true;
    document.getElementById("chat-fab").hidden = false;
  });
  document.getElementById("chat-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const msg = input.value.trim();
    if (!msg || !state.caseId) return;
    input.value = "";
    appendChatMessage("user", msg);
    const typingEl = appendChatMessage("bot", t("thinking"), true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_id: state.caseId, message: msg, language: state.lang }),
      });
      const data = await res.json();
      typingEl.remove();
      if (!res.ok) {
        appendChatMessage("bot", data.detail || t("err_generic"));
        return;
      }
      appendChatMessage("bot", data.reply);
    } catch (err) {
      typingEl.remove();
      appendChatMessage("bot", t("err_generic"));
    }
  });
}

function appendChatMessage(role, text, typing = false) {
  const container = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.className = "chat-msg " + (role === "user" ? "user" : "bot") + (typing ? " typing" : "");
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

/* ===========================================================
   Utils
   =========================================================== */
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}
