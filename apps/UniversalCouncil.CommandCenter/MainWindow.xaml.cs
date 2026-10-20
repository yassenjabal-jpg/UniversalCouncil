using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Imaging;

namespace UniversalCouncil.CommandCenter;

public partial class MainWindow : Window
{
    private readonly MainWindowViewModel _viewModel;
    private FrameworkElement? _lastInteractionTarget;
    private string? _activeRoleId;
    private ScreenKind _currentScreen = ScreenKind.Home;
    private bool _nativeReferenceBlendEnabled;
    private const string OwnerPromptPlaceholder = "صف ما تريد إنجازه...";

    private static readonly IReadOnlyDictionary<ScreenKind, string> ScreenImages =
        new Dictionary<ScreenKind, string>
        {
            [ScreenKind.Home] = "01-home_owner_workspace.png",
            [ScreenKind.ProjectWorkspace] = "02-living_project_workspace.png",
            [ScreenKind.SoftwareAutopilot] = "03-software_autopilot_project.png",
            [ScreenKind.StudioProject] = "04-studio_project.png",
            [ScreenKind.DecisionMode] = "05-owner_decision_mode.png",
            [ScreenKind.RecoveryFork] = "06-checkpoint_recovery_fork.png",
            [ScreenKind.PulseStory] = "07-pulse_visual_project_story.png",
            [ScreenKind.WorkReceipt] = "08-project_complete_work_receipt.png",
        };

    private static readonly IReadOnlyDictionary<ScreenKind, string> ScreenLabels =
        new Dictionary<ScreenKind, string>
        {
            [ScreenKind.Home] = "Home / Owner Workspace",
            [ScreenKind.ProjectWorkspace] = "Living Project Workspace",
            [ScreenKind.SoftwareAutopilot] = "Software Autopilot Project",
            [ScreenKind.StudioProject] = "Studio Project",
            [ScreenKind.DecisionMode] = "Owner Decision Mode",
            [ScreenKind.RecoveryFork] = "Checkpoint / Recovery / Fork",
            [ScreenKind.PulseStory] = "Pulse Visual Project Story",
            [ScreenKind.WorkReceipt] = "Project Complete / Work Receipt",
        };

    private static readonly IReadOnlyDictionary<string, RoleContextData> Roles =
        new Dictionary<string, RoleContextData>(StringComparer.Ordinal)
        {
            ["owner"] = new(
                "المالك",
                "تحديد الاتجاه",
                "يضبط اتجاه العمل ويحوّل ما يحتاج قرار المالك إلى سياق واضح.",
                "لا توجد مهمة تشغيل حي مرتبطة بهذا السطح البصري الآن.",
                "UNKNOWN / UI INTERACTION LAYER",
                "يعرض دور المالك وسياق القرار فقط؛ لا توجد نتيجة تشغيل مختلقة.",
                "يظهر الاعتراض فقط عندما يكون موثقًا في حالة المشروع.",
                "الأدلة تُفتح من Evidence Peek عندما تكون متاحة.",
                "UNKNOWN — لا يوجد نموذج/effort مفبرك."),
            ["strategy"] = new(
                "الاستراتيجية",
                "تحليل وفرص",
                "تحلل الاتجاهات والفرص والبدائل على مستوى المشروع.",
                "لا توجد مهمة تشغيل حي مرتبطة بهذا العضو الآن.",
                "UNKNOWN / UI INTERACTION LAYER",
                "واجهة العضو جاهزة لاستقبال النتائج الفعلية من حالة المشروع.",
                "أي بديل أو اعتراض يظهر فقط إذا كان موجودًا في البيانات.",
                "Evidence links غير متوفرة في هذه المرحلة.",
                "UNKNOWN — لا يتم افتراض provider أو effort."),
            ["research"] = new(
                "البحث",
                "جمع الأدلة",
                "يجمع الأدلة ويربطها بالقرارات والمخرجات.",
                "لا توجد جلسة بحث حقيقية مرتبطة بالشاشة الحالية.",
                "UNKNOWN / UI INTERACTION LAYER",
                "عند ربط runtime ستظهر الأدلة والمصادر هنا.",
                "لا يوجد اعتراض حالي موثق.",
                "Evidence Peek جاهز دلاليًا لكنه بلا بيانات تشغيلية الآن.",
                "UNKNOWN."),
            ["verification"] = new(
                "التحقق",
                "مراجعة الحقائق",
                "يتحقق من الادعاءات والحالات قبل السماح بعرض VERIFIED.",
                "لا توجد عملية تحقق حية مرتبطة بالشاشة الحالية.",
                "UNKNOWN / UI INTERACTION LAYER",
                "لا يتم عرض نجاح أو تحقق من دون evidence-backed state.",
                "أي تناقض موثق سيظهر هنا.",
                "لا يوجد دليل حي متصل الآن.",
                "UNKNOWN."),
            ["execution"] = new(
                "التنفيذ",
                "تحويل إلى عمل",
                "يحوّل العمل المعتمد إلى خطوات تنفيذية عندما تسمح السلطة والحالة.",
                "التنفيذ الحي غير مفعّل من هذه الواجهة.",
                "DISABLED / AUTHORITY NOT GRANTED",
                "هذه الشاشة تطبق التفاعل فقط ولا ترسل أوامر تنفيذ.",
                "أي مانع تنفيذي يجب أن يظهر كسبب صريح.",
                "لا توجد أدلة تنفيذية حية.",
                "UNKNOWN."),
            ["creative"] = new(
                "الإبداع",
                "تصميم وإنتاج",
                "يمثل التصميم والإنتاج مع الالتزام بالمرجع البصري المعتمد.",
                "لا توجد أداة إنتاج خارجية مشغلة من هذه الشاشة.",
                "UNKNOWN / UI INTERACTION LAYER",
                "الهوية البصرية ثابتة والعضو جاهز لاستقبال مساهماته الفعلية.",
                "الانحراف البصري يعاد للمراجعة ولا يعتمد تلقائيًا.",
                "لا يوجد artifact evidence حي الآن.",
                "UNKNOWN."),
            ["data"] = new(
                "البيانات",
                "تحليل وقياس",
                "يعرض التحليل والقياس فقط عند توفر بيانات موثقة.",
                "لا توجد مهمة تحليل حي مرتبطة بالشاشة الحالية.",
                "UNKNOWN / UI INTERACTION LAYER",
                "الأرقام الموجودة في المرجع هي fixture بصري وليست runtime truth.",
                "لا يوجد اعتراض موثق.",
                "لا توجد بيانات evidence حية.",
                "UNKNOWN."),
            ["learning"] = new(
                "التعلم",
                "تطوير مستمر",
                "يلتقط التحسينات القابلة لإعادة الاستخدام بدون اختلاق ذاكرة تشغيلية.",
                "لا توجد دورة تعلم حية مرتبطة بالشاشة الحالية.",
                "UNKNOWN / UI INTERACTION LAYER",
                "جاهز لعرض الدروس بعد وجود أحداث ومراجعات حقيقية.",
                "لا يوجد اعتراض موثق.",
                "لا يوجد evidence حي.",
                "UNKNOWN."),
            ["evidence"] = new(
                "Evidence",
                "تحليل الأدلة",
                "يجمع ويفحص الأدلة المرتبطة بالمشروع الحالي.",
                "لا توجد مهمة حيّة محددة في طبقة المرجع.",
                "REFERENCE FIXTURE / UNKNOWN",
                "يفتح Evidence Role Context ويحافظ على provenance.",
                "لا يوجد اعتراض خاص بهذا الدور.",
                "Evidence Peek يصبح فعالًا فقط عند وجود evidence refs.",
                "UNKNOWN."),
            ["ux"] = new(
                "UX",
                "تصميم التجربة",
                "يمثل أثر القرارات على المستخدم وسير العمل.",
                "لا توجد مهمة runtime حية محددة.",
                "REFERENCE FIXTURE / UNKNOWN",
                "يعرض user-impact findings عند توفرها.",
                "اعتراضات تجربة المستخدم تظهر عند وجودها.",
                "الأدلة غير متصلة حاليًا.",
                "UNKNOWN."),
            ["redteam"] = new(
                "Red Team",
                "اختبار الثغرات والاعتراض",
                "يبحث عن أقوى اعتراض وفشل محتمل قبل الاعتماد.",
                "لا توجد مراجعة حية قيد التشغيل.",
                "REFERENCE FIXTURE / UNKNOWN",
                "المسار الدلالي جاهز لعرض blocker أو return ticket.",
                "أقوى اعتراض لا يُختلق؛ يظهر فقط من بيانات حقيقية.",
                "الأدلة غير متصلة حاليًا.",
                "UNKNOWN."),
            ["studio"] = new(
                "Studio",
                "التطوير والتصميم",
                "يتولى سياق الإنتاج المرئي أو التطويري المرتبط بالمشروع.",
                "لا توجد مرحلة إنتاج حية مفعلة من هذه الشاشة.",
                "REFERENCE FIXTURE / UNKNOWN",
                "يعرض artifact/handoff عند وجود pipeline فعلي.",
                "أي return ticket يبقى قابلًا للفحص.",
                "Artifact evidence غير متصل الآن.",
                "UNKNOWN."),
            ["security"] = new(
                "Security",
                "المراجعة الأمنية",
                "يفحص المخاطر والأمان والخصوصية ضمن نطاق المشروع.",
                "لا توجد مراجعة أمنية حية.",
                "REFERENCE FIXTURE / UNKNOWN",
                "لا يتم تحويل اللون أو الرمز إلى ادعاء أمان.",
                "المخاطر تظهر فقط من evidence حقيقي.",
                "الأدلة الأمنية غير متصلة الآن.",
                "UNKNOWN."),
            ["synthesis"] = new(
                "Synthesis",
                "دمج النتائج",
                "يجمع المساهمات دون حذف مسارات الاعتراض أو الأدلة.",
                "لا توجد عملية synthesis حية.",
                "REFERENCE FIXTURE / UNKNOWN",
                "يظهر البدائل والنتيجة المركبة عندما تتوفر.",
                "الاعتراض يبقى مستقلًا ولا يُمحى بالدمج.",
                "الأدلة غير متصلة الآن.",
                "UNKNOWN.")
        };

