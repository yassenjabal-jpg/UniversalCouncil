const roles = {
  owner: {
    title: "المالك",
    subtitle: "تحديد الاتجاه",
    why: "يضبط اتجاه العمل ويحوّل ما يحتاج قرار المالك إلى سياق واضح.",
    task: "لا توجد مهمة تشغيل حقيقية مرتبطة بهذا الـprototype.",
    state: "PROTOTYPE / UNKNOWN",
    findings: "هذه طبقة تفاعل فوق المرجع؛ لا تعرض نتائج فعلية.",
    dissent: "يظهر عند وجود اعتراض موثّق فقط."
  },
  strategy: {
    title: "الاستراتيجية",
    subtitle: "تحليل وفرص",
    why: "تحليل الاتجاهات والفرص والبدائل على مستوى المشروع.",
    task: "غير مرتبط بمهمة تشغيل حقيقية في الـprototype.",
    state: "PROTOTYPE / UNKNOWN",
    findings: "لا توجد نتائج فعلية في هذه النسخة.",
    dissent: "يُعرض عندما يوجد اعتراض أو بديل موثّق."
  },
  research: {
    title: "البحث",
    subtitle: "جمع الأدلة",
    why: "جمع الأدلة والمصادر وربطها بالقرارات والمخرجات.",
    task: "لا توجد جلسة بحث حقيقية في الـprototype.",
    state: "PROTOTYPE / UNKNOWN",
    findings: "Evidence links ستكون قابلة للفحص عند ربط runtime حقيقي.",
    dissent: "لا يوجد ادعاء حالي."
  },
  verification: {
    title: "التحقق",
    subtitle: "مراجعة الحقائق",
    why: "يتحقق من الادعاءات والحالة قبل إظهار VERIFIED أو نجاح.",
    task: "غير متصل بعملية تحقق حقيقية.",
    state: "PROTOTYPE / UNKNOWN",
    findings: "لا توجد حالة تحقق فعلية.",
    dissent: "أي تناقض مستقبلي يظهر هنا."
  },
  execution: {
    title: "التنفيذ",
    subtitle: "تحويل إلى عمل",
    why: "يحوّل العمل المعتمد إلى خطوات تنفيذية ويعرض الاعتماديات.",
    task: "التنفيذ الحقيقي غير مفعّل في هذا الـprototype.",
    state: "PROTOTYPE / DISABLED",
    findings: "هذه النسخة تختبر التفاعل فقط.",
    dissent: "الموانع التشغيلية تظهر هنا عند الربط."
  },
  creative: {
    title: "الإبداع",
    subtitle: "تصميم وإنتاج",
    why: "يمثل العمل الإبداعي والإنتاجي مع المحافظة على المرجع المعتمد.",
    task: "لا توجد أداة إنتاج متصلة من داخل هذا الـprototype.",
    state: "PROTOTYPE / UNKNOWN",
    findings: "لا يتم توليد أي تصميم بديل هنا.",
    dissent: "أي انحراف بصري يجب أن يعود للمراجعة."
  },
  data: {
    title: "البيانات",
    subtitle: "تحليل وقياس",
    why: "يعرض القياس والتحليل عندما توجد بيانات موثقة.",
    task: "لا توجد بيانات runtime فعلية في الـprototype.",
    state: "PROTOTYPE / UNKNOWN",
    findings: "الأرقام الظاهرة في المرجع مثال بصري وليست runtime truth.",
    dissent: "لا يوجد ادعاء حالي."
  },
  learning: {
    title: "التعلم",
    subtitle: "تطوير مستمر",
    why: "يلتقط الملاحظات والتحسينات القابلة لإعادة الاستخدام.",
    task: "غير متصل بدورة تعلم فعلية.",
    state: "PROTOTYPE / UNKNOWN",
    findings: "لا توجد ذاكرة تشغيلية مستنتجة من هذه الصورة.",
    dissent: "لا يوجد ادعاء حالي."
  }
};

const routeInfo = {
  "council-route": ["المجلس", "تحليل شامل ومجلس متخصص", "اختيار مسار المجلس يغيّر التوجيه فقط بعد ربط منطق prototype حقيقي."],
  "studio-route": ["الاستوديو", "إنتاج المحتوى والتصميم", "اختيار مسار الاستوديو لا يشغّل أدوات خارجية في هذه النسخة."],
  "auto-route": ["التنفيذ التلقائي", "من الفكرة إلى الإنجاز بشكل تلقائي", "Auto هنا تفاعل تجريبي فقط ولا يمنح execution authority."]
};

const projectInfo = {
  "smart-secretary": ["Smart Secretary V2", "مشروع نشط في المرجع", "فتح المشروع يجب أن ينقل إلى Living Project Workspace مع حفظ السياق."],
  "privacy": ["M2-A: Privacy", "بحث وتحليل", "المشروع يحافظ على أعضاءه وأدلته وإصداراته عند الانتقال."],
  "erasure": ["Erasure Contract", "مراجعة نهائية", "VERIFIED في المرجع مثال بصري ولا يُعامل كحقيقة runtime."]
};

