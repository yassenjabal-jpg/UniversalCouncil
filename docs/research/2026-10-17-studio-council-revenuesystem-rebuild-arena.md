# جلسة الاستوديو × المجلس — تطوير مجلس إعادة بناء «المطابقة»

**التاريخ:** 2026-10-17  
**الحالة:** OWNER-DIRECTED / PROJECT-SCOPED CANDIDATE  
**UniversalCouncil source pin:** `d807b2a68d88cfe8266145536daefcdc691ca984`  
**RevenueSystem source pin:** `6886fbb6398b67b366faf3ca446dbae54eb1ce4f`

## الهدف

تطوير المجلس ليصبح قادرًا على إعادة إنتاج RevenueSystem / «المطابقة» من جديد باستخدام منهج الاستوديو في العمل المرحلي، مع:

- GUI كمسار التنفيذ الأساسي داخل البرامج التفاعلية.
- Desktop Commander كطبقة دعم ثانوية للنظام والملفات وGit والبناء والاختبارات والسجلات والاسترداد.
- استخدام البرامج الفعلية المثبتة على YASSIN بدل استبدال العمل الحرفي بكود سريع أو ملفات نصية.
- طلب مساعدة المالك فقط عند وجود فجوة حقيقية في البرنامج/الأداة/الاعتماد/الصلاحية.
- الحفاظ على الصرامة المالية والبيانية والاختبارية الموجودة في RevenueSystem Council.

## ما دخل المجلس لتعلمه من الاستوديو

تمت مراجعة:
- `STUDIO_MASTER_PIPELINE.md`
- `MEDIA_PRODUCTION_CELL.md`
- `SPECIALIZED_TOOL_FIRST`
- `STUDIO_EXECUTION_RECOVERY.md`
- `HUMAN_ASSISTANCE_LANE.md`
- `HYBRID_EXECUTION_FABRIC.md`
- `hybrid_execution.json`
- YASSIN Control Bridge الفعلي على الجهاز.

### الآليات التي ثبت أنها قابلة للنقل إلى تطوير البرمجيات

1. **Specialized Tool First / Code Last for Craft**
   - لا يُستبدل Visual Studio/Blend/التطبيق الفعلي بسكربت لمجرد أن السكربت أسهل.
   - الكود الآلي يستخدم للتنسيق، الفحص، التكرار، الاختبارات، القياس، السجلات والـQC.
   - غياب أداة مناسبة ينتج `CAPABILITY_GAP` بدل ادعاء نجاح ضعيف.

2. **مرحلة واحدة ذات مالك واضح**
   - لكل مرحلة برنامج GUI أساسي ومالك وظيفي واضح.
   - DC لا يصبح محررًا خفيًا بدل البرنامج؛ يبقى طبقة دعم.

3. **Handoff + Lock**
   - المخرجات المقبولة تُقفل عند حدود المرحلة.
   - الفريق التالي لا يصلح بصمت ما كسره الفريق السابق؛ يصدر Return Ticket.

4. **UNKNOWN != SUCCESS**
   - تنفيذ الأمر أو ظهور process لا يثبت النجاح.
   - كل تغيير حالة يحتاج postcondition مستقلًا.

5. **Observe → Locate → Act → Observe → Verify**
   - نفس قاعدة الاستوديو تُطبق على Visual Studio، Blend، RevenueSystem runtime وأي نافذة إعدادات.

6. **Human Assistance**
   - إذا تعذر إجراء بسبب login، صلاحية، برنامج مفقود، قرار بصري/مالي يحتاج المالك، أو عطل لم تحله recovery؛ يطلب المجلس أصغر تدخل بشري ممكن فقط.

## جرد YASSIN الذي تم التحقق منه

### بيئة تطوير
- Visual Studio Community 2026 — موجود.
- Blend for Visual Studio — موجود.
- MSBuild — موجود.
- .NET SDK 10.0.401 / 10.0.402 — موجود.
- Windows Desktop Runtime 6/8/10 — موجود.
- Windows SDK — موجود.
- Git — موجود.
- Python 3.13 — موجود.
- Node.js 24 — موجود.

### برامج تصميم/إنتاج يمكن استخدامها عند الحاجة
- Adobe Photoshop 2025
- Adobe Illustrator 2025
- Adobe After Effects 2025
- Adobe Premiere Pro 2025
- Adobe Audition 2025
- Adobe Bridge 2025
- Adobe Media Encoder 2025
- Adobe Substance 3D family
- Adobe Animate / InDesign / Acrobat وغيرها

هذه البرامج ليست بديلًا عن IDE، لكنها متاحة لصناعة الأصول البصرية، الأيقونات، المواد التسويقية، أو أي artifact يحتاج أداة حرفية متخصصة.

### طبقة GUI الحقيقية
على YASSIN يوجد `CouncilVideoStudio\bridge\yassin_control` ويتضمن:
- Microsoft WinApp UI Automation.
- semantic inspect/search.
- invoke / set-value / focus / wait-for / scroll.
- screenshot و recording.
- click / drag / send-keys عند الحاجة.
- pywinauto fallback.
- `verified_action.py` للتقاط before/after والتحقق.
- audit log محلي.

إذن لا توجد حاليًا فجوة أساسية تمنع GUI-first لتطوير WPF.

## مراجعة المجلس — المواقف الأساسية

