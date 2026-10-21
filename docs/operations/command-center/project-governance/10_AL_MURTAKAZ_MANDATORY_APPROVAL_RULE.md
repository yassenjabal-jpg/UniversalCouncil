# المرتكز — قاعدة الموافقة الإلزامية على جميع تغييرات البرنامج

Date: 2026-10-19  
Status: OWNER-DIRECTIVE / MANDATORY GOVERNANCE LAW  
Scope: UniversalCouncil Command Center + Android Owner Companion

## القاعدة العليا

**لا يتم تعديل أو اعتماد أو إكمال أو دمج أو إصدار أي جزء من البرنامج دون المرور عبر المرتكز والحصول على موافقة صريحة ومسجلة منه.**

تنطبق القاعدة على:

- UX/UI.
- Visual System.
- Motion/Animation.
- Role Sigils/Iconography.
- Components.
- Windows/WPF.
- Android.
- Autopilot.
- Council/Workshop project-local profiles.
- model/reasoning/fallback controls.
- Memory.
- Evidence.
- security/privacy.
- remote owner.
- tool integrations.
- project state.
- runtime architecture.
- tests/gates.
- documentation that changes product behavior or governance.
- releases/deployment.
- project-stage transitions.

## دورة التغيير الإلزامية

أي تغيير يمر بهذه الحالات فقط:

`PROPOSED`
→ `MURTAKAZ_REVIEW_REQUIRED`
→ `MURTAKAZ_REVIEWING`
→ one of:
- `APPROVED_BY_AL_MURTAKAZ`
- `RETURNED_FOR_CHANGES`
- `BLOCKED_BY_AL_MURTAKAZ`
- `OWNER_DECISION_REQUIRED`

بعد `APPROVED_BY_AL_MURTAKAZ` فقط يمكن أن ينتقل العمل إلى:
- implementation;
- adoption;
- completion;
- merge;
- release;
- next phase.

## قاعدة "التعديل قبل التنفيذ"

لا يكفي أن يراجع المرتكز النتيجة بعد تنفيذ التعديل.

قبل أي تعديل مادي يجب تسجيل:
- change_id;
- scope;
- reason;
- affected files/components;
- expected behavior;
- risk class;
- required reviewers from هيئة المرتكز;
- required craft owners from مشغل المرتكز.

ثم يصدر المرتكز:
- APPROVE_TO_IMPLEMENT;
- RETURN_FOR_REDESIGN;
- BLOCK;
- OWNER_DECISION_REQUIRED.

## قاعدة "الاعتماد بعد التنفيذ"

حتى إذا كان التعديل مصرحًا بتنفيذه، لا يصبح معتمدًا أو مكتملًا تلقائيًا.

بعد التنفيذ:
- يتم عرض النتيجة على المرتكز؛
- يجري التحقق من الأدلة والاختبارات/الصور/الحركة المناسبة؛
- يصدر قرار نهائي:
  - ACCEPT;
  - ACCEPT_WITH_MINOR_FIXES;
  - RETURN;
  - BLOCK;
  - OWNER_DECISION_REQUIRED.

## هيئة المرتكز

تراجع:
- truth/evidence;
- architecture;
- security/privacy;
- durability;
- cross-platform semantics;
- model/memory/evals;
- human impact;
- risks.

يتم تفعيل أصغر مجموعة لازمة من الأدوار، لكن لا يجوز تجاوز هيئة المرتكز بالكامل.

## مشغل المرتكز

يشرف على:
- visual;
- UX;
- interaction;
- motion;
- iconography;
- prototype;
- Windows/Android presentation;
- accessibility;
- visual fidelity.

أي تغيير بصري أو حركي يحتاج مراجعة مشغل المرتكز قبل اعتماده.

## Owner authority

المالك يبقى صاحب القرار النهائي.

لكن حتى Owner-directed changes:
- تُسجل كـ `OWNER_DIRECTIVE`;
- تمر عبر المرتكز لتحليل التأثير والمخاطر قبل التطبيق؛
- إذا أصر المالك على تجاوز توصية غير أمنية، يسجل القرار مع dissent.

المرتكز لا يستطيع تجاوز:
- Owner;
- execution authority;
- security hard blockers;
- evidence truth.

## لا موافقة ضمنية

هذه الحالات لا تعني موافقة:
- no objection;
- CI green;
- screenshot looks correct;
- prototype works;
- test passes;
- prior similar approval;
- Owner viewed it;
- role consensus.

الموافقة يجب أن تكون صريحة:
`APPROVED_BY_AL_MURTAKAZ`

## صلاحية الموافقة

كل موافقة مرتبطة بـ:
- change_id;
- artifact/version;
- scope;
- source revision/hash where applicable;
- decision;
- reviewers;
- evidence;
- timestamp;
- expiry/reopen triggers.

أي تعديل جوهري بعد الموافقة يعيد الحالة إلى:
`MURTAKAZ_REVIEW_REQUIRED`

## Reopen triggers

إعادة المراجعة إلزامية عند:
- تغيير متطلبات المالك;
- تغيير architecture;
- تغيير security/authority;
- تغيير model/provider/fallback semantics;
- تغيير data/schema;
- تغيير interaction;
- تغيير visual direction;
- تغيير motion semantics;
- تغيير target platform;
- فشل test/evidence previously used for approval;
- source drift;
- dependency/version change with material effect.

## حالة الطوارئ

لا يوجد bypass صامت.

إذا كان هناك إصلاح أمني عاجل:
- يسجل كـ `EMERGENCY_CHANGE`;
- يسمح فقط بالإجراء الأدنى لتقليل الضرر إذا كان التأخير أخطر;
- يصبح `PENDING_RETROSPECTIVE_MURTAKAZ_REVIEW`;
- لا يعتبر مكتملًا أو معتمدًا حتى مراجعة المرتكز.

## التنفيذ الآلي

أي Automation/Autopilot مستقبلي يجب أن يطبق هذه القاعدة كـpolicy gate.

لا يمكن للـAutopilot:
- تعديل;
- اعتماد;
- دمج;
- نشر;
- إغلاق مرحلة

دون Murtakaz approval receipt مناسب لنطاق الفعل.

## النتيجة

هذه القاعدة هي **Global Project Law** داخل Command Center.

أي عقد أو مرحلة أو أداة محلية تتعارض معها تعتبر غير صالحة داخل هذا المشروع.