const panelInfo = {
  "since-away": ["منذ آخر زيارة", "ملخص تغييرات ذات قيمة", "يفتح التفاصيل مع الحفاظ على المشروع/المصدر."],
  "needs-decision": ["يحتاج قرارك", "قرارات تمنع استمرار العمل", "كل عنصر يجب أن يوضح لماذا يحتاج قرارك وما أثر الاختيار."],
  "recent-results": ["النتائج الأخيرة", "مخرجات حديثة", "شارة VERIFIED لا تظهر في runtime الحقيقي إلا بدليل حالة."],
  autopilot: ["Autopilot", "الحالة التشغيلية", "يفتح Live Execution Detail عند وجود runtime حقيقي."],
  "tool-dock": ["Tool Dock", "أدوات المشروع", "يفرق بين Active وReady وUnavailable وUnknown."],
  "global-nav": ["التنقل العام", "وجهات Command Center", "النقر الحقيقي سيحفظ السياق الحالي بدل إعادة تحميل واجهة منفصلة."]
};

const inspector = document.getElementById("inspector");
const title = document.getElementById("inspector-title");
const kind = document.getElementById("inspector-kind");
const body = document.getElementById("inspector-body");
const close = document.getElementById("close-inspector");
const debugButton = document.getElementById("toggle-debug");
const toast = document.getElementById("toast");
let lastTrigger = null;

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("show");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => toast.classList.remove("show"), 2400);
}

function cards(entries) {
  return entries.map(([heading, value]) =>
    `<section class="context-card"><h3>${heading}</h3><p>${value}</p></section>`
  ).join("");
}

function openInspector(trigger, eyebrow, heading, content) {
  lastTrigger = trigger;
  kind.textContent = eyebrow;
  title.textContent = heading;
  body.innerHTML = content;
  inspector.classList.add("open");
  inspector.setAttribute("aria-hidden", "false");
  close.focus();
}

function roleContext(trigger, id) {
  const role = roles[id];
  openInspector(trigger, "ROLE CONTEXT", role.title, [
    cards([
      ["الوظيفة", role.subtitle],
      ["لماذا يظهر", role.why],
      ["المهمة الحالية", role.task],
      ["الحالة", role.state],
      ["النتائج", role.findings],
      ["أقوى اعتراض", role.dissent],
      ["الأدلة", "غير متصلة في prototype التفاعل."],
      ["النموذج / الاستدلال", "UNKNOWN — لا يتم اختلاق نموذج أو effort."]
    ]),
    `<div class="context-actions">
      <button type="button" data-demo-action="ask">اسأل عن نتيجة هذا العضو</button>
      <button type="button" data-demo-action="evidence" disabled>فتح الأدلة — غير متاح في prototype</button>
      <button type="button" data-demo-action="reasoning">Model & Reasoning Inspector</button>
      <button type="button" data-demo-action="history">مساهمات العضو في المشروع</button>
    </div>`
  ].join(""));
}

function reasoningContext(trigger, id) {
  const role = roles[id];
  openInspector(trigger, "MODEL & REASONING", role.title, cards([
    ["العضو", `${role.title} — ${role.subtitle}`],
    ["المزوّد / النموذج", "UNKNOWN"],
    ["مستوى الاستدلال", "UNKNOWN"],
    ["السبب", "لا يوجد task/runtime مربوط بهذه النسخة."],
    ["Fallback", "لا يتم اختلاق fallback chain."],
    ["الاستخدام / التكلفة", "غير متاح."]
  ]));
}

function genericContext(trigger, eyebrow, info) {
  openInspector(trigger, eyebrow, info[0], cards([
    ["السياق", info[1]],
    ["السلوك المقصود", info[2]],
    ["حقيقة الـprototype", "هذه طبقة تفاعل فوق الصورة المرجعية الأصلية؛ لا يوجد تنفيذ خارجي."]
  ]));
}

document.querySelectorAll(".hotspot").forEach((button) => {
  button.addEventListener("click", () => {
    const type = button.dataset.kind;
    const id = button.dataset.id;
    if (type === "member") return roleContext(button, id);
    if (type === "reasoning") return reasoningContext(button, id);
    if (type === "route") return genericContext(button, "ROUTING", routeInfo[id]);
    if (type === "project") return genericContext(button, "PROJECT CONTEXT", projectInfo[id]);
    if (type === "panel" || type === "region") return genericContext(button, "SEMANTIC REGION", panelInfo[id]);
    if (type === "action" && id === "start") {
      showToast("التنفيذ الحقيقي غير مفعّل — هذا prototype تفاعل فقط.");
    }
  });
});

const bodyElement = document.body;

bodyElement.addEventListener("click", (event) => {
  const action = event.target.closest("[data-demo-action]");
  if (!action) return;
  const name = action.dataset.demoAction;
  if (name === "reasoning") {
    showToast("Model & Reasoning = UNKNOWN في هذا الـprototype.");
  } else {
    showToast("تم اختبار المسار التفاعلي فقط؛ لا يوجد runtime action.");
  }
});

function closeInspector() {
  inspector.classList.remove("open");
  inspector.setAttribute("aria-hidden", "true");
  if (lastTrigger) lastTrigger.focus();
}

close.addEventListener("click", closeInspector);

debugButton.addEventListener("click", () => {
  const active = document.body.classList.toggle("debug-hotspots");
  debugButton.setAttribute("aria-pressed", String(active));
  debugButton.textContent = active ? "إخفاء مناطق التفاعل" : "إظهار مناطق التفاعل";
});

document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && inspector.classList.contains("open")) {
    closeInspector();
  }
  if ((event.key === "d" || event.key === "D") && !event.ctrlKey && !event.metaKey && !event.altKey) {
    const target = event.target;
    if (target instanceof HTMLInputElement || target instanceof HTMLTextAreaElement) return;
    debugButton.click();
  }
});