### Chair / Decision Controller
المطلوب ليس تحويل المجلس إلى استوديو فيديو، بل استيراد نظام التشغيل المنضبط: gates، locks، handoffs، recovery، capability gaps، وGUI-primary.

### Application Architecture Owner
اعترض على نسخ قاعدة "برنامج واحد فقط" حرفيًا؛ تطوير البرمجيات يحتاج IDE + build/tests/files. تم تعديلها إلى:
**برنامج GUI أساسي واحد للمرحلة، مع DC كطبقة دعم غير حرفية.**

### Requirements & Change Impact
طالب بأن يبدأ rebuild من current source + behavior archaeology، لا من تصاميم الذاكرة أو screenshots وحدها. أي سلوك مالي/بياني قديم يجب أن يثبت من source/tests/requirements قبل نقله.

### Financial Controls
اعترض على أي rebuild بصري يسبق تثبيت invariants المالية. العملات، السالب/المرتجعات، المطابقة، الحسابات والتقارير يجب أن تملك acceptance contracts قبل تنفيذ الواجهة.

### Data Integrity & Persistence
رفض إعادة بناء UI فوق persistence غير محددة. schema ownership، recovery، autosave، DB incarnation، imports، transaction boundaries يجب أن تُقفل كعقود قبل migration أو استبدال.

### Security
أكد أن GUI automation لا تدخل credentials ولا تعمل على بيانات الإنتاج/الشبكة الحساسة تلقائيًا.

### Test Architecture & QA Red Team
طالبا بثلاثة أنواع إثبات لكل vertical slice:
1. build/tests؛
2. runtime behavior؛
3. GUI evidence من التطبيق الفعلي.
أي واحد مفقود = ليس DONE.

### UI/UX + Interaction
طالبا بأن يتم تنفيذ الواجهة في Blend/Visual Studio والاختبار داخل التطبيق الفعلي، لا الاكتفاء بصور أو XAML مولد بدون مراجعة GUI. Figma يبقى مرجع تصميم مفيد، لكنه ليس إثبات التنفيذ.

### Performance & Observability
طالب بقياس freeze/startup/large grids/import/report paths بدل الاعتماد على الإحساس.

### Release & Environment
طالب بتثبيت source SHA وbranch وworking tree في بداية كل جلسة، وبقاء release/installer آخر مرحلة لا أولها.

### HR & Capability Director
قرر عدم طلب تثبيت برنامج جديد الآن؛ القدرات الأساسية متوفرة. أي أداة جديدة يجب أن تمر:
gap → candidate → security/overlap check → sandbox → owner adoption.

## القرار المشترك

تم اعتماد **RevenueSystem Rebuild Studio** كخلية مشروع متخصصة، لا كاستبدال للمجلس.

المجلس يحتفظ بسلطة:
- requirements;
- finance;
- data;
- security;
- architecture;
- test;
- QA;
- release.

ويستعير من الاستوديو:
- producer/control-plane;
- gated stages;
- one-primary-GUI-app per craft stage;
- handoff packets;
- return tickets;
- checkpoints;
- execution recovery;
- human assistance;
- specialized-tool-first.

## سياسة GUI + DC الخاصة بإعادة البناء

### GUI Primary
يستخدم في:
- Visual Studio 2026
- Blend for Visual Studio
- RevenueSystem runtime
- أي أداة تصميم/تحليل تفاعلية عند الحاجة

### DC Secondary
يستخدم في:
- git/fetch/branch/status/diff
- filesystem
- build/restore
- isolated tests
- logs
- process health
- artifact/hash checks
- crash diagnostics
- recovery support

### ممنوع
- إعلان نجاح من process/file فقط عندما الحالة GUI مهمة.
- تعديل XAML أو الكود عبر shell كبديل دائم عن IDE إذا كانت المرحلة معرفة بأنها GUI craft.
- blind clicking.
- coordinate-only control إذا توفر selector.
- replay لعملية UNKNOWN بلا reconciliation.
- لمس production LAN/DB بدون تفويض منفصل وصريح.

## بوابات إعادة الإنتاج

- **G0 — Source & Environment Lock**
- **G1 — Behavior / Invariants Lock**
- **G2 — UX + Architecture Ready Lock**
- **G3 — Vertical Slice Ready**
- **G4 — Build/Test Verified**
- **G5 — Runtime GUI Acceptance**
- **G6 — Finance/Data Integrity Clearance**
- **G7 — Regression/Performance Clearance**
- **G8 — Release Candidate Lock**
- **G9 — Owner Release Approval**

## طلبات البرامج

**لا يوجد طلب تثبيت إلزامي الآن.**

إذا ظهرت لاحقًا فجوة فعلية، تُرفع لك بحزمة صغيرة تحدد:
- اسم البرنامج؛
- سبب الحاجة؛
- لماذا الأدوات الحالية غير كافية؛
- هل هو مجاني/مدفوع؛
- المخاطر/الصلاحيات؛
- خطة اختبار sandbox؛
- معيار القبول؛
- بديل إن وجد.

## نتيجة الجلسة

المجلس أصبح لديه نموذج واضح لتحويل خبرته من "مراجعة واقتراح" إلى **خط إنتاج برمجي قابل للتحقق** مع GUI فعلي على YASSIN وDC كطبقة دعم، دون التخلي عن الحوكمة المالية والبيانية والاختبارية التي تميز RevenueSystem.