    internal MainWindow(MainWindowViewModel viewModel)
    {
        _viewModel = viewModel;
        InitializeComponent();
        DataContext = viewModel;
    }

    private string ExecutionTruthLabel =>
        _viewModel.ExecutionFabric.LiveDispatchEnabled
            ? "LIVE DISPATCH ENABLED"
            : "LIVE DISPATCH DISABLED";

    private void Role_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string roleId)
        {
            return;
        }

        OpenRoleContext(roleId, button, useHomeActivationRing: true);
    }

    private void Reasoning_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string roleId)
        {
            return;
        }

        OpenReasoningContext(roleId, button);
    }

    private void NativeRole_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string roleId)
        {
            return;
        }

        OpenRoleContext(roleId, button, useNativeActivation: true);
    }

    private void NativeReasoning_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string roleId)
        {
            return;
        }

        OpenReasoningContext(roleId, button);
    }

    private void CouncilActivity_Click(object sender, RoutedEventArgs e)
    {
        _lastInteractionTarget = sender as FrameworkElement;
        OpenGenericRegion(
            "نشاط المجلس",
            "Council Pulse",
            "يفتح سجل تفعيل الأعضاء ومسارات handoff والاعتراضات عند وجود أحداث حقيقية.",
            "REFERENCE FIXTURE / NATIVE RECONSTRUCTION SLICE");
    }

    private void OwnerPromptBox_GotKeyboardFocus(object sender, KeyboardFocusChangedEventArgs e)
    {
        if (sender is not TextBox textBox || textBox.Text != OwnerPromptPlaceholder)
        {
            return;
        }

        textBox.Text = string.Empty;
        textBox.Foreground = (Brush)FindResource("ReferenceInk");
    }

    private void OwnerPromptBox_LostKeyboardFocus(object sender, KeyboardFocusChangedEventArgs e)
    {
        if (sender is not TextBox textBox || !string.IsNullOrWhiteSpace(textBox.Text))
        {
            return;
        }

        textBox.Text = OwnerPromptPlaceholder;
        textBox.Foreground = (Brush)FindResource("ReferenceMuted");
    }

    private void ComposerControl_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string control)
        {
            return;
        }

        _lastInteractionTarget = button;

        switch (control)
        {
            case "attach":
                ShowNotice("الإرفاق واجهة Native جاهزة؛ لم يتم فتح منتقي ملفات أو إرسال ملف.");
                break;
            case "tools":
                OpenToolInspector("composer-tools");
                break;
            case "web":
                OpenGenericRegion(
                    "بحث في الويب",
                    "Composer routing preference",
                    "هذا التحكم يحدد تفضيل البحث فقط عند توصيل execution/runtime؛ لا يبدأ بحثًا من الواجهة الحالية.",
                    "UI INTERACTION LAYER");
                break;
            case "model":
                OpenGenericRegion(
                    "اختيار النموذج",
                    "Owner-controlled model selection",
                    "الموديل الظاهر في المرجع Fixture بصري. الاختيار الفعلي يبقى تحت تحكم المالك ولا يُفترض من الصورة.",
                    _viewModel.ProviderConnectionLabel);
                break;
            case "reasoning":
                OpenGenericRegion(
                    "مستوى التفكير",
                    "Reasoning control",
                    "المستوى الظاهر في المرجع Fixture بصري، ولا يعني أن effort فعليًا مفعّل حتى يصل state موثوق.",
                    "UNKNOWN / OWNER CONTROLLED");
                break;
        }
    }

    private void Route_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string route)
        {
            return;
        }

        _lastInteractionTarget = button;

        if (route == "studio-route")
        {
            NavigateTo(ScreenKind.StudioProject);
            return;
        }

        if (route == "auto-route")
        {
            NavigateTo(ScreenKind.SoftwareAutopilot);
            return;
        }

        OpenDrawer(
            "ROUTING",
            "المجلس",
            "تحليل ومراجعة متعددة الأدوار",
            "هذا الاختيار يحدد مسار العمل دلاليًا؛ لا يفعّل صلاحية تنفيذ حي.",
            "بانتظار أمر مالك صريح وسياق مشروع صالح.",
            ExecutionTruthLabel,
            "يعرض المسار المقترح فقط؛ لا توجد خطوة نفذت من هذا الاختيار.",
            "أي blocker أو authority gate يجب أن يظهر قبل البدء.",
            "لا توجد أدلة تشغيلية مرتبطة بالاختيار بعد.",
            $"Fallback: {_viewModel.ModelFallbackLabel}");
    }

    private void Project_Click(object sender, RoutedEventArgs e)
    {
        _lastInteractionTarget = sender as FrameworkElement;
        NavigateTo(ScreenKind.ProjectWorkspace);
    }

    private void Region_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string regionId)
        {
            return;
        }

        _lastInteractionTarget = button;

        if (regionId == "autopilot")
        {
            NavigateTo(ScreenKind.SoftwareAutopilot);
            return;
        }

        if (regionId == "needs-decision")
        {
            NavigateTo(ScreenKind.DecisionMode);
            return;
        }

        if (regionId == "recent-results")
        {
            NavigateTo(ScreenKind.PulseStory);
            return;
        }

        var data = regionId switch
        {
            "since-away" => new RegionContext(
                "منذ آخر زيارة",
                "التحديثات ذات القيمة",
                "ملخص زمني يحافظ على المشروع والمصدر عند فتح التفاصيل.",
                "REFERENCE FIXTURE"),
            "tool-dock" => new RegionContext(
                "Tool Dock",
                "الأدوات",
                "يفرق بين READY / ACTIVE / BLOCKED / UNKNOWN ويفتح Tool Inspector.",
                ExecutionTruthLabel),
            _ => new RegionContext(
                "التنقل العام",
                "Command Center Navigation",
                "يحفظ السياق الحالي عند الانتقال إلى وجهة أخرى.",
                "UI INTERACTION LAYER")
        };

        OpenGenericRegion(data.Title, data.Subtitle, data.Explanation, data.State);
    }

    private void Start_Click(object sender, RoutedEventArgs e)
    {
        _lastInteractionTarget = sender as FrameworkElement;
        ShowNotice("التنفيذ الحي غير مفعل من Home البصرية. تم اختبار press/feedback فقط بدون إرسال أي أمر.");
    }

    private void OpenRoleContext(
        string roleId,
        FrameworkElement source,
        bool useHomeActivationRing = false,
        bool useNativeActivation = false)
    {
        if (!Roles.TryGetValue(roleId, out var role))
        {
            return;
        }

        _activeRoleId = roleId;
        _lastInteractionTarget = source;

        if (useNativeActivation && source is Button nativeButton)
        {
            AnimateNativeRoleButton(nativeButton);
        }
        else if (useHomeActivationRing && source is Button button)
        {
            ShowRoleActivation(button);
        }
        else
        {
            ShowSecondaryActivation(source);
        }

        OpenDrawer(
            "ROLE CONTEXT",
            role.Title,
            role.Subtitle,
            role.Why,
            role.Task,
            role.State,
            role.Findings,
            role.Dissent,
            role.Evidence,
            role.Reasoning);
    }

    private void OpenReasoningContext(string roleId, FrameworkElement source)
    {
        if (!Roles.TryGetValue(roleId, out var role))
        {
            return;
        }

        _activeRoleId = roleId;
        _lastInteractionTarget = source;
        OpenDrawer(
            "MODEL & REASONING",
            role.Title,
            role.Subtitle,
            "تفاصيل النموذج والاستدلال لهذا العضو.",
            "لا توجد مهمة runtime حية مرتبطة بهذه الشاشة.",
            "UNKNOWN",
            $"Provider connection: {_viewModel.ProviderConnectionLabel}",
            "لا يتم عرض fallback أو effort غير معروف كأنه فعال.",
            "Usage / cost غير متاح من هذه الطبقة.",
            "Model: UNKNOWN\nEffort: UNKNOWN\nFallback: " + _viewModel.ModelFallbackLabel);
    }

    private void NavigateTo(ScreenKind screen)
    {
        _currentScreen = screen;
        _activeRoleId = null;
        CloseDrawerImmediate();

        var imageName = ScreenImages[screen];
        var uri = new Uri(
            $"/UniversalCouncil.CommandCenter;component/Assets/VisualReferences/{imageName}",
            UriKind.Relative);
        ReferenceImage.Source = new BitmapImage(uri);
        AutomationProperties.SetName(
            ReferenceImage,
            $"المرجع البصري المعتمد — {ScreenLabels[screen]}");

        var isHome = screen == ScreenKind.Home;
        InteractionCanvas.Visibility = isHome ? Visibility.Visible : Visibility.Collapsed;
        NativeHomeReconstructionRoot.Visibility = isHome ? Visibility.Visible : Visibility.Collapsed;
        NativeHomeReconstructionRoot.Opacity = _nativeReferenceBlendEnabled && isHome ? 0.46 : 1;
        RoleActivationRing.Visibility = Visibility.Collapsed;
        SecondaryInteractionCanvas.Visibility = isHome ? Visibility.Collapsed : Visibility.Visible;
        SecondaryInteractionCanvas.Children.Clear();

        if (!isHome)
        {
            BuildSecondaryInteractions(screen);
        }

        if (SystemParameters.ClientAreaAnimation)
        {
            ReferenceImage.Opacity = 0.68;
            ReferenceImage.BeginAnimation(
                OpacityProperty,
                new DoubleAnimation(0.68, 1, TimeSpan.FromMilliseconds(220))
                {
                    EasingFunction = new CubicEase { EasingMode = EasingMode.EaseOut }
                });
        }
        else
        {
            ReferenceImage.Opacity = 1;
        }
    }

    private void BuildSecondaryInteractions(ScreenKind screen)
    {
        foreach (var hotspot in GetHotspots(screen))
        {
            var button = new Button
            {
                Width = hotspot.Width,
                Height = hotspot.Height,
                Tag = hotspot.Id,
                ToolTip = hotspot.Label,
                Style = (Style)FindResource(
                    hotspot.Kind == HotspotKind.Reasoning
                        ? "ReasoningHotspotStyle"
                        : "HotspotButtonStyle"),
            };

            AutomationProperties.SetName(button, hotspot.Label);
            Canvas.SetLeft(button, hotspot.X);
            Canvas.SetTop(button, hotspot.Y);
            button.Click += (_, _) => HandleSecondaryHotspot(hotspot, button);
            SecondaryInteractionCanvas.Children.Add(button);
        }
    }

    private void HandleSecondaryHotspot(HotspotDefinition hotspot, Button source)
    {
        _lastInteractionTarget = source;

        switch (hotspot.Kind)
        {
            case HotspotKind.Navigate:
                NavigateTo(ParseScreen(hotspot.Id));
                break;
            case HotspotKind.Role:
                OpenRoleContext(hotspot.Id, source);
                break;
            case HotspotKind.Reasoning:
                OpenReasoningContext(hotspot.Id, source);
                break;
            case HotspotKind.Filmstrip:
                OpenVersionInspector(hotspot.Id);
                break;
            case HotspotKind.Tool:
                OpenToolInspector(hotspot.Id);
                break;
            case HotspotKind.DecisionAction:
                HandleDecisionAction(hotspot.Id);
                break;
            case HotspotKind.RecoveryAction:
                HandleRecoveryAction(hotspot.Id);
                break;
            case HotspotKind.Artifact:
                OpenArtifact(hotspot.Id);
                break;
            case HotspotKind.Stage:
                OpenStageDetail(hotspot.Id);
                break;
            case HotspotKind.Pulse:
                OpenPulseDetail(hotspot.Id);
                break;
            default:
                OpenScreenRegion(hotspot.Id, hotspot.Label);
                break;
        }
    }

    private void OpenScreenRegion(string id, string label)
    {
        if (id == "decision-stack")
        {
            NavigateTo(ScreenKind.DecisionMode);
            return;
        }

        if (id == "recovery-entry")
        {
            NavigateTo(ScreenKind.RecoveryFork);
            return;
        }

        if (id == "pulse-entry")
        {
            NavigateTo(ScreenKind.PulseStory);
            return;
        }

        if (id == "receipt-entry")
        {
            NavigateTo(ScreenKind.WorkReceipt);
            return;
        }

        var explanation = id switch
        {
            "project-header" => "Project Context يحافظ على هوية المشروع والمرحلة والحالة الحالية.",
            "autopilot-rail" => "Autopilot Current Marker يفتح تفاصيل المرحلة والمهمة والأداة وآخر checkpoint.",
            "routing-context" => "يعرض سبب تفعيل الأدوار ومسار التوجيه الحالي.",
            "execution-info" => "يعرض التنفيذ الفعلي فقط عند وجود state موثوق.",
            "studio-player" => "Artifact Viewer للمعاينة الحالية مع provenance وحالة الجودة.",
            "studio-timeline" => "Stage / media timeline مع markers وhandoff context.",
            "decision-surface" => "Decision Context: السؤال، لماذا الآن، التوصية، الاعتراض والأثر.",
            "evidence-peek" => "Evidence Peek لا يغيّر truth state ويعرض المصدر والملف المرتبط.",
            "checkpoint-timeline" => "Checkpoint Inspector يحفظ التاريخ ولا يفترض نجاح الاسترجاع.",
            "branch-compare" => "Branch comparison يحافظ على A/B بدون ترجيح بصري قبل القرار.",
            "story-timeline" => "Pulse story timeline يربط التغيير بالسبب والدليل وما سيحدث لاحقًا.",
            "work-receipt" => "Work Receipt يجمع المطلوب والمنجز والأدلة والأدوات والقرارات.",
            _ => "عنصر دلالي من المرجع البصري المعتمد."
        };

        OpenGenericRegion(label, ScreenLabels[_currentScreen], explanation, "REFERENCE FIXTURE / INTERACTION READY");
    }

    private void OpenVersionInspector(string id) =>
        OpenDrawer(
            "VERSION INSPECTOR",
            "شريط إصدارات المشروع",
            "Filmstrip / history",
            "الإطارات المرئية تمثل إصدارات قابلة للفحص والمقارنة.",
            "لا يوجد إصدار runtime مختار من هذه الطبقة.",
            "REFERENCE FIXTURE",
            "Compare / Open Artifact / Ask / Evidence جاهزة دلاليًا.",
            "Restore ليس فعلًا افتراضيًا ولا يحدث بدون حوكمة.",
            "Provenance سيظهر عند ربط artifact state.",
            "Model / Reasoning يظهر لكل إصدار عند توفره.");

    private void OpenToolInspector(string id) =>
        OpenDrawer(
            "TOOL INSPECTOR",
            id == "tool-dock" ? "Tool Dock" : "الأدوات النشطة",
            "Ready / Active / Connected / Unknown / Blocked",
            "الأداة المرئية قابلة للفحص وليست أيقونة زخرفية.",
            "لا توجد مهمة tool runtime مفترضة.",
            ExecutionTruthLabel,
            "Open related artifact / diagnostics تصبح فعالة حسب السلطة.",
            "الأداة لا تُعرض Active إذا أصبحت حالتها UNKNOWN.",
            "Last verified timestamp/evidence يظهر عند توفره.",
            "N/A");

    private void HandleDecisionAction(string action)
    {
        var label = action switch
        {
            "approve" => "الموافقة",
            "request-changes" => "طلب تعديلات",
            "reject" => "رفض",
            "ask" => "طرح سؤال",
            "inspect-evidence" => "فحص الأدلة",
            _ => action
        };

        if (action == "inspect-evidence")
        {
            OpenScreenRegion("evidence-peek", "Evidence Peek");
            return;
        }

        if (action == "ask")
        {
            ShowNotice("Ask This يحتفظ بسؤال القرار والمشروع والأدلة في السياق، بدون تنفيذ قرار.");
            return;
        }

        ShowNotice($"{label}: تم اختبار تفاعل القرار فقط. لم يتم تسجيل قرار أو استئناف تنفيذ حي.");
    }

    private void HandleRecoveryAction(string action)
    {
        var message = action switch
        {
            "restore" => "طلب الاسترجاع لا يعني RESTORED. النجاح يظهر فقط بعد CHECKPOINT_RESTORED_VERIFIED.",
            "fork" => "إنشاء Fork يحافظ على الأصل ويبدأ فرعًا جديدًا؛ لا يوجد إنشاء runtime من هذه الطبقة.",
            "promote" => "Promote branch يحتاج اختيارًا محكومًا ونتيجة تحقق قبل اعتماده.",
            "delete" => "الحذف فعل تدميري ويحتاج تأكيدًا وسلطة خادمية؛ لم يُنفذ شيء.",
            _ => "تم اختبار مسار Recovery/Fork فقط بدون تعديل الحالة."
        };

        ShowNotice(message);
    }

    private void OpenArtifact(string id) =>
        OpenDrawer(
            "ARTIFACT VIEWER",
            "المخرج / الأثر",
            id,
            "يفتح المعاينة والمقارنة والمصدر وprovenance.",
            "لا يوجد تنزيل أو فتح أداة خارجية تلقائيًا.",
            "REFERENCE FIXTURE",
            "الـartifact يبقى قابلًا للفحص بعد handoff أو return.",
            "Request Change يبقى مسارًا صريحًا عند وجوده.",
            "Evidence/provenance غير متصلين الآن.",
            "N/A");

    private void OpenStageDetail(string id) =>
        OpenDrawer(
            "STAGE DETAIL",
            "مرحلة العمل",
            id,
            "يعرض entry condition وartifact الحالي وQC وhandoff والمرحلة التالية.",
            "لا توجد مرحلة runtime مفعلة من هذه الطبقة.",
            "REFERENCE FIXTURE",
            "Stage transition لا يُعتبر ناجحًا بدون حدث فعلي.",
            "Return Ticket يبقى ظاهرًا إذا رفضت المرحلة التالية.",
            "Checkpoint/evidence يظهران عند توفرهما.",
            "N/A");

    private void OpenPulseDetail(string id) =>
        OpenDrawer(
            "PULSE DETAIL",
            "Pulse",
            id,
            "يعرض ما تغير، لماذا، وما الذي سيحدث لاحقًا.",
            "لا توجد promotion حية من هذه الطبقة.",
            "REFERENCE FIXTURE",
            "Create Task / Decision / Research تبقى actions دلالية.",
            "الـPulse الأصلي يبقى مرتبطًا كمصدر بعد التحويل.",
            "Truth badge يفتح Evidence Peek عند توفر الدليل.",
            "N/A");

    private void OpenGenericRegion(string title, string subtitle, string explanation, string state) =>
        OpenDrawer(
            "SEMANTIC REGION",
            title,
            subtitle,
            explanation,
            "لا توجد مهمة مستقلة داخل هذا العنصر الآن.",
            state,
            "تم تفعيل المسار التفاعلي فقط.",
            "لا يوجد اعتراض مرتبط بهذه المنطقة.",
            "Evidence available only when supplied by the underlying state.",
            "N/A");

    private void AskThis_Click(object sender, RoutedEventArgs e)
    {
        var context = _activeRoleId is not null && Roles.TryGetValue(_activeRoleId, out var role)
            ? role.Title
            : DrawerTitle.Text;
        ShowNotice($"Ask This سيحمل السياق تلقائيًا: {context}. لا توجد محادثة runtime مربوطة بعد.");
    }

    private void OpenEvidence_Click(object sender, RoutedEventArgs e) =>
        OpenScreenRegion("evidence-peek", "Evidence Peek");

    private void ReasoningInspector_Click(object sender, RoutedEventArgs e)
    {
        if (_activeRoleId is not null && Roles.ContainsKey(_activeRoleId))
        {
            OpenReasoningContext(_activeRoleId, CloseDrawerButton);
            return;
        }

        ShowNotice("Model & Reasoning غير متاح لهذا العنصر.");
    }

    private void ContributionHistory_Click(object sender, RoutedEventArgs e) =>
        ShowNotice("Contribution History سيعرض مساهمات العنصر المرتبطة بالمشروع عندما تتوفر أحداث فعلية.");

    private void CloseDrawer_Click(object sender, RoutedEventArgs e) => CloseDrawer();

    private void Window_PreviewKeyDown(object sender, KeyEventArgs e)
    {
        if (e.Key == Key.Escape && ContextDrawer.Visibility == Visibility.Visible)
        {
            CloseDrawer();
            e.Handled = true;
            return;
        }

        if (!Keyboard.Modifiers.HasFlag(ModifierKeys.Control))
        {
            return;
        }

        if (Keyboard.Modifiers.HasFlag(ModifierKeys.Shift) &&
            e.Key == Key.O &&
            _currentScreen == ScreenKind.Home)
        {
            _nativeReferenceBlendEnabled = !_nativeReferenceBlendEnabled;
            NativeHomeReconstructionRoot.Opacity = _nativeReferenceBlendEnabled ? 0.46 : 1;
            ShowNotice(
                _nativeReferenceBlendEnabled
                    ? "وضع مقارنة Overlay مفعّل: المرجع الأصلي ظاهر تحت Council Pulse الـNative."
                    : "وضع المقارنة متوقف: Council Pulse الـNative بكامل العتامة.");
            e.Handled = true;
            return;
        }

        var screen = e.Key switch
        {
            Key.D1 => ScreenKind.Home,
            Key.D2 => ScreenKind.ProjectWorkspace,
            Key.D3 => ScreenKind.SoftwareAutopilot,
            Key.D4 => ScreenKind.StudioProject,
            Key.D5 => ScreenKind.DecisionMode,
            Key.D6 => ScreenKind.RecoveryFork,
            Key.D7 => ScreenKind.PulseStory,
            Key.D8 => ScreenKind.WorkReceipt,
            _ => (ScreenKind?)null
        };

        if (screen.HasValue)
        {
            NavigateTo(screen.Value);
            e.Handled = true;
        }
    }

    private void OpenDrawer(
        string eyebrow,
        string title,
        string subtitle,
        string why,
        string task,
        string state,
        string findings,
        string dissent,
        string evidence,
        string reasoning)
    {
        DrawerEyebrow.Text = eyebrow;
        DrawerTitle.Text = title;
        DrawerSubtitle.Text = subtitle;
        DrawerWhy.Text = why;
        DrawerTask.Text = task;
        DrawerState.Text = state;
        DrawerFindings.Text = findings;
        DrawerDissent.Text = dissent;
        DrawerEvidence.Text = evidence;
        DrawerReasoning.Text = reasoning;

        ContextDrawer.Visibility = Visibility.Visible;

        if (!SystemParameters.ClientAreaAnimation)
        {
            DrawerTransform.X = 0;
            ContextDrawer.Opacity = 1;
            CloseDrawerButton.Focus();
            return;
        }

        DrawerTransform.X = 430;
        ContextDrawer.Opacity = 0;

        var ease = new CubicEase { EasingMode = EasingMode.EaseOut };
        DrawerTransform.BeginAnimation(
            System.Windows.Media.TranslateTransform.XProperty,
            new DoubleAnimation(430, 0, TimeSpan.FromMilliseconds(240)) { EasingFunction = ease });
        ContextDrawer.BeginAnimation(
            OpacityProperty,
            new DoubleAnimation(0, 1, TimeSpan.FromMilliseconds(180)));

        CloseDrawerButton.Focus();
    }

    private void CloseDrawer()
    {
        if (ContextDrawer.Visibility != Visibility.Visible)
        {
            return;
        }

        if (!SystemParameters.ClientAreaAnimation)
        {
            CloseDrawerImmediate();
            RestoreInteractionFocus();
            return;
        }

        var ease = new CubicEase { EasingMode = EasingMode.EaseIn };
        var slide = new DoubleAnimation(0, 430, TimeSpan.FromMilliseconds(190))
        {
            EasingFunction = ease
        };
        slide.Completed += (_, _) =>
        {
            CloseDrawerImmediate();
            RestoreInteractionFocus();
        };

        DrawerTransform.BeginAnimation(System.Windows.Media.TranslateTransform.XProperty, slide);
        ContextDrawer.BeginAnimation(
            OpacityProperty,
            new DoubleAnimation(1, 0, TimeSpan.FromMilliseconds(150)));
    }

    private void CloseDrawerImmediate()
    {
        ContextDrawer.BeginAnimation(OpacityProperty, null);
        DrawerTransform.BeginAnimation(System.Windows.Media.TranslateTransform.XProperty, null);
        ContextDrawer.Visibility = Visibility.Collapsed;
        ContextDrawer.Opacity = 0;
        DrawerTransform.X = 430;
    }

    private void RestoreInteractionFocus() => _lastInteractionTarget?.Focus();

    private static void AnimateNativeRoleButton(Button button)
    {
        if (!SystemParameters.ClientAreaAnimation)
        {
            return;
        }

        button.RenderTransformOrigin = new Point(0.5, 0.5);
        var scale = new ScaleTransform(1, 1);
        button.RenderTransform = scale;

        var pulse = new DoubleAnimationUsingKeyFrames();
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(
            1,
            KeyTime.FromTimeSpan(TimeSpan.Zero)));
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(
            1.045,
            KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(90))));
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(
            1,
            KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(260))));

        scale.BeginAnimation(ScaleTransform.ScaleXProperty, pulse);
        scale.BeginAnimation(ScaleTransform.ScaleYProperty, pulse);
    }

    private void ShowRoleActivation(Button button)
    {
        var left = Canvas.GetLeft(button);
        var top = Canvas.GetTop(button);

        Canvas.SetLeft(RoleActivationRing, left - 5);
        Canvas.SetTop(RoleActivationRing, top - 5);
        RoleActivationRing.Visibility = Visibility.Visible;

        if (!SystemParameters.ClientAreaAnimation)
        {
            RoleActivationRing.Opacity = 0.75;
            return;
        }

        RoleActivationRing.Opacity = 0;
        var pulse = new DoubleAnimationUsingKeyFrames();
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(0, KeyTime.FromTimeSpan(TimeSpan.Zero)));
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(0.9, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(90))));
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(0.42, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(320))));
        RoleActivationRing.BeginAnimation(OpacityProperty, pulse);
    }

    private void ShowSecondaryActivation(FrameworkElement target)
    {
        var left = Canvas.GetLeft(target);
        var top = Canvas.GetTop(target);
        if (double.IsNaN(left) || double.IsNaN(top))
        {
            return;
        }

        var ring = new Border
        {
            Width = target.Width + 10,
            Height = target.Height + 10,
            BorderBrush = new SolidColorBrush(Color.FromArgb(180, 47, 107, 255)),
            BorderThickness = new Thickness(3),
            CornerRadius = new CornerRadius(18),
            IsHitTestVisible = false,
            Opacity = SystemParameters.ClientAreaAnimation ? 0 : 0.7
        };
        Canvas.SetLeft(ring, left - 5);
        Canvas.SetTop(ring, top - 5);
        Panel.SetZIndex(ring, 20);
        SecondaryInteractionCanvas.Children.Add(ring);

        if (!SystemParameters.ClientAreaAnimation)
        {
            return;
        }

        var pulse = new DoubleAnimationUsingKeyFrames();
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(0, KeyTime.FromTimeSpan(TimeSpan.Zero)));
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(0.9, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(90))));
        pulse.KeyFrames.Add(new EasingDoubleKeyFrame(0, KeyTime.FromTimeSpan(TimeSpan.FromMilliseconds(420))));
        pulse.Completed += (_, _) => SecondaryInteractionCanvas.Children.Remove(ring);
        ring.BeginAnimation(OpacityProperty, pulse);
    }

    private async void ShowNotice(string message)
    {
        PrototypeNoticeText.Text = message;
        PrototypeNotice.Visibility = Visibility.Visible;
        PrototypeNotice.Opacity = 1;

        await Task.Delay(2600);

        if (!IsLoaded)
        {
            return;
        }

        if (!SystemParameters.ClientAreaAnimation)
        {
            PrototypeNotice.Visibility = Visibility.Collapsed;
            return;
        }

        var fade = new DoubleAnimation(1, 0, TimeSpan.FromMilliseconds(180));
        fade.Completed += (_, _) => PrototypeNotice.Visibility = Visibility.Collapsed;
        PrototypeNotice.BeginAnimation(OpacityProperty, fade);
    }

    private static ScreenKind ParseScreen(string id) => id switch
    {
        "home" => ScreenKind.Home,
        "project" => ScreenKind.ProjectWorkspace,
        "autopilot" => ScreenKind.SoftwareAutopilot,
        "studio" => ScreenKind.StudioProject,
        "decision" => ScreenKind.DecisionMode,
        "recovery" => ScreenKind.RecoveryFork,
        "pulse" => ScreenKind.PulseStory,
        "receipt" => ScreenKind.WorkReceipt,
        _ => ScreenKind.Home
    };

    private static IReadOnlyList<HotspotDefinition> GetHotspots(ScreenKind screen) => screen switch
    {
        ScreenKind.ProjectWorkspace => ProjectWorkspaceHotspots,
        ScreenKind.SoftwareAutopilot => SoftwareAutopilotHotspots,
        ScreenKind.StudioProject => StudioProjectHotspots,
        ScreenKind.DecisionMode => DecisionModeHotspots,
        ScreenKind.RecoveryFork => RecoveryForkHotspots,
        ScreenKind.PulseStory => PulseStoryHotspots,
        ScreenKind.WorkReceipt => WorkReceiptHotspots,
        _ => []
    };

    private static readonly IReadOnlyList<HotspotDefinition> ProjectWorkspaceHotspots =
    [
        Nav(1464, 65, 66, 74, "home", "الرئيسية"),
        Region(260, 62, 1170, 136, "project-header", "سياق المشروع"),
        Region(260, 205, 1170, 166, "autopilot-rail", "Autopilot — الماضي / الحالي / المستقبل"),
        Role(280, 403, 102, 112, "evidence", "Evidence — تحليل الأدلة"),
        Role(445, 403, 102, 112, "ux", "UX — تصميم التجربة"),
        Role(610, 403, 102, 112, "redteam", "Red Team — اختبار الثغرات"),
        Role(775, 403, 110, 112, "studio", "Studio — التطوير والتصميم"),
        Role(945, 403, 102, 112, "security", "Security — المراجعة الأمنية"),
        Role(1110, 403, 112, 112, "synthesis", "Synthesis — دمج النتائج"),
        Reasoning(342, 394, 28, 28, "evidence", "Reasoning — Evidence"),
        Reasoning(507, 394, 28, 28, "ux", "Reasoning — UX"),
        Reasoning(672, 394, 28, 28, "redteam", "Reasoning — Red Team"),
        Reasoning(842, 394, 28, 28, "studio", "Reasoning — Studio"),
        Reasoning(1007, 394, 28, 28, "security", "Reasoning — Security"),
        Reasoning(1177, 394, 28, 28, "synthesis", "Reasoning — Synthesis"),
        Region(1240, 385, 195, 160, "routing-context", "سياق توجيه المهام بين الوكلاء"),
        Filmstrip(260, 560, 1175, 195, "project-filmstrip", "شريط إصدارات المشروع"),
        Region(260, 770, 430, 190, "decision-stack", "Decision Stack — افتح وضع القرار"),
        Tool(700, 770, 400, 190, "active-tools", "الأدوات النشطة"),
        Region(1110, 770, 340, 190, "execution-info", "معلومات التنفيذ الحالية"),
        Region(18, 62, 215, 160, "autopilot-rail", "Autopilot status")
    ];

    private static readonly IReadOnlyList<HotspotDefinition> SoftwareAutopilotHotspots =
    [
        Nav(1464, 65, 66, 74, "home", "الرئيسية"),
        Nav(1464, 145, 66, 74, "project", "المشاريع"),
        Region(260, 60, 1175, 145, "project-header", "Software project context"),
        Region(260, 210, 1175, 255, "checkpoint-timeline", "Checkpoint / branch timeline"),
        Region(260, 470, 640, 300, "diff-view", "Diff / comparison"),
        Region(915, 470, 250, 300, "branch-a", "Branch A"),
        Region(1175, 470, 260, 300, "branch-b", "Branch B"),
        Region(260, 780, 1175, 175, "recovery-entry", "Recovery / checkpoint controls"),
        RecoveryAction(1160, 820, 260, 52, "fork", "Create Fork"),
        RecoveryAction(1160, 880, 260, 52, "restore", "Request Recovery"),
        Tool(10, 915, 1515, 90, "tool-dock", "Tool / model / evidence dock")
    ];

    private static readonly IReadOnlyList<HotspotDefinition> StudioProjectHotspots =
    [
        Nav(1464, 65, 66, 74, "home", "الرئيسية"),
        Nav(1464, 305, 66, 74, "studio", "الاستوديو"),
        Region(250, 62, 1180, 130, "project-header", "Studio project context"),
        Stage(250, 195, 1180, 120, "production-pipeline", "مراحل الإنتاج الخمس"),
        Region(470, 320, 690, 330, "studio-player", "المشغل / المخرج الحالي"),
        Region(250, 320, 210, 330, "studio-project-info", "معلومات المشروع"),
        Tool(1170, 320, 260, 330, "studio-tools", "الأداة / النموذج / QC"),
        Stage(250, 660, 1180, 180, "studio-timeline", "Timeline / waveform / markers"),
        Region(250, 845, 380, 110, "review-ticket", "Review Ticket"),
        Role(640, 845, 380, 110, "studio", "الفريق النشط / handoff"),
        Region(1030, 845, 400, 110, "next-handoff", "Next Handoff"),
        Tool(10, 915, 1515, 90, "tool-dock", "Tool Dock")
    ];

    private static readonly IReadOnlyList<HotspotDefinition> DecisionModeHotspots =
    [
        Nav(1464, 65, 66, 74, "home", "الرئيسية"),
        Nav(1464, 145, 66, 74, "project", "المشاريع"),
        Region(400, 145, 735, 730, "decision-surface", "Decision Context"),
        Role(190, 145, 120, 140, "evidence", "الأدلة"),
        Role(135, 365, 130, 150, "redteam", "الفريق المعارض"),
        Role(1210, 145, 130, 145, "synthesis", "المركزي / synthesis"),
        Role(1260, 365, 130, 150, "ux", "تجربة المستخدم"),
        Role(1240, 565, 145, 155, "security", "الأمن والخصوصية"),
        Region(32, 575, 325, 300, "evidence-peek", "معاينة دليل"),
        DecisionAction(1015, 890, 145, 65, "approve", "الموافقة"),
        DecisionAction(825, 890, 170, 65, "request-changes", "طلب تعديلات"),
        DecisionAction(680, 890, 125, 65, "reject", "رفض"),
        DecisionAction(520, 890, 140, 65, "ask", "طرح سؤال"),
        DecisionAction(365, 890, 140, 65, "inspect-evidence", "فحص الأدلة")
    ];

    private static readonly IReadOnlyList<HotspotDefinition> RecoveryForkHotspots =
    [
        Nav(1464, 65, 66, 74, "home", "الرئيسية"),
        Nav(1464, 145, 66, 74, "project", "المشاريع"),
        Region(235, 155, 1240, 315, "checkpoint-timeline", "المخطط الزمني ونقاط الحفظ"),
        Region(20, 475, 325, 315, "selected-checkpoint", "معلومات نقطة الحفظ المحددة"),
        Region(355, 475, 355, 315, "branch-a", "الفرع A"),
        Region(720, 475, 375, 315, "branch-b", "الفرع B"),
        Region(1105, 475, 370, 315, "branch-compare", "مقارنة الفروع"),
        Region(20, 805, 490, 165, "event-log", "السجل الزمني والإجراءات"),
        Region(520, 805, 420, 165, "evidence-peek", "أدلة ومقتطفات مهمة"),
        RecoveryAction(1180, 815, 285, 42, "restore", "استرجاع هذه النقطة"),
        RecoveryAction(1180, 862, 285, 42, "fork", "إنشاء فرع جديد"),
        RecoveryAction(1180, 909, 285, 42, "promote", "ترقية نتيجة الفرع"),
        RecoveryAction(955, 909, 215, 42, "delete", "حذف الفرع المحدد")
    ];

    private static readonly IReadOnlyList<HotspotDefinition> PulseStoryHotspots =
    [
        Nav(1464, 65, 66, 74, "home", "الرئيسية"),
        Nav(1464, 145, 66, 74, "project", "المشاريع"),
        Region(250, 65, 1185, 115, "project-header", "Pulse / project selector"),
        Region(250, 185, 1185, 145, "story-timeline", "Story timeline"),
        Pulse(250, 340, 280, 250, "before", "Before"),
        Pulse(540, 340, 605, 250, "video-story", "Video / main story"),
        Pulse(1155, 340, 280, 250, "after", "After"),
        Pulse(250, 605, 225, 330, "achievement", "Achievement"),
        Pulse(485, 605, 225, 330, "handoff", "Handoff"),
        Pulse(720, 605, 225, 330, "discovery", "Discovery / Unknown"),
        Pulse(955, 605, 225, 330, "blocker", "Blocker / evidence"),
        Pulse(1190, 605, 245, 330, "verified", "Verified achievement"),
        Region(20, 62, 215, 160, "autopilot-rail", "Autopilot status"),
        Tool(10, 915, 1515, 90, "tool-dock", "Tool Dock")
    ];

    private static readonly IReadOnlyList<HotspotDefinition> WorkReceiptHotspots =
    [
        Nav(1464, 65, 66, 74, "home", "الرئيسية"),
        Nav(1464, 145, 66, 74, "project", "المشاريع"),
        Region(250, 62, 1185, 220, "work-receipt", "Completion / Work Receipt header"),
        Stage(250, 290, 1185, 155, "completed-stages", "مراحل المشروع المكتملة"),
        Region(250, 455, 300, 335, "business-receipt", "إيصال الأعمال"),
        Artifact(560, 455, 520, 250, "final-outputs", "المخرجات النهائية"),
        Region(1090, 455, 345, 335, "evidence-peek", "الأدلة والشواهد"),
        Region(560, 715, 520, 75, "usage-summary", "النماذج / الأدوات / الوقت / الاستخدام"),
        Region(250, 805, 275, 145, "issues-recovered", "المشاكل التي تم تجاوزها"),
        Region(535, 805, 275, 145, "fallbacks", "خطط الرجوع"),
        Region(820, 805, 275, 145, "checkpoints", "نقاط التحقق"),
        Region(1105, 805, 185, 145, "council-decisions", "قرارات المجلس"),
        Region(1300, 805, 135, 145, "receipt-entry", "الإجراء الموصى به الآن"),
        Tool(10, 915, 1515, 90, "tool-dock", "Tool Dock")
    ];

    private static HotspotDefinition Nav(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Navigate, id, label);

    private static HotspotDefinition Role(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Role, id, label);

    private static HotspotDefinition Reasoning(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Reasoning, id, label);

    private static HotspotDefinition Region(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Region, id, label);

    private static HotspotDefinition Filmstrip(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Filmstrip, id, label);

    private static HotspotDefinition Tool(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Tool, id, label);

    private static HotspotDefinition DecisionAction(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.DecisionAction, id, label);

    private static HotspotDefinition RecoveryAction(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.RecoveryAction, id, label);

    private static HotspotDefinition Artifact(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Artifact, id, label);

    private static HotspotDefinition Stage(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Stage, id, label);

    private static HotspotDefinition Pulse(
        double x,
        double y,
        double width,
        double height,
        string id,
        string label) =>
        new(x, y, width, height, HotspotKind.Pulse, id, label);

    private enum ScreenKind
    {
        Home,
        ProjectWorkspace,
        SoftwareAutopilot,
        StudioProject,
        DecisionMode,
        RecoveryFork,
        PulseStory,
        WorkReceipt,
    }

    private enum HotspotKind
    {
        Navigate,
        Role,
        Reasoning,
        Region,
        Filmstrip,
        Tool,
        DecisionAction,
        RecoveryAction,
        Artifact,
        Stage,
        Pulse,
    }

    private sealed record HotspotDefinition(
        double X,
        double Y,
        double Width,
        double Height,
        HotspotKind Kind,
        string Id,
        string Label);

    private sealed record RoleContextData(
        string Title,
        string Subtitle,
        string Why,
        string Task,
        string State,
        string Findings,
        string Dissent,
        string Evidence,
        string Reasoning);

    private sealed record RegionContext(
        string Title,
        string Subtitle,
        string Explanation,
        string State);
}
