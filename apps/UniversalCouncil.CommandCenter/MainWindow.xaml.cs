using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
using System.Windows.Media.Effects;
using System.Windows.Media.Imaging;
using System.Windows.Shapes;

namespace UniversalCouncil.CommandCenter;

public partial class MainWindow : Window
{
    private readonly MainWindowViewModel _viewModel;
    private FrameworkElement? _lastInteractionTarget;
    private string? _activeRoleId;
    private ScreenKind _currentScreen = ScreenKind.Home;
    private bool _nativeReferenceBlendEnabled;
    private const string OwnerPromptPlaceholder = "صف ما تريد إنجازه...";

    private static class CrossScreenVisualTokens
    {
        public const string TopChromeBackground = "#FFFCF8F3";
        public const string SharedPanelBackground = "#FFFCFBF8";
        public const string SharedBorder = "#E5E0D8";
        public const string SharedSoftBorder = "#E7E2DA";
        public const string SharedCoolBorder = "#DDE2E7";
        public const string SharedMutedText = "#7A8390";
        public const string SharedBodyText = "#2D3748";
        public const string PrimaryBlue = "#2F75F3";
        public const string SuccessGreen = "#16A452";
        public const string UnknownState = "#8A93A0";
        public const double TopChromeHeight = 49;
        public const double RightRailLeft = 1470;
        public const double RightRailWidth = 66;
        public const double BottomDockTop = 963;
        public const double BottomDockHeight = 61;
        public const double SharedCardRadius = 12;
        public const double NavGlyphSize = 21;
        public const double NavLabelSize = 9.5;
        public const double DockGlyphSize = 16;
        public const double DockLabelSize = 10.5;
    }

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
        BuildNativeHomeChrome();
    }

    private string ExecutionTruthLabel =>
        _viewModel.ExecutionFabric.LiveDispatchEnabled
            ? "LIVE DISPATCH ENABLED"
            : "LIVE DISPATCH DISABLED";

    private static SolidColorBrush Brush(string hex) =>
        new((Color)ColorConverter.ConvertFromString(hex));

    private static TextBlock ChromeText(
        string text,
        double fontSize,
        string color,
        FontWeight? weight = null,
        FlowDirection flow = FlowDirection.RightToLeft)
    {
        return new TextBlock
        {
            Text = text,
            FontSize = fontSize,
            Foreground = Brush(color),
            FontWeight = weight ?? FontWeights.Normal,
            FlowDirection = flow,
            VerticalAlignment = VerticalAlignment.Center,
            TextTrimming = TextTrimming.CharacterEllipsis,
        };
    }

    private static void Place(
        Canvas canvas,
        FrameworkElement element,
        double left,
        double top,
        double width,
        double height)
    {
        element.Width = width;
        element.Height = height;
        Canvas.SetLeft(element, left);
        Canvas.SetTop(element, top);
        canvas.Children.Add(element);
    }

    private static Border ChromePanel(
        string background,
        string border,
        double radius,
        Thickness? borderThickness = null) =>
        new()
        {
            Background = Brush(background),
            BorderBrush = Brush(border),
            BorderThickness = borderThickness ?? new Thickness(1),
            CornerRadius = new CornerRadius(radius),
            IsHitTestVisible = false,
        };

    private void AddFixtureTruthBadge(Canvas layer)
    {
        var badge = ChromePanel("#F4F5F7", "#D9DDE3", 7);
        AutomationProperties.SetName(
            badge,
            "بيانات مرجعية للعرض فقط — ليست حالة تشغيل حية");
        Place(layer, badge, 326, 11, 158, 26);

        var text = ChromeText(
            "REFERENCE FIXTURE · NOT LIVE",
            7.7,
            "#616B78",
            FontWeights.SemiBold,
            FlowDirection.LeftToRight);
        text.TextAlignment = TextAlignment.Center;
        AutomationProperties.SetName(
            text,
            "بيانات مرجعية للعرض فقط — ليست حالة تشغيل حية");
        Place(layer, text, 334, 15, 142, 17);
    }

    private Button AddChromeHotspot(
        double left,
        double top,
        double width,
        double height,
        string tag,
        string label,
        RoutedEventHandler handler)
    {
        var button = new Button
        {
            Tag = tag,
            ToolTip = label,
            Style = (Style)FindResource("HotspotButtonStyle"),
        };
        AutomationProperties.SetName(button, label);
        AutomationProperties.SetHelpText(button, "يعرض حالة موثقة أو UNKNOWN ولا يفترض اتصالًا أو نجاحًا.");
        button.Click += handler;
        Place(NativeHomeChromeLayer, button, left, top, width, height);
        return button;
    }

    private void BuildNativeHomeChrome()
    {
        NativeHomeChromeLayer.Children.Clear();

        // Top chrome.
        Place(
            NativeHomeChromeLayer,
            ChromePanel(CrossScreenVisualTokens.TopChromeBackground, CrossScreenVisualTokens.SharedBorder, 0, new Thickness(0, 0, 0, 1)),
            0,
            0,
            1536,
            49);
        AddFixtureTruthBadge(NativeHomeChromeLayer);

        var mark = new Ellipse
        {
            Fill = Brush("#FFEEC34B"),
            Stroke = Brush("#E1B232"),
            StrokeThickness = 1,
            IsHitTestVisible = false,
        };
        Place(NativeHomeChromeLayer, mark, 25, 14, 18, 18);
        Place(
            NativeHomeChromeLayer,
            ChromeText("✦", 15, "#3978DA", FontWeights.Bold, FlowDirection.LeftToRight),
            28,
            11,
            20,
            22);
        Place(
            NativeHomeChromeLayer,
            ChromeText("UniversalCouncil", 17, "#15213B", FontWeights.SemiBold, FlowDirection.LeftToRight),
            55,
            9,
            140,
            28);
        Place(
            NativeHomeChromeLayer,
            ChromeText("Command Center", 13, "#7A8290", null, FlowDirection.LeftToRight),
            198,
            11,
            120,
            26);

        var search = ChromePanel("#FFFCFBFA", "#DCD9D5", 13);
        Place(NativeHomeChromeLayer, search, 505, 7, 525, 35);
        Place(
            NativeHomeChromeLayer,
            ChromeText("⌕", 16, "#5C86C5", null, FlowDirection.LeftToRight),
            520,
            9,
            25,
            30);
        Place(
            NativeHomeChromeLayer,
            ChromeText("البحث في جميع مشاريعك وملفاتك وقرارات المجلس...", 11, "#9A9FA8"),
            554,
            9,
            390,
            30);
        var shortcut = ChromePanel("#F7F6F4", "#E0DDD8", 6);
        Place(NativeHomeChromeLayer, shortcut, 973, 13, 48, 22);
        Place(
            NativeHomeChromeLayer,
            ChromeText("Ctrl K", 9, "#596171", FontWeights.SemiBold, FlowDirection.LeftToRight),
            982,
            14,
            34,
            19);
        AddChromeHotspot(505, 7, 525, 35, "search", "البحث العام", NativeUtility_Click);

        Place(
            NativeHomeChromeLayer,
            ChromeText("☼", 21, "#D99D26", null, FlowDirection.LeftToRight),
            1220,
            10,
            28,
            28);
        Place(
            NativeHomeChromeLayer,
            ChromeText("♟", 20, "#DB334F", null, FlowDirection.LeftToRight),
            1268,
            9,
            28,
            28);
        AddChromeHotspot(1209, 5, 43, 39, "theme", "المظهر", NativeUtility_Click);
        AddChromeHotspot(1257, 5, 43, 39, "notifications", "التنبيهات", NativeUtility_Click);

        Place(
            NativeHomeChromeLayer,
            ChromeText("المجلس الخاص بك", 11.5, "#3A4454", FontWeights.SemiBold),
            1321,
            5,
            122,
            20);
        Place(
            NativeHomeChromeLayer,
            ChromeText("Owner", 10, "#78808D", null, FlowDirection.LeftToRight),
            1377,
            22,
            57,
            17);
        var ownerAvatar = new Ellipse
        {
            Fill = new RadialGradientBrush(
                Color.FromRgb(232, 244, 255),
                Color.FromRgb(116, 105, 228)),
            Stroke = Brush("#B8B3F0"),
            StrokeThickness = 1.2,
            IsHitTestVisible = false,
        };
        Place(NativeHomeChromeLayer, ownerAvatar, 1437, 10, 28, 28);
        AddChromeHotspot(1314, 3, 154, 43, "owner", "سياق المالك", NativeUtility_Click);

        // Hero band.
        Place(
            NativeHomeChromeLayer,
            ChromePanel("#FFF9F3EC", "#F3EEE7", 0, new Thickness(0)),
            240,
            49,
            1230,
            114);

        AddHeroPath("M 252,98 C 330,42 414,56 538,130", "#65CDE9", 1.5, 0.46);
        AddHeroPath("M 300,135 C 400,65 474,66 596,153", "#856EE8", 1.5, 0.34);
        AddHeroPath("M 1188,121 C 1295,60 1360,74 1460,102", "#F3B06B", 1.4, 0.34);
        AddHeroPath("M 1280,155 C 1365,88 1414,91 1466,85", "#F4C97A", 1.2, 0.28);

        Place(
            NativeHomeChromeLayer,
            ChromeText("✦", 31, "#318DFF", FontWeights.Bold, FlowDirection.LeftToRight),
            963,
            72,
            36,
            44);
        Place(
            NativeHomeChromeLayer,
            ChromeText("ماذا تريد أن تنجز؟", 39, "#101A36", FontWeights.Bold),
            650,
            66,
            325,
            60);
        var support = ChromeText(
            "حوّل أفكارك إلى نتائج حقيقية\nمع مجلسك الذكي.",
            14,
            "#394456",
            FontWeights.SemiBold);
        support.TextAlignment = TextAlignment.Right;
        support.LineHeight = 22;
        Place(NativeHomeChromeLayer, support, 1065, 72, 225, 60);

        // Left status rail.
        Place(
            NativeHomeChromeLayer,
            ChromePanel("#FFF8F5EF", "#EEE9E1", 0, new Thickness(0, 0, 1, 0)),
            0,
            49,
            238,
            914);

        var autopilotLive = _viewModel.ExecutionFabric.LiveDispatchEnabled;
        var autopilotAccent = autopilotLive ? "#24C85A" : CrossScreenVisualTokens.UnknownState;
        var autopilotWaveform = autopilotLive ? "#54E98A" : "#B8BEC7";
        var autopilotLabel = autopilotLive ? "يعمل الآن" : "غير مفعّل";
        var autopilotMessage = autopilotLive
            ? "لا يوجد شيء مطلوب\nمنك الآن"
            : "التنفيذ الحي متوقف\nلا توجد مهمة فعلية";

        var autoCard = ChromePanel(CrossScreenVisualTokens.SharedPanelBackground, CrossScreenVisualTokens.SharedCoolBorder, 14);
        Place(NativeHomeChromeLayer, autoCard, 16, 62, 215, 159);
        Place(
            NativeHomeChromeLayer,
            new Ellipse { Fill = Brush(autopilotAccent), IsHitTestVisible = false },
            31,
            79,
            13,
            13);
        Place(
            NativeHomeChromeLayer,
            ChromeText("Autopilot", 16, "#1E293B", FontWeights.SemiBold, FlowDirection.LeftToRight),
            55,
            70,
            115,
            27);
        Place(
            NativeHomeChromeLayer,
            ChromeText(autopilotLabel, 10, autopilotAccent, FontWeights.SemiBold),
            55,
            96,
            80,
            20);

        var waveform = new Polyline
        {
            Stroke = Brush(autopilotWaveform),
            StrokeThickness = 2.3,
            Opacity = autopilotLive ? 0.9 : 0.28,
            IsHitTestVisible = false,
            Points = new PointCollection
            {
                new(0, 22), new(19, 21), new(30, 16), new(42, 25), new(53, 20),
                new(63, 5), new(74, 34), new(84, 10), new(95, 21), new(114, 19),
                new(132, 23), new(150, 22)
            }
        };
        Place(NativeHomeChromeLayer, waveform, 46, 113, 150, 40);
        var autoMessage = ChromeText(autopilotMessage, 11.5, "#485161", FontWeights.SemiBold);
        autoMessage.TextAlignment = TextAlignment.Center;
        Place(NativeHomeChromeLayer, autoMessage, 45, 158, 155, 48);
        Place(
            NativeHomeChromeLayer,
            ChromeText("›", 24, "#647083", null, FlowDirection.LeftToRight),
            199,
            75,
            20,
            30);
        AddChromeHotspot(16, 62, 215, 159, "autopilot", "Autopilot — حالة التنفيذ", NativeStatus_Click);

        AddNativeStatusCard(
            228,
            "—",
            CrossScreenVisualTokens.UnknownState,
            "المشاريع النشطة",
            "الحالة غير متحققة",
            "projects");
        AddNativeStatusCard(
            316,
            "—",
            CrossScreenVisualTokens.UnknownState,
            "المهام بانتظارك",
            "تُعرض من بيانات فعلية فقط",
            "waiting");
        AddNativeStatusCard(
            404,
            "—",
            CrossScreenVisualTokens.UnknownState,
            "تنبيهات مهمة",
            "لا توجد حالة حية موثقة",
            "alerts");

        // Right global navigation rail.
        Place(
            NativeHomeChromeLayer,
            ChromePanel(CrossScreenVisualTokens.SharedPanelBackground, CrossScreenVisualTokens.SharedBorder, 0, new Thickness(1, 0, 0, 0)),
            1470,
            0,
            66,
            963);
        var brandTop = ChromePanel("#15152D", "#15152D", 0);
        Place(NativeHomeChromeLayer, brandTop, 1470, 0, 66, 64);
        Place(
            NativeHomeChromeLayer,
            ChromeText("◇", 30, "#FFFFFF", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1487,
            14,
            34,
            34);

        AddNativeNavItem(72, "⌂", "الرئيسية", "home", true);
        AddNativeNavItem(158, "▣", "المشاريع", "project", false);
        AddNativeNavItem(244, "♧", "المجلس", "council", false);
        AddNativeNavItem(330, "✎", "الاستوديو", "studio", false);
        AddNativeNavItem(416, "◇", "المعرفة", "knowledge", false);
        AddNativeNavItem(502, "⌘", "الأدوات", "tools", false);
        AddNativeNavItem(588, "▥", "التقارير", "reports", false);
        AddNativeNavItem(858, "⚙", "الإعدادات", "settings", false);

        // Bottom Tool Dock.
        var dock = ChromePanel("#FFFCFBFA", "#DDD9D4", 16);
        Place(NativeHomeChromeLayer, dock, 0, 963, 1536, 61);
        Place(
            NativeHomeChromeLayer,
            ChromeText("⌃", 18, "#475366", null, FlowDirection.LeftToRight),
            19,
            978,
            25,
            25);
        Place(
            NativeHomeChromeLayer,
            ChromeText("أدواتك", 12, "#273349", FontWeights.SemiBold),
            58,
            974,
            62,
            25);
        Place(
            NativeHomeChromeLayer,
            new Ellipse { Fill = Brush(CrossScreenVisualTokens.UnknownState), IsHitTestVisible = false },
            118,
            981,
            8,
            8);
        Place(
            NativeHomeChromeLayer,
            ChromeText("UNKNOWN", 9, "#6B7280", FontWeights.SemiBold, FlowDirection.LeftToRight),
            128,
            976,
            53,
            20);

        AddDockChip(182, 103, "●", "GitHub", "github", "#F3F5F8", "#161B22");
        AddDockChip(292, 78, "Ps", "Photoshop", "photoshop", "#122D55", "#31A8FF");
        AddDockChip(377, 86, "Ae", "After Effects", "after-effects", "#26154D", "#9999FF");
        AddDockChip(470, 82, "Pr", "Premiere", "premiere", "#26154D", "#9999FF");
        AddDockChip(559, 96, "◇", "YASSIN", "yassin", "#17182B", "#FFFFFF");
        AddDockChip(662, 104, "▦", "Tailscale", "tailscale", "#F0F1F4", "#111827");
        AddDockChip(773, 93, "⬡", "Models", "models", "#F4F5F8", "#48556D");
        AddDockChip(873, 103, "▤", "Evidence", "evidence", "#F4F5F8", "#25324A");
        AddDockChip(983, 126, "●", "Android Owner", "android-owner", "#F4F5F8", "#151D2C");

        var allTools = ChromePanel("#F8F8F7", "#DEDBD6", 10);
        Place(NativeHomeChromeLayer, allTools, 1390, 973, 126, 40);
        Place(
            NativeHomeChromeLayer,
            ChromeText("جميع الأدوات   ▦", 11, "#4E5868", FontWeights.SemiBold),
            1402,
            980,
            101,
            25);
        AddChromeHotspot(1390, 973, 126, 40, "all-tools", "جميع الأدوات", NativeDockTool_Click);
    }

    private void AddHeroPath(string data, string color, double thickness, double opacity)
    {
        var path = new Path
        {
            Data = Geometry.Parse(data),
            Stroke = Brush(color),
            StrokeThickness = thickness,
            Opacity = opacity,
            IsHitTestVisible = false,
        };
        NativeHomeChromeLayer.Children.Add(path);
    }

    private void AddNativeStatusCard(
        double top,
        string count,
        string accent,
        string title,
        string subtitle,
        string tag)
    {
        var card = ChromePanel(CrossScreenVisualTokens.SharedPanelBackground, CrossScreenVisualTokens.SharedSoftBorder, CrossScreenVisualTokens.SharedCardRadius);
        Place(NativeHomeChromeLayer, card, 16, top, 215, 75);

        var countBadge = ChromePanel("#F8F9FB", "#E3E5E9", 8);
        Place(NativeHomeChromeLayer, countBadge, 29, top + 12, 36, 32);
        Place(
            NativeHomeChromeLayer,
            ChromeText(count, 18, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            39,
            top + 13,
            20,
            29);
        Place(
            NativeHomeChromeLayer,
            ChromeText(title, 12.5, "#2D3748", FontWeights.SemiBold),
            77,
            top + 8,
            126,
            25);
        Place(
            NativeHomeChromeLayer,
            ChromeText(subtitle, 9.2, "#7A8390"),
            77,
            top + 32,
            126,
            27);
        Place(
            NativeHomeChromeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false, Opacity = 0.9 },
            198,
            top + 27,
            9,
            9);
        AddChromeHotspot(16, top, 215, 75, tag, title, NativeStatus_Click);
    }

    private void AddNativeNavItem(
        double top,
        string glyph,
        string label,
        string tag,
        bool active)
    {
        if (active)
        {
            Place(
                NativeHomeChromeLayer,
                ChromePanel("#EFF5FF", "#EFF5FF", 10),
                1478,
                top,
                50,
                70);
        }

        Place(
            NativeHomeChromeLayer,
            ChromeText(
                glyph,
                21,
                active ? "#196FF1" : "#273349",
                FontWeights.SemiBold,
                FlowDirection.LeftToRight),
            1492,
            top + 7,
            26,
            27);
        var labelText = ChromeText(
            label,
            9.5,
            active ? "#196FF1" : "#455064",
            active ? FontWeights.SemiBold : FontWeights.Normal);
        labelText.TextAlignment = TextAlignment.Center;
        Place(NativeHomeChromeLayer, labelText, 1478, top + 39, 50, 22);
        AddChromeHotspot(1478, top, 50, 70, tag, label, NativeHomeNav_Click);
    }

    private void AddDockChip(
        double left,
        double width,
        string glyph,
        string label,
        string tag,
        string background,
        string accent)
    {
        var chip = ChromePanel(background, "#E1DED9", 9);
        Place(NativeHomeChromeLayer, chip, left, 972, width, 42);
        Place(
            NativeHomeChromeLayer,
            ChromeText(glyph, 16, accent, FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 10,
            980,
            24,
            24);
        Place(
            NativeHomeChromeLayer,
            ChromeText(label, 10.5, "#313B4C", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 34,
            978,
            width - 42,
            26);
        AddChromeHotspot(left, 972, width, 42, tag, label, NativeDockTool_Click);
    }

    private void NativeStatus_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string tag)
        {
            return;
        }

        _lastInteractionTarget = button;
        switch (tag)
        {
            case "autopilot":
                NavigateTo(ScreenKind.SoftwareAutopilot);
                break;
            case "projects":
                NavigateTo(ScreenKind.ProjectWorkspace);
                break;
            case "waiting":
                OpenGenericRegion(
                    "المهام بانتظارك",
                    "Owner queue",
                    "يعرض القرارات والمهام التي تحتاج تدخل المالك فقط عندما تكون موجودة فعليًا.",
                    "UNKNOWN / REFERENCE FIXTURE");
                break;
            default:
                OpenGenericRegion(
                    "تنبيهات مهمة",
                    "Owner alerts",
                    "لا توجد تنبيهات حية مفترضة من المرجع؛ الحالة الفعلية تأتي من runtime.",
                    "UNKNOWN / REFERENCE FIXTURE");
                break;
        }
    }

    private void NativeHomeNav_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string tag)
        {
            return;
        }

        _lastInteractionTarget = button;
        switch (tag)
        {
            case "home":
                NavigateTo(ScreenKind.Home);
                break;
            case "project":
                NavigateTo(ScreenKind.ProjectWorkspace);
                break;
            case "studio":
                NavigateTo(ScreenKind.StudioProject);
                break;
            case "council":
                OpenGenericRegion(
                    "المجلس",
                    "Council workspace",
                    "يفتح سياق المجلس والأعضاء ومساهماتهم دون تغيير truth state.",
                    "UI INTERACTION LAYER");
                break;
            case "knowledge":
                OpenGenericRegion(
                    "المعرفة",
                    "Knowledge",
                    "يفتح سياق المعرفة والأدلة والمصادر المرتبطة بالمشاريع.",
                    "UI INTERACTION LAYER");
                break;
            case "tools":
                OpenToolInspector("global-tools");
                break;
            case "reports":
                OpenGenericRegion(
                    "التقارير",
                    "Reports",
                    "يعرض تقارير موثقة فقط عند توفر بيانات ومخرجات فعلية.",
                    "UI INTERACTION LAYER");
                break;
            case "settings":
                OpenGenericRegion(
                    "الإعدادات",
                    "Command Center settings",
                    "إعدادات المنتج والنماذج والأدوات والواجهة، بدون تغيير تلقائي.",
                    "UI INTERACTION LAYER");
                break;
        }
    }

    private void NativeUtility_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string tag)
        {
            return;
        }

        _lastInteractionTarget = button;
        var (title, explanation) = tag switch
        {
            "search" => (
                "البحث العام",
                "بحث موحد في المشاريع والملفات وقرارات المجلس عند ربط مصدر البحث الفعلي."),
            "theme" => (
                "المظهر",
                "تغيير المظهر غير منفذ تلقائيًا من هذا السطح أثناء قفل المرجع البصري."),
            "notifications" => (
                "التنبيهات",
                "تظهر التنبيهات الفعلية فقط من state موثوق."),
            _ => (
                "Owner",
                "سياق المالك وصلاحياته؛ لا يتم تغيير صلاحيات أو نموذج من هذا الضغط.")
        };
        OpenGenericRegion(title, "Top chrome", explanation, "UI INTERACTION LAYER");
    }

    private void NativeDockTool_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string tag)
        {
            return;
        }

        _lastInteractionTarget = button;
        OpenDrawer(
            "TOOL INSPECTOR",
            button.ToolTip?.ToString() ?? tag,
            "Tool Dock",
            "الأداة قابلة للفحص من الـDock ولا يعني ظهورها أنها متصلة أو نشطة.",
            "لا توجد مهمة tool runtime مفترضة.",
            tag == "yassin" ? ExecutionTruthLabel : "UNKNOWN / REFERENCE FIXTURE",
            "Ready / Active / Connected / Blocked / Unknown يجب أن تأتي من حالة موثقة.",
            "لا يوجد blocker مفترض من الصورة.",
            "آخر تحقق ودليل الاتصال يظهران عند توفرهما.",
            "N/A");
    }

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

    private void ShowAllProjects_Click(object sender, RoutedEventArgs e)
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
        SecondaryNativeLayer.Visibility = isHome ? Visibility.Collapsed : Visibility.Visible;
        SecondaryNativeLayer.Opacity = _nativeReferenceBlendEnabled && !isHome ? 0.46 : 1;
        SecondaryNativeLayer.Children.Clear();
        SecondaryInteractionCanvas.Visibility = isHome ? Visibility.Collapsed : Visibility.Visible;
        SecondaryInteractionCanvas.Children.Clear();

        if (!isHome)
        {
            BuildSecondaryNative(screen);
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

    private void BuildSecondaryNative(ScreenKind screen)
    {
        if (screen == ScreenKind.ProjectWorkspace)
        {
            BuildNativeProjectWorkspaceCore();
        }
        else if (screen == ScreenKind.SoftwareAutopilot)
        {
            BuildNativeSoftwareAutopilot();
        }
        else if (screen == ScreenKind.StudioProject)
        {
            BuildNativeStudioProject();
        }
        else if (screen == ScreenKind.DecisionMode)
        {
            BuildNativeOwnerDecision();
        }
        else if (screen == ScreenKind.RecoveryFork)
        {
            BuildNativeRecoveryFork();
        }
        else if (screen == ScreenKind.PulseStory)
        {
            BuildNativePulseStory();
        }
        else if (screen == ScreenKind.WorkReceipt)
        {
            BuildNativeWorkReceipt();
        }

        BuildSecondarySharedChrome(screen);
    }

    private void BuildSecondarySharedChrome(ScreenKind screen)
    {
        BuildSecondaryTopChrome();
        BuildSecondaryRightNavigation(screen);

        if (screen is not ScreenKind.ProjectWorkspace and not ScreenKind.DecisionMode)
        {
            BuildSecondaryStatusRail();
        }

        if (screen is ScreenKind.ProjectWorkspace or
            ScreenKind.SoftwareAutopilot or
            ScreenKind.StudioProject or
            ScreenKind.WorkReceipt)
        {
            BuildSecondaryToolDock();
        }
    }

    private void BuildSecondaryTopChrome()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel(
                CrossScreenVisualTokens.TopChromeBackground,
                CrossScreenVisualTokens.SharedBorder,
                0,
                new Thickness(0, 0, 0, 1)),
            0,
            0,
            1536,
            CrossScreenVisualTokens.TopChromeHeight);
        AddFixtureTruthBadge(SecondaryNativeLayer);

        var mark = new Ellipse
        {
            Fill = Brush("#FFEEC34B"),
            Stroke = Brush("#E1B232"),
            StrokeThickness = 1,
            IsHitTestVisible = false,
        };
        Place(SecondaryNativeLayer, mark, 25, 14, 18, 18);
        Place(
            SecondaryNativeLayer,
            ChromeText("✦", 15, "#3978DA", FontWeights.Bold, FlowDirection.LeftToRight),
            28,
            11,
            20,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("UniversalCouncil", 17, "#15213B", FontWeights.SemiBold, FlowDirection.LeftToRight),
            55,
            9,
            140,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("Command Center", 13, CrossScreenVisualTokens.SharedMutedText, null, FlowDirection.LeftToRight),
            198,
            11,
            120,
            26);

        var search = ChromePanel("#FFFCFBFA", "#DCD9D5", 13);
        Place(SecondaryNativeLayer, search, 505, 7, 525, 35);
        Place(
            SecondaryNativeLayer,
            ChromeText("⌕", 16, "#5C86C5", null, FlowDirection.LeftToRight),
            520,
            9,
            25,
            30);
        var searchText = ChromeText(
            "البحث في جميع مشاريعك وملفاتك وقرارات المجلس...",
            11,
            "#9A9FA8");
        searchText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, searchText, 554, 9, 390, 30);
        var shortcut = ChromePanel("#F7F6F4", "#E0DDD8", 6);
        Place(SecondaryNativeLayer, shortcut, 973, 13, 48, 22);
        Place(
            SecondaryNativeLayer,
            ChromeText("Ctrl K", 9, "#596171", FontWeights.SemiBold, FlowDirection.LeftToRight),
            982,
            14,
            34,
            19);

        Place(
            SecondaryNativeLayer,
            ChromeText("☼", 21, "#D99D26", null, FlowDirection.LeftToRight),
            1220,
            10,
            28,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("♟", 20, "#DB334F", null, FlowDirection.LeftToRight),
            1268,
            9,
            28,
            28);
        var owner = ChromeText("المجلس الخاص بك", 11.5, "#3A4454", FontWeights.SemiBold);
        owner.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, owner, 1321, 5, 122, 20);
        var ownerSub = ChromeText("Owner", 10, "#78808D", null, FlowDirection.LeftToRight);
        ownerSub.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, ownerSub, 1377, 22, 57, 17);

        var ownerAvatar = new Ellipse
        {
            Fill = new RadialGradientBrush(
                Color.FromRgb(232, 244, 255),
                Color.FromRgb(116, 105, 228)),
            Stroke = Brush("#B8B3F0"),
            StrokeThickness = 1.2,
            IsHitTestVisible = false,
        };
        Place(SecondaryNativeLayer, ownerAvatar, 1437, 10, 28, 28);
    }

    private void BuildSecondaryRightNavigation(ScreenKind screen)
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel(
                CrossScreenVisualTokens.SharedPanelBackground,
                CrossScreenVisualTokens.SharedBorder,
                0,
                new Thickness(1, 0, 0, 0)),
            CrossScreenVisualTokens.RightRailLeft,
            0,
            CrossScreenVisualTokens.RightRailWidth,
            CrossScreenVisualTokens.BottomDockTop);
        Place(
            SecondaryNativeLayer,
            ChromePanel("#15152D", "#15152D", 0),
            CrossScreenVisualTokens.RightRailLeft,
            0,
            CrossScreenVisualTokens.RightRailWidth,
            64);
        Place(
            SecondaryNativeLayer,
            ChromeText("◇", 30, "#FFFFFF", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1487,
            14,
            34,
            34);

        var active = screen switch
        {
            ScreenKind.ProjectWorkspace => "project",
            ScreenKind.SoftwareAutopilot => "project",
            ScreenKind.StudioProject => "studio",
            ScreenKind.RecoveryFork => "project",
            ScreenKind.DecisionMode => "home",
            ScreenKind.PulseStory => "home",
            ScreenKind.WorkReceipt => "home",
            _ => "home",
        };

        AddSecondaryNavVisual(72, "⌂", "الرئيسية", "home", active == "home");
        AddSecondaryNavVisual(158, "▣", "المشاريع", "project", active == "project");
        AddSecondaryNavVisual(244, "♧", "المجلس", "council", active == "council");
        AddSecondaryNavVisual(330, "✎", "الاستوديو", "studio", active == "studio");
        AddSecondaryNavVisual(416, "◇", "المعرفة", "knowledge", active == "knowledge");
        AddSecondaryNavVisual(502, "⌘", "الأدوات", "tools", active == "tools");
        AddSecondaryNavVisual(588, "▥", "التقارير", "reports", active == "reports");
        AddSecondaryNavVisual(858, "⚙", "الإعدادات", "settings", active == "settings");
    }

    private void AddSecondaryNavVisual(
        double top,
        string glyph,
        string label,
        string tag,
        bool active)
    {
        if (active)
        {
            Place(
                SecondaryNativeLayer,
                ChromePanel("#EFF5FF", "#EFF5FF", 10),
                1478,
                top,
                50,
                70);
        }

        Place(
            SecondaryNativeLayer,
            ChromeText(
                glyph,
                CrossScreenVisualTokens.NavGlyphSize,
                active ? "#196FF1" : "#273349",
                FontWeights.SemiBold,
                FlowDirection.LeftToRight),
            1492,
            top + 7,
            26,
            27);
        var text = ChromeText(
            label,
            CrossScreenVisualTokens.NavLabelSize,
            active ? "#196FF1" : "#455064",
            active ? FontWeights.SemiBold : FontWeights.Normal);
        text.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, text, 1478, top + 39, 50, 22);
    }

    private void BuildSecondaryStatusRail()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFF8F5EF", "#EEE9E1", 0, new Thickness(0, 0, 1, 0)),
            0,
            CrossScreenVisualTokens.TopChromeHeight,
            238,
            430);

        var autopilotLive = _viewModel.ExecutionFabric.LiveDispatchEnabled;
        var autopilotAccent = autopilotLive ? "#24C85A" : CrossScreenVisualTokens.UnknownState;
        var autopilotWaveform = autopilotLive ? "#54E98A" : "#B8BEC7";
        var autopilotLabel = autopilotLive ? "يعمل الآن" : "غير مفعّل";
        var autopilotMessage = autopilotLive
            ? "لا يوجد شيء مطلوب\nمنك الآن"
            : "التنفيذ الحي متوقف\nلا توجد مهمة فعلية";

        var auto = ChromePanel(
            CrossScreenVisualTokens.SharedPanelBackground,
            CrossScreenVisualTokens.SharedCoolBorder,
            14);
        Place(SecondaryNativeLayer, auto, 16, 62, 215, 159);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(autopilotAccent), IsHitTestVisible = false },
            31,
            79,
            13,
            13);
        Place(
            SecondaryNativeLayer,
            ChromeText("Autopilot", 16, "#1E293B", FontWeights.SemiBold, FlowDirection.LeftToRight),
            55,
            70,
            115,
            27);
        Place(
            SecondaryNativeLayer,
            ChromeText(autopilotLabel, 10, autopilotAccent, FontWeights.SemiBold),
            55,
            96,
            80,
            20);

        var waveform = new Polyline
        {
            Stroke = Brush(autopilotWaveform),
            StrokeThickness = 2.3,
            Opacity = autopilotLive ? 0.9 : 0.28,
            IsHitTestVisible = false,
            Points = new PointCollection
            {
                new(0, 22), new(19, 21), new(30, 16), new(42, 25), new(53, 20),
                new(63, 5), new(74, 34), new(84, 10), new(95, 21), new(114, 19),
                new(132, 23), new(150, 22)
            },
        };
        Place(SecondaryNativeLayer, waveform, 46, 113, 150, 40);
        var autoMessage = ChromeText(autopilotMessage, 11.5, "#485161", FontWeights.SemiBold);
        autoMessage.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, autoMessage, 45, 158, 155, 48);
        Place(
            SecondaryNativeLayer,
            ChromeText("›", 24, "#647083", null, FlowDirection.LeftToRight),
            199,
            75,
            20,
            30);

        AddSecondaryStatusVisual(228, "—", "المشاريع النشطة", "الحالة غير متحققة", CrossScreenVisualTokens.UnknownState);
        AddSecondaryStatusVisual(316, "—", "المهام بانتظارك", "تُعرض من بيانات فعلية فقط", CrossScreenVisualTokens.UnknownState);
        AddSecondaryStatusVisual(404, "—", "تنبيهات مهمة", "لا توجد حالة حية موثقة", CrossScreenVisualTokens.UnknownState);
    }

    private void AddSecondaryStatusVisual(
        double top,
        string count,
        string title,
        string subtitle,
        string accent)
    {
        var card = ChromePanel(
            CrossScreenVisualTokens.SharedPanelBackground,
            CrossScreenVisualTokens.SharedSoftBorder,
            CrossScreenVisualTokens.SharedCardRadius);
        Place(SecondaryNativeLayer, card, 16, top, 215, 75);
        var badge = ChromePanel("#F8F9FB", "#E3E5E9", 8);
        Place(SecondaryNativeLayer, badge, 29, top + 12, 36, 32);
        Place(
            SecondaryNativeLayer,
            ChromeText(count, 18, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            39,
            top + 13,
            20,
            29);
        var titleText = ChromeText(title, 12.5, CrossScreenVisualTokens.SharedBodyText, FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, titleText, 77, top + 8, 126, 25);
        var subText = ChromeText(subtitle, 9.2, CrossScreenVisualTokens.SharedMutedText);
        subText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, subText, 77, top + 32, 126, 27);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false, Opacity = 0.9 },
            198,
            top + 27,
            9,
            9);
    }

    private void BuildSecondaryToolDock()
    {
        var dock = ChromePanel("#FFFCFBFA", "#DDD9D4", 16);
        Place(
            SecondaryNativeLayer,
            dock,
            0,
            CrossScreenVisualTokens.BottomDockTop,
            1536,
            CrossScreenVisualTokens.BottomDockHeight);
        Place(
            SecondaryNativeLayer,
            ChromeText("⌃", 18, "#475366", null, FlowDirection.LeftToRight),
            19,
            978,
            25,
            25);
        Place(
            SecondaryNativeLayer,
            ChromeText("أدواتك", 12, "#273349", FontWeights.SemiBold),
            58,
            974,
            62,
            25);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(CrossScreenVisualTokens.UnknownState), IsHitTestVisible = false },
            118,
            981,
            8,
            8);
        Place(
            SecondaryNativeLayer,
            ChromeText("UNKNOWN", 9, "#6B7280", FontWeights.SemiBold, FlowDirection.LeftToRight),
            128,
            976,
            53,
            20);

        AddSecondaryDockVisual(182, 103, "●", "GitHub", "#F3F5F8", "#161B22");
        AddSecondaryDockVisual(292, 78, "Ps", "Photoshop", "#122D55", "#31A8FF");
        AddSecondaryDockVisual(377, 86, "Ae", "After Effects", "#26154D", "#9999FF");
        AddSecondaryDockVisual(470, 82, "Pr", "Premiere", "#26154D", "#9999FF");
        AddSecondaryDockVisual(559, 96, "◇", "YASSIN", "#17182B", "#FFFFFF");
        AddSecondaryDockVisual(662, 104, "▦", "Tailscale", "#F0F1F4", "#111827");
        AddSecondaryDockVisual(773, 93, "⬡", "Models", "#F4F5F8", "#48556D");
        AddSecondaryDockVisual(873, 103, "▤", "Evidence", "#F4F5F8", "#25324A");
        AddSecondaryDockVisual(983, 126, "●", "Android Owner", "#F4F5F8", "#151D2C");

        var allTools = ChromePanel("#F8F8F7", "#DEDBD6", 10);
        Place(SecondaryNativeLayer, allTools, 1390, 973, 126, 40);
        var allToolsText = ChromeText("جميع الأدوات   ▦", 11, "#4E5868", FontWeights.SemiBold);
        allToolsText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, allToolsText, 1402, 980, 101, 25);
    }

    private void AddSecondaryDockVisual(
        double left,
        double width,
        string glyph,
        string label,
        string background,
        string accent)
    {
        var chip = ChromePanel(background, "#E1DED9", 9);
        Place(SecondaryNativeLayer, chip, left, 972, width, 42);
        Place(
            SecondaryNativeLayer,
            ChromeText(
                glyph,
                CrossScreenVisualTokens.DockGlyphSize,
                accent,
                FontWeights.SemiBold,
                FlowDirection.LeftToRight),
            left + 10,
            980,
            24,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText(
                label,
                CrossScreenVisualTokens.DockLabelSize,
                "#313B4C",
                FontWeights.SemiBold,
                FlowDirection.LeftToRight),
            left + 34,
            978,
            width - 42,
            26);
    }

    private void BuildSecondarySharedInteractions(ScreenKind screen)
    {
        AddSecondarySharedHotspot(505, 7, 525, 35, "search", "البحث العام", NativeUtility_Click);
        AddSecondarySharedHotspot(1209, 5, 43, 39, "theme", "المظهر", NativeUtility_Click);
        AddSecondarySharedHotspot(1257, 5, 43, 39, "notifications", "التنبيهات", NativeUtility_Click);
        AddSecondarySharedHotspot(1314, 3, 154, 43, "owner", "سياق المالك", NativeUtility_Click);

        AddSecondarySharedHotspot(1478, 72, 50, 70, "home", "الرئيسية", NativeHomeNav_Click);
        AddSecondarySharedHotspot(1478, 158, 50, 70, "project", "المشاريع", NativeHomeNav_Click);
        AddSecondarySharedHotspot(1478, 244, 50, 70, "council", "المجلس", NativeHomeNav_Click);
        AddSecondarySharedHotspot(1478, 330, 50, 70, "studio", "الاستوديو", NativeHomeNav_Click);
        AddSecondarySharedHotspot(1478, 416, 50, 70, "knowledge", "المعرفة", NativeHomeNav_Click);
        AddSecondarySharedHotspot(1478, 502, 50, 70, "tools", "الأدوات", NativeHomeNav_Click);
        AddSecondarySharedHotspot(1478, 588, 50, 70, "reports", "التقارير", NativeHomeNav_Click);
        AddSecondarySharedHotspot(1478, 858, 50, 70, "settings", "الإعدادات", NativeHomeNav_Click);

        if (screen is not ScreenKind.ProjectWorkspace and not ScreenKind.DecisionMode)
        {
            AddSecondarySharedHotspot(16, 62, 215, 159, "autopilot", "Autopilot — حالة التنفيذ", NativeStatus_Click);
            AddSecondarySharedHotspot(16, 228, 215, 75, "projects", "المشاريع النشطة", NativeStatus_Click);
            AddSecondarySharedHotspot(16, 316, 215, 75, "waiting", "المهام بانتظارك", NativeStatus_Click);
            AddSecondarySharedHotspot(16, 404, 215, 75, "alerts", "تنبيهات مهمة", NativeStatus_Click);
        }

        if (screen is ScreenKind.ProjectWorkspace or
            ScreenKind.SoftwareAutopilot or
            ScreenKind.StudioProject or
            ScreenKind.WorkReceipt)
        {
            AddSecondarySharedHotspot(182, 972, 103, 42, "github", "GitHub", NativeDockTool_Click);
            AddSecondarySharedHotspot(292, 972, 78, 42, "photoshop", "Photoshop", NativeDockTool_Click);
            AddSecondarySharedHotspot(377, 972, 86, 42, "after-effects", "After Effects", NativeDockTool_Click);
            AddSecondarySharedHotspot(470, 972, 82, 42, "premiere", "Premiere", NativeDockTool_Click);
            AddSecondarySharedHotspot(559, 972, 96, 42, "yassin", "YASSIN", NativeDockTool_Click);
            AddSecondarySharedHotspot(662, 972, 104, 42, "tailscale", "Tailscale", NativeDockTool_Click);
            AddSecondarySharedHotspot(773, 972, 93, 42, "models", "Models", NativeDockTool_Click);
            AddSecondarySharedHotspot(873, 972, 103, 42, "evidence", "Evidence", NativeDockTool_Click);
            AddSecondarySharedHotspot(983, 972, 126, 42, "android-owner", "Android Owner", NativeDockTool_Click);
            AddSecondarySharedHotspot(1390, 973, 126, 40, "all-tools", "جميع الأدوات", NativeDockTool_Click);
        }
    }

    private void AddSecondarySharedHotspot(
        double left,
        double top,
        double width,
        double height,
        string tag,
        string label,
        RoutedEventHandler handler)
    {
        var button = new Button
        {
            Width = width,
            Height = height,
            Tag = tag,
            ToolTip = label,
            Style = (Style)FindResource("HotspotButtonStyle"),
        };
        AutomationProperties.SetName(button, label);
        AutomationProperties.SetHelpText(button, "يعرض حالة موثقة أو UNKNOWN ولا يفترض اتصالًا أو نجاحًا.");
        Canvas.SetLeft(button, left);
        Canvas.SetTop(button, top);
        button.Click += handler;
        SecondaryInteractionCanvas.Children.Add(button);
    }

    private void BuildNativeProjectWorkspaceCore()
    {
        // Header and project identity.
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFDFBF8", "#F0EBE4", 0, new Thickness(0)),
            238,
            49,
            1232,
            151);

        Place(
            SecondaryNativeLayer,
            ChromeText("⌂  المشاريع   ›   Smart Secretary V2", 10.5, "#6C7686", FontWeights.SemiBold),
            270,
            62,
            320,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("Smart Secretary V2", 31, "#14213D", FontWeights.Bold, FlowDirection.LeftToRight),
            270,
            91,
            350,
            44);

        var runningBadge = ChromePanel("#EAFBF0", "#BFEBCF", 9);
        Place(SecondaryNativeLayer, runningBadge, 548, 98, 93, 28);
        Place(
            SecondaryNativeLayer,
            ChromeText("●  بيانات مرجعية", 10.5, "#6B7280", FontWeights.SemiBold),
            560,
            101,
            72,
            22);

        Place(
            SecondaryNativeLayer,
            ChromeText("تحديث الخصوصية وإدارة البيانات للسكرتير المدير الذكي", 18, "#374151", FontWeights.SemiBold),
            270,
            133,
            540,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText(
                "تحسين وإقفال سياسات سحابية، معالجة البيانات، وتجربة المستخدم، مع الالتزام الكامل بالمعايير الأمنية والحوكمة.",
                11.5,
                "#737B88"),
            270,
            163,
            705,
            24);

        AddProjectMetricCard(870, 104, 158, "بداية المشروع", "25 يناير 2025", "▣");
        AddProjectMetricCard(1038, 104, 158, "المدة المتوقعة", "30 يوم", "◷");
        AddProjectProgressCard(1206, 104, 228);

        Place(
            SecondaryNativeLayer,
            ChromeText("▢", 20, "#394457", null, FlowDirection.LeftToRight),
            1220,
            62,
            30,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("⇧", 20, "#394457", null, FlowDirection.LeftToRight),
            1273,
            62,
            30,
            30);
        var share = ChromePanel("#FFFFFF", "#E4E0DB", 8);
        Place(SecondaryNativeLayer, share, 1318, 58, 70, 34);
        Place(
            SecondaryNativeLayer,
            ChromeText("مشاركة", 10.5, "#465163", FontWeights.SemiBold),
            1332,
            63,
            46,
            24);
        var more = ChromePanel("#FFFFFF", "#E4E0DB", 8);
        Place(SecondaryNativeLayer, more, 1398, 58, 42, 34);
        Place(
            SecondaryNativeLayer,
            ChromeText("•••", 15, "#465163", FontWeights.Bold, FlowDirection.LeftToRight),
            1408,
            59,
            22,
            24);

        // Autopilot past/current/future rail.
        var autopilot = ChromePanel("#FFFCFBF8", "#E5E0D8", 14);
        Place(SecondaryNativeLayer, autopilot, 260, 204, 1184, 158);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#24C85A"), IsHitTestVisible = false },
            278,
            216,
            20,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("◉", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            284,
            218,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("Autopilot", 13, "#21304A", FontWeights.SemiBold, FlowDirection.LeftToRight),
            305,
            211,
            105,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("الماضي", 16, "#334155", FontWeights.SemiBold),
            517,
            222,
            95,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("الحالي", 18, "#1C64D9", FontWeights.Bold),
            802,
            213,
            92,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("المستقبل", 16, "#64748B", FontWeights.SemiBold),
            1117,
            222,
            105,
            28);

        var line = new Line
        {
            X1 = 397,
            Y1 = 274,
            X2 = 1283,
            Y2 = 274,
            Stroke = Brush("#D9DEE6"),
            StrokeThickness = 3,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(line);
        var activeLine = new Line
        {
            X1 = 397,
            Y1 = 274,
            X2 = 843,
            Y2 = 274,
            Stroke = Brush("#27BFD7"),
            StrokeThickness = 3,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(activeLine);

        AddTimelineNode(397, true, "تحليل المتطلبات", "2025/01/25", false);
        AddTimelineNode(493, true, "تصميم الحل", "2025/01/31", false);
        AddTimelineNode(591, true, "تطوير النسخة الأولى", "2025/02/10", false);
        AddTimelineNode(690, true, "مراجعة أمنية", "2025/02/18", false);
        AddTimelineNode(838, true, "تحسين الخصوصية\nوتكامل البيانات", "2025/02/25", true);
        AddTimelineNode(1003, false, "اختبارات شاملة", "2025/03/05", false);
        AddTimelineNode(1135, false, "مراجعة الامتثال", "2025/03/12", false);
        AddTimelineNode(1270, false, "الإطلاق النهائي", "2025/03/20", false);

        var plan = ChromePanel("#FAF7FF", "#DBCDF9", 9);
        Place(SecondaryNativeLayer, plan, 1275, 215, 151, 34);
        Place(
            SecondaryNativeLayer,
            ChromeText("عرض الخطة التفصيلية  ▣", 10, "#7256CA", FontWeights.SemiBold),
            1286,
            220,
            127,
            24);

        // Active Council graph.
        var council = ChromePanel("#FFFCFBF8", "#E5E0D8", 14);
        Place(SecondaryNativeLayer, council, 260, 374, 1184, 177);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            278,
            386,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("✦", 11, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            284,
            388,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("المجلس العامل على هذا المشروع", 17, "#17233B", FontWeights.SemiBold),
            310,
            381,
            260,
            31);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#28C767"), IsHitTestVisible = false },
            574,
            393,
            8,
            8);
        Place(
            SecondaryNativeLayer,
            ChromeText("6 وكلاء نشطين", 9.5, "#78818E"),
            590,
            386,
            90,
            24);

        AddCouncilRoutingPath("M 332,460 C 376,415 424,415 470,460 S 560,505 603,460", "#8A65E8", 0.36);
        AddCouncilRoutingPath("M 470,460 C 520,420 558,420 603,460 S 694,500 738,460", "#51B8E4", 0.42);
        AddCouncilRoutingPath("M 603,460 C 657,420 696,420 738,460 S 830,500 872,460", "#F5A45B", 0.42);
        AddCouncilRoutingPath("M 738,460 C 793,420 831,420 872,460 S 965,500 1006,460", "#2BC7DC", 0.42);
        AddCouncilRoutingPath("M 872,460 C 925,420 965,420 1006,460 S 1096,500 1138,460", "#7D68E8", 0.38);

        AddProjectCouncilRole(294, 421, "#EEE7FF", "#7B4EE0", "◉", "Evidence", "تحليل الأدلة");
        AddProjectCouncilRole(431, 421, "#EAF4FF", "#2982E5", "●", "UX", "تصميم التجربة");
        AddProjectCouncilRole(568, 421, "#FFF0F0", "#E94B5D", "T", "Red Team", "اختبار الثغرات");
        AddProjectCouncilRole(705, 414, "#FFF8E5", "#F09A21", "♕", "Studio", "التطوير والتصميم", true);
        AddProjectCouncilRole(842, 421, "#E8FBFD", "#24BDD2", "▣", "Security", "المراجعة الأمنية");
        AddProjectCouncilRole(979, 421, "#F2EDFF", "#8A58E5", "⌘", "Synthesis", "دمج النتائج");

        var routing = ChromePanel("#FFFDFCFA", "#E9E3DA", 11);
        Place(SecondaryNativeLayer, routing, 1217, 393, 205, 139);
        Place(
            SecondaryNativeLayer,
            ChromeText("توجيه المهام بين الوكلاء", 11.5, "#2F394A", FontWeights.SemiBold),
            1233,
            403,
            170,
            23);
        var routingBody = ChromeText(
            "يقوم Autopilot بتوجيه المهام تلقائياً\nبين الوكلاء بناءً على سياق المشروع\nوالنتائج المرحلية.",
            9.2,
            "#727B88");
        routingBody.TextAlignment = TextAlignment.Right;
        routingBody.LineHeight = 16;
        Place(SecondaryNativeLayer, routingBody, 1233, 432, 170, 53);
        var routingAction = ChromePanel("#F8F7FF", "#DCD1F5", 8);
        Place(SecondaryNativeLayer, routingAction, 1240, 492, 167, 29);
        Place(
            SecondaryNativeLayer,
            ChromeText("عرض سجل التوجيه  ▥", 9.5, "#6C55B8", FontWeights.SemiBold),
            1251,
            496,
            145,
            20);

        BuildNativeProjectWorkspaceLeftRail();
        BuildNativeProjectWorkspaceFilmstrip();
        BuildNativeProjectWorkspaceBottomPanels();
    }

    private void BuildNativeProjectWorkspaceLeftRail()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFF8F5EF", "#EEE8DF", 0, new Thickness(0, 0, 1, 0)),
            0,
            49,
            238,
            914);

        var auto = ChromePanel("#FFFCFBF8", "#DDE2E7", 14);
        Place(SecondaryNativeLayer, auto, 16, 62, 215, 159);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#24C85A"), IsHitTestVisible = false },
            31,
            79,
            13,
            13);
        Place(
            SecondaryNativeLayer,
            ChromeText("Autopilot", 16, "#1E293B", FontWeights.SemiBold, FlowDirection.LeftToRight),
            55,
            70,
            115,
            27);
        Place(
            SecondaryNativeLayer,
            ChromeText("مرجع بصري", 10, CrossScreenVisualTokens.UnknownState, FontWeights.SemiBold),
            55,
            96,
            80,
            20);
        var waveform = new Polyline
        {
            Stroke = Brush("#54E98A"),
            StrokeThickness = 2.3,
            Opacity = 0.9,
            IsHitTestVisible = false,
            Points = new PointCollection
            {
                new(0, 22), new(19, 21), new(30, 16), new(42, 25), new(53, 20),
                new(63, 5), new(74, 34), new(84, 10), new(95, 21), new(114, 19),
                new(132, 23), new(150, 22)
            }
        };
        Place(SecondaryNativeLayer, waveform, 46, 113, 150, 40);
        var status = ChromeText(
            "يدير تنفيذ المشروع وفق الخطة\nمراقبة الجودة والامتثال الأمني",
            10.5,
            "#4B5565",
            FontWeights.SemiBold);
        status.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, status, 38, 158, 170, 50);

        var nav = ChromePanel("#FFFCFBF8", "#E7E2DA", 12);
        Place(SecondaryNativeLayer, nav, 16, 232, 215, 213);
        AddProjectRailItem(244, "⌂", "نظرة عامة على المشروع", "", true);
        AddProjectRailItem(283, "▤", "المهام", "12", false);
        AddProjectRailItem(322, "▧", "الوثائق", "28", false);
        AddProjectRailItem(361, "◉", "القرارات", "7", false);
        AddProjectRailItem(400, "▢", "المناقشات", "14", false);
        AddProjectRailItem(439, "◷", "النسخ السابقة", "5", false);

        var goals = ChromePanel("#FFFCFBF8", "#E7E2DA", 12);
        Place(SecondaryNativeLayer, goals, 16, 456, 215, 201);
        Place(
            SecondaryNativeLayer,
            ChromeText("◎", 25, "#E6A127", FontWeights.Bold, FlowDirection.LeftToRight),
            30,
            470,
            30,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("أهداف المشروع", 16, "#273247", FontWeights.SemiBold),
            68,
            468,
            132,
            30);
        AddGoalLine(508, "تحسين الخصوصية وإدارة البيانات");
        AddGoalLine(538, "رفع معايير الأمان والامتثال");
        AddGoalLine(568, "تحسين تجربة المستخدم");
        AddGoalLine(598, "إطلاق نسخة مستقرة ومعتمدة");

        var projectState = ChromePanel("#FFFCFBF8", "#E7E2DA", 12);
        Place(SecondaryNativeLayer, projectState, 16, 670, 215, 220);
        Place(
            SecondaryNativeLayer,
            ChromeText("⚑", 22, "#3576E8", FontWeights.SemiBold, FlowDirection.LeftToRight),
            190,
            681,
            24,
            26);
        Place(
            SecondaryNativeLayer,
            ChromeText("حالة المشروع", 16, "#273247", FontWeights.SemiBold),
            75,
            680,
            108,
            28);

        var progressRing = new Ellipse
        {
            Stroke = Brush("#E4EAF1"),
            StrokeThickness = 8,
            Fill = Brushes.Transparent,
            IsHitTestVisible = false,
        };
        Place(SecondaryNativeLayer, progressRing, 39, 719, 84, 84);
        var arc = new Path
        {
            Data = Geometry.Parse("M 81,723 A 38,38 0 1 1 50,790"),
            Stroke = Brush("#357BE8"),
            StrokeThickness = 8,
            StrokeStartLineCap = PenLineCap.Round,
            StrokeEndLineCap = PenLineCap.Round,
            Fill = Brushes.Transparent,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(arc);
        Place(
            SecondaryNativeLayer,
            ChromeText("—", 17, "#263247", FontWeights.Bold, FlowDirection.LeftToRight),
            59,
            745,
            48,
            28);
        AddProjectStateBullet(720, "#25C86A", "12 / 18 مكتملة");
        AddProjectStateBullet(748, "#2F75F3", "4 قيد التنفيذ");
        AddProjectStateBullet(776, "#F25A5A", "2 لم تبدأ");

        var plan = ChromePanel("#FFFFFF", "#E2DED8", 8);
        Place(SecondaryNativeLayer, plan, 31, 821, 185, 42);
        Place(
            SecondaryNativeLayer,
            ChromeText("عرض خطة المشروع   ←", 10.5, "#394557", FontWeights.SemiBold),
            46,
            830,
            154,
            24);
    }

    private void AddProjectRailItem(
        double top,
        string glyph,
        string label,
        string count,
        bool active)
    {
        if (active)
        {
            Place(
                SecondaryNativeLayer,
                ChromePanel("#EAF3FF", "#D8E9FF", 8),
                27,
                top,
                193,
                34);
        }

        Place(
            SecondaryNativeLayer,
            ChromeText(
                glyph,
                15,
                active ? "#2F75F3" : "#617086",
                FontWeights.SemiBold,
                FlowDirection.LeftToRight),
            37,
            top + 5,
            22,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText(
                label,
                11.5,
                active ? "#2867C8" : "#4C596B",
                active ? FontWeights.SemiBold : FontWeights.Normal),
            69,
            top + 4,
            122,
            25);
        if (!string.IsNullOrWhiteSpace(count))
        {
            Place(
                SecondaryNativeLayer,
                ChromeText(count, 10, "#5D697A", FontWeights.SemiBold, FlowDirection.LeftToRight),
                195,
                top + 5,
                20,
                22);
        }
    }

    private void AddGoalLine(double top, string text)
    {
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#25C86A"), IsHitTestVisible = false },
            205,
            top + 7,
            7,
            7);
        Place(
            SecondaryNativeLayer,
            ChromeText(text, 10.3, "#4B5565"),
            41,
            top,
            156,
            24);
    }

    private void AddProjectStateBullet(double top, string color, string text)
    {
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(color), IsHitTestVisible = false },
            137,
            top + 7,
            8,
            8);
        Place(
            SecondaryNativeLayer,
            ChromeText(text, 10.2, "#5A6574"),
            151,
            top,
            69,
            24);
    }

    private void BuildNativeProjectWorkspaceFilmstrip()
    {
        var filmstrip = ChromePanel("#FFFCFBF8", "#E5E0D8", 13);
        Place(SecondaryNativeLayer, filmstrip, 260, 558, 1184, 194);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            278,
            570,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("▣", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            284,
            572,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("شريط إصدارات المشروع", 17, "#17233B", FontWeights.SemiBold),
            312,
            565,
            196,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("5 نسخ رئيسية", 10, "#77818F"),
            512,
            570,
            86,
            23);

        var compare = ChromePanel("#F8FBFF", "#7CB8F2", 9);
        Place(SecondaryNativeLayer, compare, 1302, 566, 124, 32);
        Place(
            SecondaryNativeLayer,
            ChromeText("مقارنة الإصدارات  ⤢", 10, "#3475C7", FontWeights.SemiBold),
            1314,
            571,
            102,
            21);

        AddVersionCard(274, "النسخة الأصلية", "Before UI", "v0.1", "2025/01/28", "#EDF4FB", false);
        AddVersionCard(493, "مراجعة تجربة المستخدم", "UX Revision", "v0.3", "2025/02/05", "#F4F6FD", false);
        AddVersionCard(712, "النسخة المعادة", "Returned Version", "v1.0", "2025/02/12", "#EEF2F7", false);
        AddVersionCard(931, "مراجعة ثانية", "Revision 2", "v1.4", "2025/02/20", "#F5F7FC", false);
        AddVersionCard(1150, "النتيجة المعتمدة", "VERIFIED", "v2.0", "2025/02/25", "#EFFBF4", true);
    }

    private void AddVersionCard(
        double left,
        string eyebrow,
        string title,
        string version,
        string date,
        string background,
        bool verified)
    {
        var card = ChromePanel(background, verified ? "#35C778" : "#DDE3EA", 9);
        Place(SecondaryNativeLayer, card, left, 604, 205, 132);
        Place(
            SecondaryNativeLayer,
            ChromeText(eyebrow, 9.4, "#637084", FontWeights.SemiBold),
            left + 12,
            610,
            150,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 13, verified ? "#159F50" : "#233047", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 12,
            629,
            150,
            24);

        var preview = ChromePanel("#FFFFFF", "#E4E7EB", 6);
        Place(SecondaryNativeLayer, preview, left + 12, 656, 181, 49);
        AddMiniScreenPreview(left + 18, 661, verified);

        var versionBadge = ChromePanel(verified ? "#DFF7E9" : "#F4F5F7", "#E0E3E7", 6);
        Place(SecondaryNativeLayer, versionBadge, left + 12, 709, 42, 20);
        Place(
            SecondaryNativeLayer,
            ChromeText(version, 8.5, verified ? "#1A9F52" : "#556273", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 19,
            711,
            30,
            15);
        Place(
            SecondaryNativeLayer,
            ChromeText(date, 8.5, "#7B8491", null, FlowDirection.LeftToRight),
            left + 112,
            711,
            80,
            15);

        if (verified)
        {
            var badge = ChromePanel("#DFF7E9", "#BEEBCF", 7);
            Place(SecondaryNativeLayer, badge, left + 121, 610, 70, 20);
            Place(
                SecondaryNativeLayer,
                ChromeText("✓ VERIFIED", 8.3, "#1A9F52", FontWeights.SemiBold, FlowDirection.LeftToRight),
                left + 130,
                612,
                55,
                15);
        }
    }

    private void AddMiniScreenPreview(double left, double top, bool verified)
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#F7F9FC", "#EEF1F5", 4),
            left,
            top,
            169,
            39);
        for (var row = 0; row < 3; row++)
        {
            Place(
                SecondaryNativeLayer,
                ChromePanel(
                    verified && row == 0 ? "#E9FAEF" : "#EAF2FB",
                    verified && row == 0 ? "#D2F0DE" : "#E0E9F4",
                    2),
                left + 10,
                top + 6 + (row * 9),
                53 + (row * 13),
                4);
        }
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFFFF", "#EDF0F4", 3),
            left + 102,
            top + 6,
            52,
            27);
    }

    private void BuildNativeProjectWorkspaceBottomPanels()
    {
        var decision = ChromePanel("#FFFCFBF8", "#E5E0D8", 11);
        Place(SecondaryNativeLayer, decision, 260, 760, 431, 203);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#F2AA29"), IsHitTestVisible = false },
            278,
            772,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("▣", 11, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            284,
            774,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("مكدس القرارات  Decision Stack", 15.5, "#273247", FontWeights.SemiBold),
            310,
            767,
            245,
            30);
        var newDecision = ChromePanel("#F9F6FF", "#DDD0F5", 7);
        Place(SecondaryNativeLayer, newDecision, 575, 769, 98, 29);
        Place(
            SecondaryNativeLayer,
            ChromeText("+   قرار جديد", 9.5, "#6D55B9", FontWeights.SemiBold),
            592,
            773,
            68,
            20);
        AddDecisionRow(809, "#25C86A", "تم اعتماد", "اعتماد سياسة خصوصية البيانات v2", "#DFF7E9");
        AddDecisionRow(846, "#2F75F3", "قيد المراجعة", "دمج طبقة التشفير الجديدة", "#E9F2FF");
        AddDecisionRow(883, "#F0A51F", "مطلوب قرار", "تفعيل التسجيل المحلي للمكالمات؟", "#FFF3D9");
        AddDecisionRow(920, "#EF596A", "مرفوض", "إزالة ميزة التحويل التلقائي للملفات", "#FFE9EC");

        var tools = ChromePanel("#FFFCFBF8", "#E5E0D8", 11);
        Place(SecondaryNativeLayer, tools, 702, 760, 397, 203);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            720,
            772,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("ϟ", 12, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            726,
            773,
            12,
            16);
        Place(
            SecondaryNativeLayer,
            ChromeText("الأدوات النشطة في هذا المشروع", 15.5, "#273247", FontWeights.SemiBold),
            752,
            767,
            240,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("5 أدوات مفعلة", 9.5, "#7B8491"),
            1005,
            771,
            80,
            23);
        AddActiveToolTile(719, 808, "✹", "Claude 3.5 Sonnet", "تحليل ومتطلبات", "#E95046");
        AddActiveToolTile(842, 808, "●", "Figma", "تصميم واجهات", "#A25BEC");
        AddActiveToolTile(965, 808, "◆", "Supabase", "إدارة البيانات", "#28C983");
        AddActiveToolTile(719, 865, "●", "GitHub", "إدارة الإصدارات", "#171B23");
        AddActiveToolTile(842, 865, "◈", "Playwright", "اختبار تلقائي", "#E84B86");
        var manage = ChromePanel("#FFFFFF", "#E2DED8", 7);
        Place(SecondaryNativeLayer, manage, 966, 865, 112, 42);
        Place(
            SecondaryNativeLayer,
            ChromeText("إدارة الأدوات   ⚙", 9.5, "#465163", FontWeights.SemiBold),
            978,
            875,
            87,
            21);

        var execution = ChromePanel("#FFFCFBF8", "#E5E0D8", 11);
        Place(SecondaryNativeLayer, execution, 1110, 760, 334, 203);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#F1A62B"), IsHitTestVisible = false },
            1128,
            772,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("▥", 11, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1134,
            774,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("معلومات التنفيذ الحالية", 15.5, "#273247", FontWeights.SemiBold),
            1160,
            767,
            220,
            30);
        AddExecutionRow(806, "النموذج النشط", "Claude 3.5 Sonnet", "✹", "#EA5D50");
        AddExecutionRow(838, "عمق التفكير", "Deep • موسع", "◷", "#576579");
        AddExecutionRow(870, "آخر نقطة تحقق", "2025/02/25 - 14:32", "✓", "#25C86A");
        AddExecutionRow(902, "المشكلات المستعادة", "4 مشكلات", "⚠", "#E68A27");
        AddExecutionRow(934, "مدة التشغيل", "2 يوم 6 ساعات 14 دقيقة", "◷", "#E24F5C");
    }

    private void AddDecisionRow(
        double top,
        string accent,
        string state,
        string title,
        string stateBackground)
    {
        var row = ChromePanel("#FFFFFF", "#ECE8E2", 6);
        Place(SecondaryNativeLayer, row, 273, top, 405, 30);
        var stateBadge = ChromePanel(stateBackground, stateBackground, 6);
        Place(SecondaryNativeLayer, stateBadge, 284, top + 5, 77, 20);
        Place(
            SecondaryNativeLayer,
            ChromeText(state, 8.3, accent, FontWeights.SemiBold),
            293,
            top + 7,
            61,
            15);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 9.4, "#384455", FontWeights.SemiBold),
            373,
            top + 4,
            238,
            21);
        Place(
            SecondaryNativeLayer,
            ChromeText("•••", 10, "#7E8793", FontWeights.Bold, FlowDirection.LeftToRight),
            647,
            top + 6,
            20,
            16);
    }

    private void AddActiveToolTile(
        double left,
        double top,
        string glyph,
        string title,
        string subtitle,
        string accent)
    {
        var tile = ChromePanel("#FFFFFF", "#E7E3DE", 7);
        Place(SecondaryNativeLayer, tile, left, top, 112, 49);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 18, accent, FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 9,
            top + 8,
            24,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 8.4, "#2F394A", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 35,
            top + 7,
            72,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText(subtitle, 7.5, "#7D8693"),
            left + 35,
            top + 24,
            72,
            16);
    }

    private void AddExecutionRow(
        double top,
        string label,
        string value,
        string glyph,
        string accent)
    {
        var row = ChromePanel("#FFFFFF", "#ECE8E2", 5);
        Place(SecondaryNativeLayer, row, 1122, top, 309, 27);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 11, accent, FontWeights.SemiBold, FlowDirection.LeftToRight),
            1130,
            top + 4,
            18,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 8.8, "#667181"),
            1153,
            top + 3,
            84,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 8.8, "#354052", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1242,
            top + 3,
            176,
            20);
    }

    private void AddProjectMetricCard(
        double left,
        double top,
        double width,
        string label,
        string value,
        string glyph)
    {
        var card = ChromePanel("#FFFCFBF9", "#E4E0DB", 9);
        Place(SecondaryNativeLayer, card, left, top, width, 68);
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 9.5, "#7B8491"),
            left + 14,
            top + 9,
            width - 44,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 12.5, "#263247", FontWeights.SemiBold),
            left + 14,
            top + 30,
            width - 44,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 18, "#4D5B73", null, FlowDirection.LeftToRight),
            left + width - 31,
            top + 25,
            20,
            24);
    }

    private void AddProjectProgressCard(double left, double top, double width)
    {
        var card = ChromePanel("#FFFCFBF9", "#E4E0DB", 9);
        Place(SecondaryNativeLayer, card, left, top, width, 68);
        Place(
            SecondaryNativeLayer,
            ChromeText("التقدم العام", 9.5, "#7B8491"),
            left + 14,
            top + 9,
            80,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText("—", 14, "#243049", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 14,
            top + 31,
            43,
            22);
        var track = ChromePanel("#E0E8F3", "#E0E8F3", 4);
        Place(SecondaryNativeLayer, track, left + 68, top + 36, width - 84, 8);
        var fill = ChromePanel("#2F75F3", "#2F75F3", 4);
        Place(SecondaryNativeLayer, fill, left + 68, top + 36, (width - 84) * 0.68, 8);
    }

    private void AddTimelineNode(
        double centerX,
        bool complete,
        string label,
        string date,
        bool current)
    {
        var ringColor = current ? "#2F75F3" : complete ? "#25C86A" : "#B8C0CC";
        var fillColor = current ? "#E9F2FF" : complete ? "#25C86A" : "#D7DCE3";
        var size = current ? 34 : 24;
        var top = current ? 257 : 262;
        var left = centerX - (size / 2);

        if (current)
        {
            Place(
                SecondaryNativeLayer,
                new Ellipse
                {
                    Fill = Brush("#DDEBFF"),
                    Stroke = Brush("#79A7F4"),
                    StrokeThickness = 1,
                    IsHitTestVisible = false,
                },
                left - 7,
                top - 7,
                size + 14,
                size + 14);
        }

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush(fillColor),
                Stroke = Brush(ringColor),
                StrokeThickness = current ? 3 : 2,
                IsHitTestVisible = false,
            },
            left,
            top,
            size,
            size);

        if (complete && !current)
        {
            Place(
                SecondaryNativeLayer,
                ChromeText("✓", 13, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
                left + 6,
                top + 1,
                14,
                18);
        }
        else if (current)
        {
            Place(
                SecondaryNativeLayer,
                ChromeText("●", 13, "#2F75F3", FontWeights.Bold, FlowDirection.LeftToRight),
                left + 10,
                top + 6,
                14,
                18);
        }

        var labelText = ChromeText(label, current ? 10.4 : 9.5, current ? "#1C64D9" : "#4D596B", current ? FontWeights.SemiBold : FontWeights.Normal);
        labelText.TextAlignment = TextAlignment.Center;
        labelText.TextWrapping = TextWrapping.Wrap;
        Place(SecondaryNativeLayer, labelText, centerX - 62, 296, 124, current ? 43 : 34);

        Place(
            SecondaryNativeLayer,
            ChromeText(date, 8.8, "#7B8491", null, FlowDirection.LeftToRight),
            centerX - 42,
            current ? 337 : 329,
            84,
            18);
    }

    private void AddCouncilRoutingPath(string data, string color, double opacity)
    {
        var path = new Path
        {
            Data = Geometry.Parse(data),
            Stroke = Brush(color),
            StrokeThickness = 1.6,
            StrokeDashArray = new DoubleCollection { 1, 4 },
            Opacity = opacity,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(path);
    }

    private void AddProjectCouncilRole(
        double left,
        double top,
        string background,
        string accent,
        string glyph,
        string title,
        string subtitle,
        bool active = false)
    {
        if (active)
        {
            Place(
                SecondaryNativeLayer,
                new Ellipse
                {
                    Fill = Brush("#FFF9E7"),
                    Stroke = Brush("#F7D98A"),
                    StrokeThickness = 1,
                    Opacity = 0.75,
                    IsHitTestVisible = false,
                },
                left - 16,
                top - 16,
                100,
                100);
        }

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush(background),
                Stroke = Brush(accent),
                StrokeThickness = 1.6,
                IsHitTestVisible = false,
            },
            left,
            top,
            68,
            68);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 25, accent, FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 18,
            top + 14,
            34,
            34);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#25C86A"), IsHitTestVisible = false },
            left + 54,
            top + 50,
            17,
            17);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 58,
            top + 50,
            11,
            13);
        var titleText = ChromeText(title, 11, "#17233B", FontWeights.SemiBold, FlowDirection.LeftToRight);
        titleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, titleText, left - 19, top + 72, 106, 20);
        var subtitleText = ChromeText(subtitle, 9, active ? "#D08314" : "#7A8391", active ? FontWeights.SemiBold : FontWeights.Normal);
        subtitleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, subtitleText, left - 29, top + 91, 126, 20);
    }

    private void BuildNativeSoftwareAutopilot()
    {
        BuildNativeAutopilotHeader();
        BuildNativeAutopilotTimeline();
        BuildNativeAutopilotDiffAndBranches();
        BuildNativeAutopilotHistory();
    }

    private void BuildNativeAutopilotHeader()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFDFBF8", "#F0EBE4", 0, new Thickness(0)),
            238,
            49,
            1232,
            203);

        Place(
            SecondaryNativeLayer,
            ChromeText("‹  المشاريع   /   Command Center Runtime", 10.5, "#707A89", FontWeights.SemiBold),
            340,
            62,
            320,
            24);

        Place(
            SecondaryNativeLayer,
            ChromePanel("#EFE9FF", "#D3C7F7", 19),
            250,
            82,
            72,
            72);
        Place(
            SecondaryNativeLayer,
            ChromeText("◇", 41, "#7251E3", FontWeights.Bold, FlowDirection.LeftToRight),
            267,
            91,
            40,
            50);

        Place(
            SecondaryNativeLayer,
            ChromeText("Memory Fabric Repair", 31, "#13203A", FontWeights.Bold, FlowDirection.LeftToRight),
            340,
            88,
            360,
            45);
        Place(
            SecondaryNativeLayer,
            ChromeText("تحسين استقرار الذاكرة وأداء المشغل في مركز القيادة", 15.5, "#596476", FontWeights.SemiBold),
            340,
            127,
            430,
            30);

        AddTagChip(340, 160, 92, "نظام أساسي", "#F3F6FF", "#4769B3");
        AddTagChip(438, 160, 45, "C++", "#F7F7FA", "#6A7180");
        AddTagChip(489, 160, 67, "runtime", "#F7F7FA", "#6A7180");
        AddTagChip(562, 160, 66, "memory", "#F7F7FA", "#6A7180");
        AddTagChip(634, 160, 84, "performance", "#F7F7FA", "#6A7180");
        AddTagChip(724, 160, 36, "+", "#FFFFFF", "#687384");

        AddAutopilotHeaderCard(775, 60, 205, "حالة المشروع", "يسير وفق الخطة", "◯", "#25C86A");
        AddAutopilotHeaderCard(991, 60, 197, "الفرع النشط", "feature/memory-fabric", "⌘", "#3B6BD8");
        AddAutopilotHeaderCard(1198, 60, 257, "النموذج النشط", "GPT-5.6 Sol · Deep", "AI", "#7D55E7");

        var tabBar = ChromePanel("#FFFDFBF8", "#EEE9E2", 0, new Thickness(0, 0, 0, 1));
        Place(SecondaryNativeLayer, tabBar, 238, 199, 1232, 53);
        AddAutopilotTab(250, "⌂", "نظرة عامة", true);
        AddAutopilotTab(366, "‹›", "الكود", false);
        AddAutopilotTab(470, "⌘", "الفروع", false);
        AddAutopilotTab(577, "♙", "الاختبارات الآن", false);
        AddAutopilotTab(709, "☁", "البناء و CI", false);
        AddAutopilotTab(834, "♧", "الأدلة والتشغيل", false);
        AddAutopilotTab(982, "◉", "المراجعات", false);
        AddAutopilotTab(1100, "⚙", "الإعدادات", false);

        var taskButton = ChromePanel("#2F75F3", "#2F75F3", 8);
        Place(SecondaryNativeLayer, taskButton, 1272, 207, 169, 37);
        Place(
            SecondaryNativeLayer,
            ChromeText("✦  بدء مهمة Autopilot", 11, "#FFFFFF", FontWeights.SemiBold),
            1287,
            214,
            138,
            23);
    }

    private void AddTagChip(
        double left,
        double top,
        double width,
        string text,
        string background,
        string foreground)
    {
        var chip = ChromePanel(background, "#E4E2DF", 10);
        Place(SecondaryNativeLayer, chip, left, top, width, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText(text, 9.5, foreground, FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 10,
            top + 3,
            width - 20,
            18);
    }

    private void AddAutopilotHeaderCard(
        double left,
        double top,
        double width,
        string title,
        string value,
        string glyph,
        string accent)
    {
        var card = ChromePanel("#FFFCFBF9", "#E4E0DB", 10);
        Place(SecondaryNativeLayer, card, left, top, width, 126);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 10.5, "#647083", FontWeights.SemiBold),
            left + 15,
            top + 11,
            width - 55,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 21, accent, FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 16,
            top + 45,
            33,
            33);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 12.5, "#263247", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 54,
            top + 43,
            width - 66,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("حالة مرجعية — لا تفترض اتصالاً حياً", 8.5, "#8A929E"),
            left + 15,
            top + 87,
            width - 30,
            22);
    }

    private void AddAutopilotTab(
        double left,
        string glyph,
        string text,
        bool active)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 14, active ? "#2F75F3" : "#647083", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left,
            213,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText(text, 10.3, active ? "#2F75F3" : "#596476", active ? FontWeights.SemiBold : FontWeights.Normal),
            left + 25,
            210,
            87,
            25);
        if (active)
        {
            Place(
                SecondaryNativeLayer,
                ChromePanel("#2F75F3", "#2F75F3", 1),
                left - 2,
                247,
                96,
                3);
        }
    }

    private void BuildNativeAutopilotTimeline()
    {
        var rail = ChromePanel("#FFFCFBF8", "#E5E0D8", 12);
        Place(SecondaryNativeLayer, rail, 244, 260, 958, 209);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            262,
            273,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("♜", 11, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            268,
            275,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("سير التطوير والفرع (Checkpoint)", 15.5, "#283347", FontWeights.SemiBold),
            295,
            269,
            260,
            29);
        Place(
            SecondaryNativeLayer,
            ChromeText("يمكنك الرجوع إلى أي نقطة في التاريخ أو إنشاء فرع جديد", 9.5, "#7960CF"),
            782,
            272,
            300,
            24);

        var timeline = new Line
        {
            X1 = 315,
            Y1 = 336,
            X2 = 1152,
            Y2 = 336,
            Stroke = Brush("#CBD6E4"),
            StrokeThickness = 3,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(timeline);

        AddCheckpointNode(318, "#5D6BE6", "main", "v2.4.1", false, false);
        AddCheckpointNode(450, "#25C86A", "a3ff9c1", "إصلاح تسرب الذاكرة", true, false);
        AddCheckpointNode(600, "#25C86A", "d72e9b", "تحسين تجميع الكاش", true, false);
        AddCheckpointNode(737, "#8759E8", "f4c2d0", "نقطة الفرع", true, true);
        AddCheckpointNode(880, "#2F75F3", "e1a7b3", "تجربة خوارزمية جديدة", true, false);
        AddCheckpointNode(1026, "#25C86A", "9c8d2a", "تحسين إدارة الخيوط", true, false);
        AddCheckpointNode(1158, "#B8C4D2", "…", "التالي", false, false);

        var branchA = ChromePanel("#ECFBF4", "#B9EFD4", 8);
        Place(SecondaryNativeLayer, branchA, 482, 406, 245, 49);
        Place(
            SecondaryNativeLayer,
            ChromeText("A", 16, "#25B870", FontWeights.Bold, FlowDirection.LeftToRight),
            497,
            417,
            20,
            25);
        Place(
            SecondaryNativeLayer,
            ChromeText("Branch A", 11, "#2D5C48", FontWeights.SemiBold, FlowDirection.LeftToRight),
            523,
            410,
            82,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("feature/memory-new-allocator", 8.5, "#4B7867", null, FlowDirection.LeftToRight),
            523,
            431,
            185,
            17);

        var branchB = ChromePanel("#EFF7FF", "#BFDDF7", 8);
        Place(SecondaryNativeLayer, branchB, 827, 406, 235, 49);
        Place(
            SecondaryNativeLayer,
            ChromeText("B", 16, "#2F75F3", FontWeights.Bold, FlowDirection.LeftToRight),
            842,
            417,
            20,
            25);
        Place(
            SecondaryNativeLayer,
            ChromeText("Branch B", 11, "#315C85", FontWeights.SemiBold, FlowDirection.LeftToRight),
            868,
            410,
            82,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("feature/memory-garbage-collector", 8.5, "#52799B", null, FlowDirection.LeftToRight),
            868,
            431,
            178,
            17);

        var recovery = ChromePanel("#FFFCFBF8", "#E5E0D8", 12);
        Place(SecondaryNativeLayer, recovery, 1212, 260, 240, 209);
        Place(
            SecondaryNativeLayer,
            ChromeText("التحكم الزمني والاستعادة", 14, "#283347", FontWeights.SemiBold),
            1232,
            274,
            190,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("◀   ●──●──◉──●   ▶", 19, "#8157E9", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1235,
            323,
            180,
            34);
        var restore = ChromePanel("#FBF8FF", "#DCCEF8", 7);
        Place(SecondaryNativeLayer, restore, 1250, 368, 164, 32);
        Place(
            SecondaryNativeLayer,
            ChromeText("الرجوع إلى هذه النقطة", 9.5, "#6C54BA", FontWeights.SemiBold),
            1266,
            373,
            130,
            21);
        Place(
            SecondaryNativeLayer,
            ChromeText("f4c2d0 · 2025-01-25 14:32", 9, "#6D7786", null, FlowDirection.LeftToRight),
            1248,
            416,
            170,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("نقطة الفرع: تحسين الذاكرة", 9.5, "#374254"),
            1248,
            437,
            170,
            20);
    }

    private void AddCheckpointNode(
        double centerX,
        string accent,
        string title,
        string subtitle,
        bool complete,
        bool current)
    {
        var size = current ? 34 : 23;
        var top = current ? 319 : 324;
        if (current)
        {
            Place(
                SecondaryNativeLayer,
                new Ellipse
                {
                    Fill = Brush("#EFE8FF"),
                    Stroke = Brush("#B498F7"),
                    StrokeThickness = 1,
                    IsHitTestVisible = false,
                },
                centerX - 24,
                top - 8,
                50,
                50);
        }

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush(complete ? accent : "#F4F6F8"),
                Stroke = Brush(accent),
                StrokeThickness = 2,
                IsHitTestVisible = false,
            },
            centerX - (size / 2),
            top,
            size,
            size);

        if (complete && !current)
        {
            Place(
                SecondaryNativeLayer,
                ChromeText("✓", 11, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
                centerX - 6,
                top + 1,
                13,
                16);
        }
        else if (current)
        {
            Place(
                SecondaryNativeLayer,
                ChromeText("●", 11, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
                centerX - 5,
                top + 7,
                12,
                15);
        }

        var titleText = ChromeText(title, 9.8, current ? "#7046D4" : "#364254", FontWeights.SemiBold, FlowDirection.LeftToRight);
        titleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, titleText, centerX - 52, 355, 104, 18);
        var subtitleText = ChromeText(subtitle, 8.5, current ? "#7046D4" : "#77818F", current ? FontWeights.SemiBold : FontWeights.Normal);
        subtitleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, subtitleText, centerX - 68, 374, 136, 24);
    }

    private void BuildNativeAutopilotDiffAndBranches()
    {
        var diff = ChromePanel("#FFFCFBF8", "#E5E0D8", 12);
        Place(SecondaryNativeLayer, diff, 16, 480, 578, 292);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            33,
            492,
            23,
            23);
        Place(
            SecondaryNativeLayer,
            ChromeText("∆", 12, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            39,
            494,
            12,
            16);
        Place(
            SecondaryNativeLayer,
            ChromeText("مقارنة التغييرات", 16, "#273247", FontWeights.SemiBold),
            66,
            487,
            170,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("src/memory/FabricAllocator.cpp", 10, "#6D7786", null, FlowDirection.LeftToRight),
            38,
            528,
            250,
            22);

        AddCodePane(30, 553, 270, 205, false);
        AddCodePane(306, 553, 274, 205, true);

        AddBranchScorecard(607, "A", "feature/memory-new-allocator", "#27BD73", true);
        AddBranchScorecard(858, "B", "feature/memory-garbage-collector", "#2F75F3", false);

        var ownerDecision = ChromePanel("#FFFCFBF8", "#E5E0D8", 12);
        Place(SecondaryNativeLayer, ownerDecision, 1110, 480, 342, 292);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#EAB12F"), IsHitTestVisible = false },
            1128,
            492,
            24,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("♕", 12, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1134,
            494,
            13,
            16);
        Place(
            SecondaryNativeLayer,
            ChromeText("قرار المالك", 15.5, "#283347", FontWeights.SemiBold),
            1160,
            487,
            120,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("اختر المسار المناسب للدمج في main", 10, "#677181"),
            1134,
            526,
            250,
            22);

        AddOwnerBranchChoice(1130, 552, "A", "Branch A", "feature/memory-new-allocator", true, "#F1A62B");
        AddOwnerBranchChoice(1130, 616, "B", "Branch B", "feature/memory-garbage-collector", false, "#2F75F3");
        AddOwnerBranchChoice(1130, 680, "⌘", "إنشاء فرع جديد من هذه النقطة", "للاستكشاف أو النهج الإضافي", false, "#657083");

        var confirm = ChromePanel("#EAA51F", "#EAA51F", 8);
        Place(SecondaryNativeLayer, confirm, 1130, 738, 300, 30);
        Place(
            SecondaryNativeLayer,
            ChromeText("♕  تأكيد القرار والبدء في الدمج", 10.5, "#FFFFFF", FontWeights.SemiBold),
            1190,
            742,
            190,
            22);
    }

    private void AddCodePane(double left, double top, double width, double height, bool after)
    {
        var pane = ChromePanel(after ? "#F0FBF5" : "#FFF2F3", after ? "#D0EEDD" : "#F0D5D8", 7);
        Place(SecondaryNativeLayer, pane, left, top, width, height);
        Place(
            SecondaryNativeLayer,
            ChromeText(after ? "+ بعد   (feature/memory-new-allocator)" : "− قبل   (main)", 9.5, after ? "#23975C" : "#C94855", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 10,
            top + 8,
            width - 20,
            20);

        var codeLines = after
            ? new[]
            {
                "142   + void* allocate(size_t size) {",
                "143   +   if (size == 0) return nullptr;",
                "144   +   void* ptr = aligned_alloc(64,size);",
                "145   +   if (!ptr) {",
                "146   +     UC_METRIC(\"alloc_failed\", size);",
                "147   +     return fallback_allocate(size);",
                "148   +   }",
                "149   +   return ptr;"
            }
            : new[]
            {
                "142   - void* allocate(size_t size) {",
                "143   -   if (size == 0) return nullptr;",
                "144   -   void* ptr = malloc(size);",
                "145   -   if (!ptr) {",
                "146   -     LOG_ERROR(\"Allocation failed\");",
                "147   -     return nullptr;",
                "148   -   }",
                "149   -   return ptr;"
            };

        for (var i = 0; i < codeLines.Length; i++)
        {
            Place(
                SecondaryNativeLayer,
                ChromeText(codeLines[i], 8.2, after ? "#24764D" : "#A44A52", null, FlowDirection.LeftToRight),
                left + 10,
                top + 34 + (i * 19),
                width - 20,
                18);
        }
    }

    private void AddBranchScorecard(
        double left,
        string branchLetter,
        string branchName,
        string accent,
        bool recommended)
    {
        var card = ChromePanel("#FFFCFBF8", recommended ? "#A9E6C8" : "#BDDDF7", 10);
        Place(SecondaryNativeLayer, card, left, 480, 240, 292);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
            left + 14,
            494,
            29,
            29);
        Place(
            SecondaryNativeLayer,
            ChromeText(branchLetter, 15, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 23,
            498,
            14,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText($"Branch {branchLetter}", 13, "#2D394B", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 50,
            491,
            95,
            23);
        Place(
            SecondaryNativeLayer,
            ChromeText(branchName, 8.4, "#647083", null, FlowDirection.LeftToRight),
            left + 50,
            516,
            178,
            20);

        AddBranchMetric(left, 548, "البناء", recommended ? "نجح  2m 14s" : "نجح  3m 02s", "#25C86A");
        AddBranchMetric(left, 582, "الاختبارات", recommended ? "148/148 نجح" : "12/148 فشل", recommended ? "#25C86A" : "#E95362");
        AddBranchMetric(left, 616, "CodeQL", recommended ? "لم يتم العثور على مشكلات" : "2 تحذيرات", recommended ? "#25C86A" : "#EAA228");
        AddBranchMetric(left, 650, "الأداء", recommended ? "تحسن +32%" : "تحسن +18%", "#25C86A");
        AddBranchMetric(left, 684, "استخدام الذاكرة", recommended ? "انخفاض -18%" : "انخفاض -35%", "#25C86A");

        var open = ChromePanel("#FFFFFF", "#CAD7E9", 7);
        Place(SecondaryNativeLayer, open, left + 14, 727, 170, 31);
        Place(
            SecondaryNativeLayer,
            ChromeText("فتح في محرر الكود  ⌘", 9, "#3A6AAE", FontWeights.SemiBold),
            left + 30,
            732,
            140,
            20);
    }

    private void AddBranchMetric(
        double left,
        double top,
        string label,
        string value,
        string accent)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText("◉", 10, accent, FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 17,
            top + 2,
            15,
            15);
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 9, "#667181"),
            left + 39,
            top,
            71,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 8.8, accent, FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 111,
            top,
            116,
            19);
    }

    private void AddOwnerBranchChoice(
        double left,
        double top,
        string glyph,
        string title,
        string subtitle,
        bool selected,
        string accent)
    {
        var card = ChromePanel(selected ? "#FFF6E5" : "#FFFFFF", selected ? "#F0B544" : "#E5E1DB", 8);
        Place(SecondaryNativeLayer, card, left, top, 300, 55);
        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush(selected ? accent : "#F4F5F7"),
                Stroke = Brush(accent),
                StrokeThickness = 1.5,
                IsHitTestVisible = false,
            },
            left + 10,
            top + 12,
            30,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 13, selected ? "#FFFFFF" : accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 19,
            top + 16,
            14,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 10.5, "#303B4C", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 50,
            top + 8,
            215,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText(subtitle, 8.2, "#6F7987", null, FlowDirection.LeftToRight),
            left + 50,
            top + 29,
            226,
            17);
    }

    private void BuildNativeAutopilotHistory()
    {
        var history = ChromePanel("#FFFCFBF8", "#E5E0D8", 12);
        Place(SecondaryNativeLayer, history, 16, 784, 1436, 151);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            34,
            796,
            23,
            23);
        Place(
            SecondaryNativeLayer,
            ChromeText("▶", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            40,
            799,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("تاريخ المشروع", 15.5, "#283347", FontWeights.SemiBold),
            66,
            791,
            130,
            30);

        AddHistoryFrame(40, "a3f9c1 · 14:02", "إضافة سجل تشخيص", "#25C86A", false);
        AddHistoryFrame(236, "d72e9b · 15:18", "تحسين تجميع الكاش", "#25C86A", false);
        AddHistoryFrame(432, "f4c2d0 · 16:32", "بداية تجربة التحسينات", "#8457E6", true);
        AddHistoryFrame(628, "e1a7b3 · 17:10", "فشل 12 اختبار", "#E95362", false);
        AddHistoryFrame(824, "8d5e4f · 18:05", "إصلاح الاختبارات", "#25C86A", false);
        AddHistoryFrame(1020, "9c8d2a · 19:22", "لا مشاكل CodeQL", "#25C86A", false);
        AddHistoryFrame(1216, "1b7a9c · 20:11", "VERIFIED · جاهز للدمج", "#25C86A", false);
    }

    private void AddHistoryFrame(
        double left,
        string title,
        string subtitle,
        string accent,
        bool current)
    {
        var card = ChromePanel(current ? "#F8F3FF" : "#FFFFFF", current ? "#9E75EC" : "#E3E0DB", 7);
        Place(SecondaryNativeLayer, card, left, 826, 180, 94);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
            left + 8,
            834,
            10,
            10);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 8.5, current ? "#714AD1" : "#667181", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 24,
            830,
            145,
            18);

        var preview = ChromePanel("#1E2430", "#2D3542", 4);
        Place(SecondaryNativeLayer, preview, left + 10, 850, 160, 39);
        for (var i = 0; i < 3; i++)
        {
            Place(
                SecondaryNativeLayer,
                ChromePanel(i == 1 ? accent : "#3E4858", i == 1 ? accent : "#3E4858", 1),
                left + 19,
                858 + (i * 8),
                105 - (i * 17),
                3);
        }

        Place(
            SecondaryNativeLayer,
            ChromeText(subtitle, 8.3, current ? "#714AD1" : "#5E6978", current ? FontWeights.SemiBold : FontWeights.Normal),
            left + 12,
            894,
            155,
            19);
    }

    private void BuildNativeStudioProject()
    {
        BuildNativeStudioHeaderAndPipeline();
        BuildNativeStudioPlayerAndContext();
        BuildNativeStudioTimeline();
        BuildNativeStudioLowerWorkflow();
    }

    private void BuildNativeOwnerDecision()
    {
        // Decision mode preserves a native reconstruction of the originating
        // project beneath the governed decision surface. The underlay is
        // de-emphasized by the translucent veil below; it never falls back to
        // reference pixels in native-only evidence.
        BuildNativeProjectWorkspaceCore();

        Place(
            SecondaryNativeLayer,
            ChromePanel("#B8EDF2F8", "#00FFFFFF", 0, new Thickness(0)),
            0,
            49,
            1470,
            914);

        BuildNativeDecisionHeader();
        BuildNativeDecisionSurface();
        BuildNativeDecisionRolesAndRouting();
        BuildNativeDecisionEvidencePeek();
        BuildNativeDecisionActions();
    }

    private void BuildNativeDecisionHeader()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#EAF1F5F9", "#00FFFFFF", 0, new Thickness(0)),
            596,
            52,
            388,
            96);

        var titlePill = ChromePanel("#FFFDFBFA", "#D7DDE8", 24);
        Place(SecondaryNativeLayer, titlePill, 657, 62, 252, 52);
        Place(
            SecondaryNativeLayer,
            ChromeText("وضع قرار المجلس", 23, "#16203A", FontWeights.Bold),
            697,
            68,
            172,
            34);
        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#2F75F3"),
                Stroke = Brush("#92B9FA"),
                StrokeThickness = 1.2,
                IsHitTestVisible = false,
            },
            864,
            74,
            28,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("◎", 17, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            871,
            75,
            18,
            22);

        var subtitle = ChromeText(
            "تحليل شامل · نقاش متعدد الزوايا · توصية موحدة",
            12.5,
            "#5C6676",
            FontWeights.SemiBold);
        subtitle.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, subtitle, 620, 117, 330, 24);
    }

    private void BuildNativeDecisionSurface()
    {
        var surface = ChromePanel("#FFFCFBFA", "#C8D5E8", 16);
        surface.Effect = new DropShadowEffect
        {
            BlurRadius = 26,
            ShadowDepth = 3,
            Opacity = 0.16,
            Color = Color.FromRgb(53, 72, 105),
        };
        Place(SecondaryNativeLayer, surface, 400, 155, 735, 785);

        var badge = ChromePanel("#FFF0F2", "#F5CCD3", 8);
        Place(SecondaryNativeLayer, badge, 429, 174, 95, 29);
        Place(
            SecondaryNativeLayer,
            ChromeText("قرار مطلوب", 10.5, "#D84259", FontWeights.SemiBold),
            443,
            178,
            68,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("#UC-2025-041", 9.5, "#737D8C", FontWeights.SemiBold, FlowDirection.LeftToRight),
            541,
            178,
            93,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("26 مايو 2025", 9.5, "#87909C"),
            653,
            178,
            92,
            20);

        Place(
            SecondaryNativeLayer,
            ChromePanel("#EFF6FF", "#CFE2FC", 11),
            1056,
            191,
            57,
            57);
        Place(
            SecondaryNativeLayer,
            ChromeText("◇", 31, "#1674E8", FontWeights.Bold, FlowDirection.LeftToRight),
            1070,
            200,
            31,
            38);

        var question = ChromeText(
            "هل نعتمد إطلاق المشروع؟",
            31,
            "#101A34",
            FontWeights.Bold);
        question.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, question, 661, 196, 376, 47);

        var productBadge = ChromePanel("#EAFBF0", "#BFEBCF", 8);
        Place(SecondaryNativeLayer, productBadge, 1003, 262, 70, 26);
        Place(
            SecondaryNativeLayer,
            ChromeText("منتج", 9.5, "#17994E", FontWeights.SemiBold),
            1019,
            265,
            38,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("Smart Secretary V2", 12.5, "#4F5B6D", FontWeights.SemiBold, FlowDirection.LeftToRight),
            842,
            262,
            154,
            24);

        var summary = ChromeText(
            "اكتملت متطلبات التطوير الأساسية، واجتازت النسخة التجريبية الاختبارات الداخلية بنجاح.\nنحتاج قرار المجلس للمضي في الإطلاق العام.",
            13,
            "#626C7A",
            FontWeights.SemiBold);
        summary.TextAlignment = TextAlignment.Right;
        summary.TextWrapping = TextWrapping.Wrap;
        summary.LineHeight = 23;
        Place(SecondaryNativeLayer, summary, 506, 300, 590, 55);

        AddDecisionInfoPanel(
            414,
            366,
            349,
            205,
            "#F2F8FF",
            "#C9DFF8",
            "#226ED8",
            "✦",
            "لماذا وصل المشروع إلى هذه المرحلة؟",
            new[]
            {
                "اكتملت جميع متطلبات المنتج الأساسية",
                "نجحت النسخة التجريبية في الاختبارات الداخلية",
                "تم معالجة 92% من الملاحظات الحرجة",
                "جاهزية البنية التحتية وقابلية التوسع",
                "توافق مع المعايير القانونية والأمنية",
            });

        AddDecisionRecommendationPanel();

        AddDecisionDissentPanel();

        AddDecisionEvidenceSummaryPanel();

        AddDecisionImpactPanel(
            414,
            773,
            349,
            156,
            "#F1FBF4",
            "#C8ECD2",
            "#14994E",
            "✓",
            "أثر الموافقة",
            new[]
            {
                "إطلاق المنتج في السوق خلال 2 أسبوع",
                "تحقيق ميزة تنافسية مبكرة",
                "توقع نمو الإيرادات بنسبة 25% في الربع الأول",
                "تعزيز ثقة العملاء والمستثمرين",
            });

        AddDecisionImpactPanel(
            774,
            773,
            349,
            156,
            "#FFF3F4",
            "#F0D0D4",
            "#E03B4E",
            "×",
            "أثر الرفض",
            new[]
            {
                "تأخير الوصول إلى السوق",
                "خسارة فرصة تنافسية لصالح المنافسين",
                "ارتفاع التكاليف التشغيلية الإضافية",
                "احتمال تراجع ثقة الفريق وأصحاب المصلحة",
            });
    }

    private void AddDecisionInfoPanel(
        double left,
        double top,
        double width,
        double height,
        string background,
        string border,
        string accent,
        string glyph,
        string title,
        IReadOnlyList<string> items)
    {
        var panel = ChromePanel(background, border, 11);
        Place(SecondaryNativeLayer, panel, left, top, width, height);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 20, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 17,
            top + 13,
            27,
            27);
        var titleText = ChromeText(title, 15, "#253149", FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, titleText, left + 56, top + 11, width - 73, 29);

        for (var index = 0; index < items.Count; index++)
        {
            var y = top + 51 + index * 27;
            Place(
                SecondaryNativeLayer,
                new Ellipse
                {
                    Fill = Brush("#22B761"),
                    IsHitTestVisible = false,
                },
                left + width - 34,
                y + 4,
                14,
                14);
            Place(
                SecondaryNativeLayer,
                ChromeText("✓", 8, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
                left + width - 31,
                y + 2,
                10,
                14);
            var itemText = ChromeText(items[index], 10.5, "#566171", FontWeights.SemiBold);
            itemText.TextAlignment = TextAlignment.Right;
            Place(SecondaryNativeLayer, itemText, left + 20, y, width - 61, 21);
        }
    }

    private void AddDecisionRecommendationPanel()
    {
        var panel = ChromePanel("#F1FBF4", "#BFE9CB", 11);
        Place(SecondaryNativeLayer, panel, 774, 366, 349, 205);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#24BB61"), IsHitTestVisible = false },
            790,
            381,
            30,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 16, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            798,
            383,
            18,
            22);
        var heading = ChromeText("توصية المجلس", 16, "#17683B", FontWeights.Bold);
        heading.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, heading, 855, 356, 245, 31);

        var recommendationBadge = ChromePanel("#E5F7EB", "#BDE8C9", 8);
        Place(SecondaryNativeLayer, recommendationBadge, 1033, 424, 69, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText("التوصية", 9, "#15934A", FontWeights.SemiBold),
            1047,
            427,
            42,
            18);

        var recommendation = ChromeText(
            "المضي في الإطلاق مع تحسينات محددة",
            15.5,
            "#1E4732",
            FontWeights.Bold);
        recommendation.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, recommendation, 802, 442, 286, 31);

        var details = ChromeText(
            "يؤيد أغلب أعضاء المجلس إطلاق المشروع نظراً لقيمته العالية\nوجاهزيته، مع تنفيذ التوصيات المدرجة.",
            10.8,
            "#577063",
            FontWeights.SemiBold);
        details.TextAlignment = TextAlignment.Right;
        details.TextWrapping = TextWrapping.Wrap;
        details.LineHeight = 18;
        Place(SecondaryNativeLayer, details, 803, 479, 286, 47);
    }

    private void AddDecisionDissentPanel()
    {
        var panel = ChromePanel("#FFF1F2", "#F2CDD2", 11);
        Place(SecondaryNativeLayer, panel, 414, 584, 349, 177);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#F1475A"), IsHitTestVisible = false },
            431,
            598,
            30,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("!", 17, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            443,
            600,
            10,
            22);
        var heading = ChromeText("أقوى اعتراض", 15.5, "#B72E41", FontWeights.Bold);
        heading.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, heading, 533, 560, 205, 28);

        var teamBadge = ChromePanel("#F8DDE1", "#F0C6CC", 8);
        Place(SecondaryNativeLayer, teamBadge, 594, 635, 144, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText("الفريق المعارض", 9, "#C0394D", FontWeights.SemiBold),
            610,
            638,
            110,
            18);

        var text = ChromeText(
            "مخاطر الخصوصية المرتبطة بمعالجة البيانات الحساسة\nتحتاج إلى مزيد من الضمانات قبل الإطلاق العام.",
            11,
            "#6B4B52",
            FontWeights.SemiBold);
        text.TextAlignment = TextAlignment.Right;
        text.TextWrapping = TextWrapping.Wrap;
        text.LineHeight = 20;
        Place(SecondaryNativeLayer, text, 445, 673, 288, 54);
    }

    private void AddDecisionEvidenceSummaryPanel()
    {
        var panel = ChromePanel("#F7F8FC", "#DEE2EB", 11);
        Place(SecondaryNativeLayer, panel, 774, 584, 349, 177);
        Place(
            SecondaryNativeLayer,
            ChromeText("▤", 22, "#6253DA", FontWeights.SemiBold, FlowDirection.LeftToRight),
            792,
            595,
            30,
            30);
        var heading = ChromeText("ملخص الأدلة", 15.5, "#283348", FontWeights.Bold);
        heading.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, heading, 940, 558, 160, 28);

        var evidenceCount = ChromePanel("#F1EEFF", "#DAD2F6", 8);
        Place(SecondaryNativeLayer, evidenceCount, 792, 633, 76, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText("12 دليلاً", 9.2, "#6250BC", FontWeights.SemiBold),
            809,
            636,
            44,
            18);

        AddDecisionEvidenceRow(793, 665, "نتائج الاختبارات الداخلية والأداء", "3 ملفات", "▣");
        AddDecisionEvidenceRow(793, 696, "مراجعة الامتثال القانوني والخصوصية", "4 ملفات", "♢");
        AddDecisionEvidenceRow(793, 727, "تحليل السوق وتعليقات المستخدمين", "5 ملفات", "▥");
    }

    private void AddDecisionEvidenceRow(
        double left,
        double top,
        string title,
        string count,
        string glyph)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 12, "#5869C8", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left,
            top,
            20,
            20);
        var titleText = ChromeText(title, 9.6, "#556071", FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, titleText, left + 27, top, 220, 20);
        Place(
            SecondaryNativeLayer,
            ChromeText(count, 8.8, "#7B8491"),
            left + 261,
            top,
            54,
            20);
    }

    private void AddDecisionImpactPanel(
        double left,
        double top,
        double width,
        double height,
        string background,
        string border,
        string accent,
        string glyph,
        string title,
        IReadOnlyList<string> items)
    {
        var panel = ChromePanel(background, border, 11);
        Place(SecondaryNativeLayer, panel, left, top, width, height);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
            left + 17,
            top + 14,
            30,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 16, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 25,
            top + 16,
            18,
            22);
        var titleText = ChromeText(title, 14, accent, FontWeights.Bold);
        titleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, titleText, left + 70, top + 13, width - 91, 26);

        for (var index = 0; index < items.Count; index++)
        {
            var y = top + 48 + index * 20;
            Place(
                SecondaryNativeLayer,
                new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
                left + width - 28,
                y + 5,
                6,
                6);
            var itemText = ChromeText(items[index], 9.5, "#596474");
            itemText.TextAlignment = TextAlignment.Right;
            Place(SecondaryNativeLayer, itemText, left + 18, y, width - 52, 19);
        }
    }

    private void BuildNativeDecisionRolesAndRouting()
    {
        AddDecisionRoutingPath("M 300,226 C 340,204 366,204 400,223", "#744DE7", false);
        AddDecisionRoutingPath("M 264,452 C 325,431 350,465 400,494", "#EF3E55", true);
        AddDecisionRoutingPath("M 1135,223 C 1172,202 1200,202 1232,223", "#28C878", false);
        AddDecisionRoutingPath("M 1135,456 C 1183,431 1211,436 1260,461", "#2986E9", false);
        AddDecisionRoutingPath("M 1135,645 C 1182,620 1208,621 1248,645", "#E6B530", false);

        AddDecisionRole(205, 177, 96, "#F3EEFF", "#6F4BE1", "▣", "الأدلة", "يحلل الأدلة الحالية...", "evidence");
        AddDecisionRole(146, 388, 112, "#FFF0F2", "#EE4057", "♦", "الفريق المعارض", "يحدد المخاطر والثغرات...", "redteam");
        AddDecisionRole(1222, 163, 106, "#EDFFF5", "#28C878", "✦", "المركزي", "يلخص ويحسن القرار...", "synthesis");
        AddDecisionRole(1269, 391, 106, "#EEF6FF", "#2B83E8", "●", "تجربة المستخدم", "يقيم الأثر على المستخدمين...", "ux");
        AddDecisionRole(1252, 582, 110, "#FFF9E7", "#DFB228", "▣", "الأمن والخصوصية", "يقيم المخاطر والالتزام...", "security");

        var dissent = ChromePanel("#FFE1E5", "#F3B9C1", 10);
        Place(SecondaryNativeLayer, dissent, 302, 467, 121, 35);
        Place(
            SecondaryNativeLayer,
            ChromeText("مسار الاعتراض", 10.5, "#BD3548", FontWeights.SemiBold),
            322,
            473,
            82,
            22);
    }

    private void AddDecisionRoutingPath(
        string data,
        string color,
        bool dissent)
    {
        var path = new Path
        {
            Data = Geometry.Parse(data),
            Stroke = Brush(color),
            StrokeThickness = dissent ? 3 : 2.1,
            StrokeDashArray = new DoubleCollection { 1, dissent ? 3 : 5 },
            Opacity = dissent ? 0.9 : 0.72,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(path);
    }

    private void AddDecisionRole(
        double left,
        double top,
        double size,
        string background,
        string accent,
        string glyph,
        string title,
        string subtitle,
        string roleId)
    {
        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#30FFFFFF"),
                Stroke = Brush("#65FFFFFF"),
                StrokeThickness = 1,
                IsHitTestVisible = false,
            },
            left - 22,
            top - 22,
            size + 44,
            size + 44);

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush(background),
                Stroke = Brush(accent),
                StrokeThickness = 2.3,
                IsHitTestVisible = false,
            },
            left,
            top,
            size,
            size);
        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#00FFFFFF"),
                Stroke = Brush(accent),
                StrokeThickness = 1,
                Opacity = 0.35,
                IsHitTestVisible = false,
            },
            left - 11,
            top - 11,
            size + 22,
            size + 22);

        Place(
            SecondaryNativeLayer,
            ChromePanel("#E8F2F5F9", "#00FFFFFF", 8, new Thickness(0)),
            left - 48,
            top + size + 4,
            size + 96,
            60);

        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, size * 0.34, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + size * 0.31,
            top + size * 0.25,
            size * 0.45,
            size * 0.45);
        var titleText = ChromeText(title, 13.5, "#1E293B", FontWeights.Bold);
        titleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, titleText, left - 40, top + size + 9, size + 80, 25);
        var subtitleText = ChromeText(subtitle, 9.3, "#667181", FontWeights.SemiBold);
        subtitleText.TextAlignment = TextAlignment.Center;
        subtitleText.TextTrimming = TextTrimming.CharacterEllipsis;
        Place(SecondaryNativeLayer, subtitleText, left - 50, top + size + 34, size + 100, 24);

        var stateDot = new Ellipse
        {
            Fill = Brush(accent),
            IsHitTestVisible = false,
        };
        Place(SecondaryNativeLayer, stateDot, left + size - 2, top + size * 0.46, 9, 9);
    }

    private void BuildNativeDecisionEvidencePeek()
    {
        var group = new Canvas
        {
            Width = 325,
            Height = 322,
            FlowDirection = FlowDirection.LeftToRight,
        };

        var card = ChromePanel("#FFFDFCFB", "#D8DEE8", 13);
        card.Effect = new DropShadowEffect
        {
            BlurRadius = 16,
            ShadowDepth = 2,
            Opacity = 0.13,
            Color = Color.FromRgb(69, 79, 98),
        };
        Place(group, card, 0, 0, 325, 322);

        Place(group, ChromeText("×", 22, "#526071", FontWeights.Normal, FlowDirection.LeftToRight), 18, 15, 27, 28);
        Place(group, ChromeText("معاينة دليل", 17, "#1E293B", FontWeights.Bold), 108, 14, 120, 29);
        var counter = ChromePanel("#F4F5F7", "#E1E3E7", 7);
        Place(group, counter, 273, 17, 38, 25);
        Place(group, ChromeText("3/12", 9, "#606A78", FontWeights.SemiBold, FlowDirection.LeftToRight), 280, 21, 26, 17);

        var pdf = ChromePanel("#FFF0F1", "#F0D8DB", 7);
        Place(group, pdf, 26, 63, 43, 52);
        Place(group, ChromeText("PDF", 11, "#E13D52", FontWeights.Bold, FlowDirection.LeftToRight), 33, 77, 29, 23);

        var evidenceTitle = ChromeText("تقرير التدقيق الأمني والخصوصية", 11.5, "#263246", FontWeights.Bold);
        evidenceTitle.TextAlignment = TextAlignment.Right;
        Place(group, evidenceTitle, 81, 62, 195, 24);
        Place(group, ChromeText("20 مايو 2025  ·  1.4 MB", 9, "#7A8390"), 130, 91, 146, 20);

        var verified = ChromePanel("#E7F9ED", "#BCEAC9", 8);
        Place(group, verified, 29, 128, 85, 25);
        Place(group, ChromeText("● VERIFIED", 8.5, "#15944B", FontWeights.Bold, FlowDirection.LeftToRight), 39, 131, 66, 18);
        Place(group, ChromeText("↗   ⛓", 17, "#647083", null, FlowDirection.LeftToRight), 243, 126, 55, 25);

        var body = ChromeText(
            "يؤكد التقرير أن النظام يتوافق مع معايير حماية\nالبيانات، مع توصيات إضافية لتشفير البيانات\nالحساسة في بيئات الإنتاج.",
            10.2,
            "#566171",
            FontWeights.SemiBold);
        body.TextAlignment = TextAlignment.Right;
        body.TextWrapping = TextWrapping.Wrap;
        body.LineHeight = 19;
        Place(group, body, 25, 169, 276, 70);

        var full = ChromePanel("#FFFFFF", "#E2E4E8", 8);
        Place(group, full, 25, 250, 275, 40);
        Place(group, ChromeText("عرض الدليل الكامل  ←", 10, "#344055", FontWeights.SemiBold), 97, 259, 168, 21);

        Place(SecondaryNativeLayer, group, 32, 610, 325, 322);
    }

    private void BuildNativeDecisionActions()
    {
        var dock = ChromePanel("#FFFCFBFA", "#D7DCE6", 17);
        dock.Effect = new DropShadowEffect
        {
            BlurRadius = 18,
            ShadowDepth = 2,
            Opacity = 0.14,
            Color = Color.FromRgb(58, 71, 95),
        };
        Place(SecondaryNativeLayer, dock, 381, 941, 796, 70);

        AddDecisionActionVisual(397, 955, 137, "#F7F9FF", "#8AAAE9", "#244D9C", "▤", "فحص الأدلة");
        AddDecisionActionVisual(545, 955, 137, "#FFFFFF", "#D9DCE3", "#3D4758", "?", "طرح سؤال");
        AddDecisionActionVisual(694, 955, 137, "#FFF0F2", "#EEA6B0", "#DB334B", "×", "رفض");
        AddDecisionActionVisual(843, 955, 166, "#FFF9E8", "#F0CC78", "#B97D13", "⚙", "طلب تعديلات");
        AddDecisionActionVisual(1020, 955, 139, "#2475F3", "#2475F3", "#FFFFFF", "✓", "الموافقة");
    }

    private void AddDecisionActionVisual(
        double left,
        double top,
        double width,
        string background,
        string border,
        string foreground,
        string glyph,
        string label)
    {
        var panel = ChromePanel(background, border, 9);
        Place(SecondaryNativeLayer, panel, left, top, width, 44);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 16, foreground, FontWeights.Bold, FlowDirection.LeftToRight),
            left + width - 34,
            top + 8,
            21,
            27);
        var text = ChromeText(label, 12, foreground, FontWeights.SemiBold);
        text.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, text, left + 12, top + 7, width - 50, 28);
    }

    private void BuildNativeRecoveryFork()
    {
        BuildNativeRecoveryHeader();
        BuildNativeRecoveryTimeline();
        BuildNativeRecoveryCards();
        BuildNativeRecoveryBottomPanels();
    }

    private void BuildNativeRecoveryHeader()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFDFBF8", "#EEE9E2", 0, new Thickness(0)),
            230,
            49,
            1240,
            104);

        Place(
            SecondaryNativeLayer,
            ChromeText("⌂   المشاريع   /   Smart Secretary V2   /   استرجاع وفروع المشروع", 10.5, "#6D7888", FontWeights.SemiBold),
            244,
            59,
            430,
            24);

        Place(
            SecondaryNativeLayer,
            ChromeText("⑂", 36, "#2F8BEE", FontWeights.Bold, FlowDirection.LeftToRight),
            963,
            69,
            44,
            48);
        var title = ChromeText("استرجاع وفروع المشروع", 34, "#111B34", FontWeights.Bold);
        title.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, title, 626, 72, 345, 50);
        var subtitle = ChromeText(
            "ارجع إلى أي نقطة في التاريخ، أو أنشئ فرعاً جديداً، وقارن النتائج بذكاء",
            13,
            "#606B7B",
            FontWeights.SemiBold);
        subtitle.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, subtitle, 550, 121, 495, 25);

        var help = ChromePanel("#F7FAFF", "#DEE7F3", 12);
        Place(SecondaryNativeLayer, help, 1150, 58, 300, 81);
        Place(
            SecondaryNativeLayer,
            ChromeText("▣", 22, "#2A72DC", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1414,
            76,
            24,
            30);
        var helpTitle = ChromeText("حول نقاط الحفظ والفروع", 12.5, "#29364A", FontWeights.Bold);
        helpTitle.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, helpTitle, 1180, 69, 218, 25);
        var helpBody = ChromeText(
            "استكشف تطور المشروع، استرجع الإصدارات السابقة\nوأنشئ فروعاً جديدة لتجربة أفكار مختلفة.",
            9.5,
            "#737D8B",
            FontWeights.SemiBold);
        helpBody.TextAlignment = TextAlignment.Right;
        helpBody.LineHeight = 16;
        Place(SecondaryNativeLayer, helpBody, 1180, 94, 218, 39);
    }

    private void BuildNativeRecoveryTimeline()
    {
        var card = ChromePanel("#FFFCFBF8", "#E5E0D8", 13);
        Place(SecondaryNativeLayer, card, 230, 153, 1240, 345);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            242,
            164,
            28,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("♟", 13, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            250,
            168,
            15,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("المخطط الزمني للمشروع ونقاط الحفظ", 17, "#17233B", FontWeights.Bold),
            280,
            160,
            310,
            32);

        AddTagChipToCanvas(SecondaryNativeLayer, 1112, 162, 65, "▦", "#F7F8FA", "#5E6877");
        AddTagChipToCanvas(SecondaryNativeLayer, 1186, 162, 65, "▤", "#EEF5FF", "#2F75F3");
        AddTagChipToCanvas(SecondaryNativeLayer, 1260, 162, 65, "▧", "#F7F8FA", "#5E6877");
        AddTagChipToCanvas(SecondaryNativeLayer, 1333, 162, 65, "عرض", "#FFFFFF", "#566171");

        var create = ChromePanel("#2475F3", "#2475F3", 8);
        Place(SecondaryNativeLayer, create, 1300, 171, 145, 36);
        Place(
            SecondaryNativeLayer,
            ChromeText("+  إنشاء نقطة حفظ جديدة", 9.5, "#FFFFFF", FontWeights.SemiBold),
            1311,
            177,
            123,
            23);

        var line = new Line
        {
            X1 = 300,
            Y1 = 261,
            X2 = 1395,
            Y2 = 261,
            Stroke = Brush("#D7DDE5"),
            StrokeThickness = 2.2,
            StrokeDashArray = new DoubleCollection { 1, 4 },
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(line);

        AddRecoveryCheckpointNode(292, 238, "#2F75F3", "▶", "البداية", "1 يناير 2025", "المشروع منشأ", false);
        AddRecoveryCheckpointNode(458, 238, "#2DC86B", "✓", "نقطة حفظ #1", "10 يناير 2025", "معمارية أساس", false);
        AddRecoveryCheckpointNode(632, 238, "#8B63E7", "◇", "نقطة حفظ #2", "22 يناير 2025", "تكامل البيانات", false);
        AddRecoveryCheckpointNode(809, 229, "#2475F3", "⌃", "نقطة حفظ #3", "5 فبراير 2025", "تحسين الأمان", true);
        AddRecoveryCheckpointNode(990, 238, "#29B8CC", "✓", "نقطة حفظ #4", "20 فبراير 2025", "توسيع المزايا", false);
        AddRecoveryCheckpointNode(1171, 238, "#8A58E5", "↗", "نقطة حفظ #5", "10 مارس 2025", "تحسين الأداء", false);
        AddRecoveryCheckpointNode(1382, 238, "#2F75F3", "⚑", "الإصدار الحالي", "25 مارس 2025", "v2.1.0", false);

        var selected = ChromePanel("#F2F7FF", "#8AB8F9", 7);
        Place(SecondaryNativeLayer, selected, 786, 194, 108, 28);
        Place(
            SecondaryNativeLayer,
            ChromeText("النقطة المحددة", 9.5, "#2768C9", FontWeights.SemiBold),
            804,
            198,
            73,
            19);

        var selectedInfo = ChromePanel("#FFFDFBF8", "#D9E1EC", 8);
        Place(SecondaryNativeLayer, selectedInfo, 697, 344, 132, 61);
        Place(
            SecondaryNativeLayer,
            ChromeText("5 فبراير 2025", 9.3, "#566171", FontWeights.SemiBold),
            716,
            351,
            93,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("تحسين الأمان", 10.3, "#263247", FontWeights.Bold),
            716,
            375,
            93,
            21);

        AddRecoveryBranchPath(
            "M 822,285 C 820,335 877,356 943,365 L 1288,365",
            "#25C86A");
        AddRecoveryBranchPath(
            "M 822,285 C 820,370 877,414 943,423 L 1288,423",
            "#875BE4");

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#25C86A"), IsHitTestVisible = false },
            1013,
            351,
            31,
            31);
        Place(
            SecondaryNativeLayer,
            ChromeText("◉", 15, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1022,
            355,
            16,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("الفرع A", 13, "#1C6840", FontWeights.Bold),
            1058,
            344,
            80,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("التركيز على الخصوصية", 9.2, "#667181"),
            1058,
            367,
            115,
            19);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#875BE4"), IsHitTestVisible = false },
            1013,
            409,
            31,
            31);
        Place(
            SecondaryNativeLayer,
            ChromeText("◆", 15, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1022,
            413,
            16,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("الفرع B", 13, "#5F3EB5", FontWeights.Bold),
            1058,
            402,
            80,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("ميزات الذكاء المتقدم", 9.2, "#667181"),
            1058,
            425,
            125,
            19);

        AddRecoveryBranchEnd(1296, 343, "#EAFBF0", "#25C86A", "الإصدار A-1", "تم الإنشاء من #3", "12 فبراير 2025", "✓");
        AddRecoveryBranchEnd(1296, 402, "#F3EEFF", "#875BE4", "الإصدار B-1", "تم الإنشاء من #3", "15 فبراير 2025", "⚗");

        var restoreLabel = ChromePanel("#F5F8FF", "#CADAF2", 8);
        Place(SecondaryNativeLayer, restoreLabel, 568, 344, 120, 36);
        Place(
            SecondaryNativeLayer,
            ChromeText("↶  استرجاع إلى هذه النقطة", 9.2, "#3170C8", FontWeights.SemiBold),
            579,
            350,
            99,
            22);
    }

    private void AddRecoveryCheckpointNode(
        double left,
        double top,
        string accent,
        string glyph,
        string title,
        string date,
        string subtitle,
        bool selected)
    {
        if (selected)
        {
            Place(
                SecondaryNativeLayer,
                new Ellipse
                {
                    Fill = Brush("#EAF4FF"),
                    Stroke = Brush("#8ABAFB"),
                    StrokeThickness = 1.3,
                    IsHitTestVisible = false,
                },
                left - 13,
                top - 13,
                70,
                70);
        }

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#FAFBFC"),
                Stroke = Brush(accent),
                StrokeThickness = selected ? 3 : 2,
                IsHitTestVisible = false,
            },
            left,
            top,
            44,
            44);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 19, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 12,
            top + 8,
            22,
            25);

        var titleText = ChromeText(title, 10.5, selected ? "#2467CA" : "#354052", selected ? FontWeights.Bold : FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, titleText, left - 32, top + 51, 108, 21);
        var dateText = ChromeText(date, 9, selected ? "#2C70D1" : "#727B87", selected ? FontWeights.SemiBold : FontWeights.Normal);
        dateText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, dateText, left - 30, top + 73, 104, 19);
        var subText = ChromeText(subtitle, 8.8, "#7A8390");
        subText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, subText, left - 36, top + 93, 116, 19);
    }

    private void AddRecoveryBranchPath(string data, string color)
    {
        var path = new Path
        {
            Data = Geometry.Parse(data),
            Stroke = Brush(color),
            StrokeThickness = 2,
            StrokeDashArray = new DoubleCollection { 2, 4 },
            Opacity = 0.9,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(path);
    }

    private void AddRecoveryBranchEnd(
        double left,
        double top,
        string background,
        string accent,
        string title,
        string subtitle,
        string date,
        string glyph)
    {
        var card = ChromePanel(background, accent, 8);
        Place(SecondaryNativeLayer, card, left, top, 146, 50);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 18, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 117,
            top + 12,
            20,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 10.2, "#314055", FontWeights.Bold),
            left + 14,
            top + 5,
            87,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText(subtitle, 8.2, "#657083"),
            left + 14,
            top + 20,
            93,
            16);
        Place(
            SecondaryNativeLayer,
            ChromeText(date, 7.8, "#7D8591"),
            left + 14,
            top + 34,
            95,
            14);
    }

    private void BuildNativeRecoveryCards()
    {
        var firstChild = SecondaryNativeLayer.Children.Count;

        BuildNativeSelectedCheckpointCard();
        BuildNativeRecoveryBranchCard(
            350,
            "#EFFAF3",
            "#25B960",
            "الفرع A — التركيز على الخصوصية",
            "VERIFIED",
            "#E5F8EB",
            "#178F49",
            "Claude 3.7 Sonnet",
            "عميق",
            "يعمل بنجاح",
            "تحسينات كبيرة في خصوصية البيانات مع الحفاظ على الأداء، وإضافة تشفير متقدم.",
            "06-checkpoint_recovery_fork.png",
            new Int32Rect(376, 678, 286, 75));
        BuildNativeRecoveryBranchCard(
            715,
            "#F7F2FF",
            "#8455DF",
            "الفرع B — ميزات الذكاء المتقدم",
            "PROPOSAL",
            "#FFF4DD",
            "#D68A17",
            "GPT-4.1",
            "إبداعي",
            "قيد المراجعة",
            "إضافة قدرات تحليل متقدمة وميزات تنبؤية جديدة باستخدام نماذج أكثر تقدماً.",
            "06-checkpoint_recovery_fork.png",
            new Int32Rect(745, 678, 289, 75));
        BuildNativeRecoveryComparison();

        TranslateSecondaryChildren(firstChild, 30);
    }

    private void BuildNativeSelectedCheckpointCard()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 16, 475, 324, 335);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            29,
            489,
            28,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("◇", 15, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            37,
            492,
            18,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("معلومات نقطة الحفظ المحددة", 15, "#263247", FontWeights.Bold),
            69,
            486,
            220,
            28);

        var content = ChromePanel("#FFFDFCFB", "#ECE7E0", 8);
        Place(SecondaryNativeLayer, content, 25, 527, 306, 250);
        Place(
            SecondaryNativeLayer,
            ChromePanel("#F1EEFF", "#D8CEF6", 8),
            37,
            539,
            42,
            42);
        Place(
            SecondaryNativeLayer,
            ChromeText("◇", 24, "#7D55E4", FontWeights.Bold, FlowDirection.LeftToRight),
            47,
            546,
            25,
            27);
        Place(
            SecondaryNativeLayer,
            ChromeText("نقطة حفظ #3", 12.5, "#263247", FontWeights.Bold),
            91,
            537,
            110,
            23);
        Place(
            SecondaryNativeLayer,
            ChromeText("تحسين الأمان", 10, "#657083", FontWeights.SemiBold),
            91,
            561,
            100,
            19);

        AddRecoveryInfoLine(594, "5 فبراير 2025 · 14:30", "▣");
        AddRecoveryInfoLine(621, "إضافة طبقة أمان محسنة وتحديث سياسات الوصول وتحسين سجل المراجعة.", "▧", true);

        AddTagChipToCanvas(SecondaryNativeLayer, 37, 666, 62, "الأمان", "#EFF6FF", "#3777C9");
        AddTagChipToCanvas(SecondaryNativeLayer, 106, 666, 62, "التحقق", "#F3EEFF", "#7354C7");
        AddTagChipToCanvas(SecondaryNativeLayer, 175, 666, 90, "البنية التحتية", "#F7F2FF", "#8B5BD0");

        Place(
            SecondaryNativeLayer,
            ChromeText("الموديل المستخدم", 8.6, "#7A8390"),
            37,
            704,
            88,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("Claude 3.5 Sonnet", 9.5, "#344052", FontWeights.SemiBold, FlowDirection.LeftToRight),
            37,
            724,
            120,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("مستوى التفكير", 8.6, "#7A8390"),
            182,
            704,
            78,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("متوازن", 9.5, "#7B56D1", FontWeights.SemiBold),
            182,
            724,
            70,
            20);

        var result = ChromePanel("#EAFBF0", "#C3EBCF", 8);
        Place(SecondaryNativeLayer, result, 37, 751, 122, 23);
        Place(
            SecondaryNativeLayer,
            ChromeText("♥  النتيجة  VERIFIED", 8.2, "#168F49", FontWeights.Bold),
            46,
            754,
            104,
            17);
    }

    private void AddRecoveryInfoLine(double top, string value, string glyph, bool wrap = false)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 11, "#657083", FontWeights.SemiBold, FlowDirection.LeftToRight),
            38,
            top,
            18,
            21);
        var text = ChromeText(value, 8.9, "#536071", FontWeights.SemiBold);
        text.TextWrapping = wrap ? TextWrapping.Wrap : TextWrapping.NoWrap;
        text.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, text, 62, top, 252, wrap ? 38 : 21);
    }

    private void BuildNativeRecoveryBranchCard(
        double left,
        string background,
        string accent,
        string title,
        string truthLabel,
        string truthBackground,
        string truthForeground,
        string model,
        string reasoning,
        string state,
        string summary,
        string imageName,
        Int32Rect sourceRect)
    {
        var card = ChromePanel(background, "#DFDDE1", 11);
        Place(SecondaryNativeLayer, card, left, 475, 355, 335);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
            left + 14,
            489,
            21,
            21);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 14.2, accent, FontWeights.Bold),
            left + 46,
            482,
            230,
            31);

        var truth = ChromePanel(truthBackground, truthForeground, 8);
        Place(SecondaryNativeLayer, truth, left + 250, 486, 78, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText(truthLabel, 8.4, truthForeground, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 261,
            490,
            56,
            17);
        Place(
            SecondaryNativeLayer,
            ChromeText("•••", 14, "#5C6676", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 330,
            488,
            19,
            20);

        Place(
            SecondaryNativeLayer,
            ChromeText("الموديل المستخدم", 8.5, "#7A8390"),
            left + 15,
            526,
            85,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText(model, 9.2, "#344052", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 15,
            545,
            112,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText("مستوى التفكير", 8.5, "#7A8390"),
            left + 139,
            526,
            82,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText(reasoning, 9.2, accent, FontWeights.SemiBold),
            left + 139,
            545,
            74,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText("حالة الفرع", 8.5, "#7A8390"),
            left + 236,
            526,
            70,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText(state, 9.2, state.Contains("نجاح", StringComparison.Ordinal) ? "#15934A" : "#C48118", FontWeights.SemiBold),
            left + 236,
            545,
            89,
            19);

        var summaryPanel = ChromePanel("#FFFDFCFB", "#E9E4DD", 8);
        Place(SecondaryNativeLayer, summaryPanel, left + 14, 573, 327, 77);
        Place(
            SecondaryNativeLayer,
            ChromeText("ملخص النتيجة", 10.5, "#344052", FontWeights.Bold),
            left + 30,
            579,
            115,
            20);
        var summaryText = ChromeText(summary, 9.2, "#626C79", FontWeights.SemiBold);
        summaryText.TextAlignment = TextAlignment.Right;
        summaryText.TextWrapping = TextWrapping.Wrap;
        Place(SecondaryNativeLayer, summaryText, left + 30, 602, 292, 42);

        Place(
            SecondaryNativeLayer,
            ChromeText("أبرز المخرجات", 9.5, "#586273", FontWeights.SemiBold),
            left + 20,
            658,
            100,
            19);
        var thumbs = CreateReferenceCrop(imageName, sourceRect);
        Place(SecondaryNativeLayer, thumbs, left + 18, 681, 316, 70);

        var footer = ChromePanel("#FFFDFCFB", "#E8E3DC", 8);
        Place(SecondaryNativeLayer, footer, left + 14, 758, 327, 24);
        Place(
            SecondaryNativeLayer,
            ChromeText("عرض جميع المخرجات", 8.9, "#596477", FontWeights.SemiBold),
            left + 111,
            760,
            118,
            19);
    }

    private void BuildNativeRecoveryComparison()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 1100, 475, 370, 335);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            1115,
            489,
            27,
            27);
        Place(
            SecondaryNativeLayer,
            ChromeText("⚖", 15, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1121,
            493,
            18,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("مقارنة الفروع", 15.5, "#273247", FontWeights.Bold),
            1155,
            486,
            130,
            28);
        var detailed = ChromePanel("#FFFFFF", "#E0DDD8", 8);
        Place(SecondaryNativeLayer, detailed, 1360, 486, 92, 29);
        Place(
            SecondaryNativeLayer,
            ChromeText("مقارنة تفصيلية  ›", 8.8, "#5270A5", FontWeights.SemiBold),
            1368,
            491,
            76,
            18);

        Place(
            SecondaryNativeLayer,
            ChromePanel("#F7F8FA", "#E3E2DF", 0),
            1114,
            527,
            340,
            36);
        Place(
            SecondaryNativeLayer,
            ChromeText("المعيار", 9.3, "#5A6575", FontWeights.Bold),
            1370,
            534,
            62,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("الفرع A\nالخصوصية", 9.2, "#168F49", FontWeights.Bold),
            1252,
            529,
            80,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("الفرع B\nالذكاء المتقدم", 9.2, "#7148C3", FontWeights.Bold),
            1132,
            529,
            88,
            30);

        AddRecoveryComparisonRow(563, "الموديل المستخدم", "Claude 3.7 Sonnet", "GPT-4.1", "#344052", "#344052");
        AddRecoveryComparisonRow(596, "مستوى التفكير", "عميق", "إبداعي", "#15934A", "#7148C3");
        AddRecoveryComparisonRow(629, "الأداء المتوقع", "+15%", "+28%", "#15934A", "#7148C3");
        AddRecoveryComparisonRow(662, "الأمان والخصوصية", "متفوق", "جيد", "#15934A", "#C48118");
        AddRecoveryComparisonRow(695, "قابلية التوسع", "جيد", "متفوق", "#4B63A8", "#7148C3");
        AddRecoveryComparisonRow(728, "جاهزية الإنتاج", "جاهز", "قيد المراجعة", "#15934A", "#C48118");

        var a = ChromePanel("#E9F9EF", "#C1EBCF", 8);
        Place(SecondaryNativeLayer, a, 1240, 758, 97, 24);
        Place(SecondaryNativeLayer, ChromeText("A  VERIFIED", 8.2, "#15934A", FontWeights.Bold, FlowDirection.LeftToRight), 1250, 761, 78, 17);
        var b = ChromePanel("#FFF4DD", "#F3D89C", 8);
        Place(SecondaryNativeLayer, b, 1131, 758, 100, 24);
        Place(SecondaryNativeLayer, ChromeText("B  PROPOSAL", 8.2, "#C58118", FontWeights.Bold, FlowDirection.LeftToRight), 1140, 761, 82, 17);
    }

    private void AddRecoveryComparisonRow(
        double top,
        string label,
        string aValue,
        string bValue,
        string aColor,
        string bColor)
    {
        Place(SecondaryNativeLayer, ChromePanel("#EAE7E2", "#EAE7E2", 0), 1114, top + 31, 340, 1);
        Place(SecondaryNativeLayer, ChromeText(label, 8.8, "#5B6574", FontWeights.SemiBold), 1350, top + 5, 82, 20);
        Place(SecondaryNativeLayer, ChromeText(aValue, 8.8, aColor, FontWeights.SemiBold, FlowDirection.LeftToRight), 1232, top + 5, 101, 20);
        Place(SecondaryNativeLayer, ChromeText(bValue, 8.8, bColor, FontWeights.SemiBold, FlowDirection.LeftToRight), 1123, top + 5, 101, 20);
    }

    private void BuildNativeRecoveryBottomPanels()
    {
        var firstChild = SecondaryNativeLayer.Children.Count;

        BuildNativeRecoveryEventLog();
        BuildNativeRecoveryEvidence();
        BuildNativeRecoveryActions();

        TranslateSecondaryChildren(firstChild, 50);
    }

    private void TranslateSecondaryChildren(int firstChild, double deltaY)
    {
        for (var index = firstChild; index < SecondaryNativeLayer.Children.Count; index++)
        {
            if (SecondaryNativeLayer.Children[index] is not FrameworkElement element)
            {
                continue;
            }

            var top = Canvas.GetTop(element);
            if (!double.IsNaN(top))
            {
                Canvas.SetTop(element, top + deltaY);
            }
        }
    }

    private void BuildNativeRecoveryEventLog()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 16, 798, 490, 170);
        Place(SecondaryNativeLayer, ChromeText("◷", 21, "#D29A2C", FontWeights.SemiBold, FlowDirection.LeftToRight), 30, 808, 28, 28);
        Place(SecondaryNativeLayer, ChromeText("السجل الزمني والإجراءات", 14.5, "#2C374A", FontWeights.Bold), 69, 806, 180, 27);
        AddTagChipToCanvas(SecondaryNativeLayer, 438, 805, 52, "الكل", "#FFFFFF", "#626C79");

        AddRecoveryTimelineEvent(29, 842, "#8457E6", "تم إنشاء الفرع B", "15 فبراير 2025 · 09:20");
        AddRecoveryTimelineEvent(147, 842, "#25C86A", "تم إنشاء الفرع A", "12 فبراير 2025 · 10:15");
        AddRecoveryTimelineEvent(265, 842, "#2F75F3", "تم استرجاع نقطة حفظ #3", "5 فبراير 2025 · 14:30");
        AddRecoveryTimelineEvent(383, 842, "#2F75F3", "تم إنشاء نقطة حفظ #3", "5 فبراير 2025 · 14:28");
    }

    private void AddRecoveryTimelineEvent(
        double left,
        double top,
        string accent,
        string title,
        string time)
    {
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
            left,
            top,
            18,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("•", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 6,
            top,
            8,
            14);
        var titleText = ChromeText(title, 8.9, "#344052", FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, titleText, left - 4, top + 24, 105, 32);
        var timeText = ChromeText(time, 7.7, "#7A8390");
        timeText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, timeText, left - 4, top + 59, 105, 26);
    }

    private void BuildNativeRecoveryEvidence()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 516, 798, 421, 170);
        Place(SecondaryNativeLayer, ChromeText("⛓", 20, "#5279D7", FontWeights.SemiBold, FlowDirection.LeftToRight), 531, 808, 28, 28);
        Place(SecondaryNativeLayer, ChromeText("أدلة ومقتطفات مهمة", 14.5, "#2C374A", FontWeights.Bold), 568, 806, 170, 27);
        Place(SecondaryNativeLayer, ChromeText("•••", 15, "#6A7483", FontWeights.Bold, FlowDirection.LeftToRight), 900, 808, 22, 25);

        AddRecoveryEvidenceItem(531, 842, 185, "تقرير تقييم الخصوصية .pdf", "2.4 MB · 12 فبراير 2025", "▧");
        AddRecoveryEvidenceItem(730, 842, 185, "مقتطف من سجل التحديث", "تم تعديل تشفير من طرف لطرف", "▤");
        AddRecoveryEvidenceItem(531, 907, 185, "مخطط المعمارية الجديد", "1.1 MB · 12 فبراير 2025", "▣");

        var more = ChromePanel("#FFFFFF", "#E1DED9", 8);
        Place(SecondaryNativeLayer, more, 730, 907, 191, 43);
        Place(SecondaryNativeLayer, ChromeText("عرض جميع الأدلة  ›", 9.2, "#4D5A6D", FontWeights.SemiBold), 775, 917, 110, 22);
    }

    private void AddRecoveryEvidenceItem(
        double left,
        double top,
        double width,
        string title,
        string subtitle,
        string glyph)
    {
        var item = ChromePanel("#FFFDFCFB", "#E7E3DD", 7);
        Place(SecondaryNativeLayer, item, left, top, width, 54);
        Place(SecondaryNativeLayer, ChromeText(glyph, 15, "#5279D7", FontWeights.SemiBold, FlowDirection.LeftToRight), left + 10, top + 9, 22, 24);
        var titleText = ChromeText(title, 8.8, "#344052", FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, titleText, left + 38, top + 5, width - 49, 20);
        var subText = ChromeText(subtitle, 7.7, "#7A8390");
        subText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, subText, left + 38, top + 27, width - 49, 18);
    }

    private void BuildNativeRecoveryActions()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 946, 798, 524, 170);
        Place(SecondaryNativeLayer, ChromeText("ϟ", 20, "#E89522", FontWeights.SemiBold, FlowDirection.LeftToRight), 960, 808, 28, 28);
        Place(SecondaryNativeLayer, ChromeText("الإجراءات المتاحة", 14.5, "#2C374A", FontWeights.Bold), 995, 806, 150, 27);

        AddRecoveryActionVisual(960, 842, 240, "#F7F9FF", "#C7D9F4", "#3170C8", "↶", "استرجاع هذه النقطة", "العودة للمشروع من هذه النقطة");
        AddRecoveryActionVisual(1214, 842, 240, "#F7F9FF", "#C7D9F4", "#3170C8", "⑂", "إنشاء فرع جديد", "بداية فرع جديد انطلاقاً من هنا");
        AddRecoveryActionVisual(960, 900, 240, "#F0FBF3", "#C7EBD2", "#168F49", "⇧", "ترقية نتيجة الفرع", "دمج أفضل النتائج في المسار الرئيسي");
        AddRecoveryActionVisual(1214, 900, 240, "#FFFFFF", "#E2DED8", "#4F5968", "↗", "فتح في مساحة العمل", "فتح الملفات والمخرجات");
        var danger = ChromePanel("#FFF0F1", "#F1C9CE", 7);
        Place(SecondaryNativeLayer, danger, 1214, 948, 240, 18);
        Place(SecondaryNativeLayer, ChromeText("▣  حذف الفرع المحدد — فعل مدمر", 8, "#D83D50", FontWeights.SemiBold), 1250, 949, 172, 15);
    }

    private void AddRecoveryActionVisual(
        double left,
        double top,
        double width,
        string background,
        string border,
        string accent,
        string glyph,
        string title,
        string subtitle)
    {
        var item = ChromePanel(background, border, 8);
        Place(SecondaryNativeLayer, item, left, top, width, 50);
        Place(SecondaryNativeLayer, ChromeText(glyph, 18, accent, FontWeights.Bold, FlowDirection.LeftToRight), left + 12, top + 9, 26, 27);
        var titleText = ChromeText(title, 9.6, "#354052", FontWeights.Bold);
        titleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, titleText, left + 45, top + 5, width - 58, 20);
        var subtitleText = ChromeText(subtitle, 7.8, "#747D89");
        subtitleText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, subtitleText, left + 45, top + 25, width - 58, 18);
    }

    private void BuildNativePulseStory()
    {
        BuildNativePulseHeader();
        BuildNativePulseTimeline();
        BuildNativePulseStorySurface();
        BuildNativePulseCards();
    }

    private void BuildNativePulseHeader()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFDFBF8", "#EEE9E2", 0, new Thickness(0)),
            238,
            49,
            1232,
            113);

        Place(
            SecondaryNativeLayer,
            ChromeText("المشاريع   /   Smart Secretary V2   /   نبض المشروع", 10.5, "#707A89", FontWeights.SemiBold),
            252,
            60,
            330,
            23);

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#2F85F3"),
                Stroke = Brush("#C7E0FB"),
                StrokeThickness = 1.5,
                IsHitTestVisible = false,
            },
            268,
            95,
            52,
            52);
        Place(
            SecondaryNativeLayer,
            ChromeText("▧", 25, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            282,
            105,
            28,
            32);

        Place(
            SecondaryNativeLayer,
            ChromeText("نبض المشروع", 31, "#121C36", FontWeights.Bold),
            336,
            91,
            170,
            45);
        Place(
            SecondaryNativeLayer,
            ChromeText("✦", 28, "#2F8DFF", FontWeights.Bold, FlowDirection.LeftToRight),
            506,
            93,
            32,
            36);
        Place(
            SecondaryNativeLayer,
            ChromeText("قصة مرئية لرحلة المشروع من المشكلة إلى الأثر", 12.5, "#626D7C", FontWeights.SemiBold),
            336,
            131,
            333,
            24);

        var selector = ChromePanel("#F8FBFF", "#DCE5F0", 11);
        Place(SecondaryNativeLayer, selector, 1030, 79, 410, 72);
        var thumb = CreateReferenceCrop(
            "07-pulse_visual_project_story.png",
            new Int32Rect(1047, 91, 48, 48));
        Place(SecondaryNativeLayer, thumb, 1047, 91, 48, 48);
        Place(
            SecondaryNativeLayer,
            ChromeText("Smart Secretary V2", 15.5, "#17233B", FontWeights.Bold, FlowDirection.LeftToRight),
            1104,
            89,
            190,
            26);
        Place(
            SecondaryNativeLayer,
            ChromeText("تحديثات الخصوصية وإدارة البيانات", 10, "#6C7685", FontWeights.SemiBold),
            1104,
            119,
            210,
            19);
        var running = ChromePanel("#EEF5FF", "#C9DCF6", 8);
        Place(SecondaryNativeLayer, running, 1313, 96, 93, 29);
        Place(
            SecondaryNativeLayer,
            ChromeText("قيد التنفيذ", 9.5, "#2768C9", FontWeights.SemiBold),
            1333,
            101,
            53,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText("⌄", 16, "#5A6575", FontWeights.Bold, FlowDirection.LeftToRight),
            1414,
            101,
            15,
            19);
    }

    private void BuildNativePulseTimeline()
    {
        var card = ChromePanel("#FFFCFBF8", "#E4E0DA", 12);
        Place(SecondaryNativeLayer, card, 244, 174, 1200, 112);

        var line = new Path
        {
            Data = Geometry.Parse("M 334,221 C 425,194 503,237 596,217 S 783,236 872,218 S 1058,196 1152,219 S 1304,232 1377,217"),
            Stroke = Brush("#79BDEB"),
            StrokeThickness = 1.8,
            StrokeDashArray = new DoubleCollection { 1, 4 },
            Opacity = 0.58,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(line);

        AddPulseTimelineNode(322, 192, "#2F83EE", "◉", "اليوم", "تحسينات الخصوصية", true);
        AddPulseTimelineNode(504, 193, "#2DC86B", "▣", "الأسبوع الماضي", "إطلاق النسخة التجريبية", false);
        AddPulseTimelineNode(691, 193, "#8B5DE4", "◇", "قبل أسبوعين", "تحسين البنية", false);
        AddPulseTimelineNode(876, 193, "#E8A332", "♟", "قبل شهر", "أبحاث المستخدمين", false);
        AddPulseTimelineNode(1065, 193, "#EB596A", "♨", "قبل شهرين", "تحديد المشكلة", false);
        AddPulseTimelineNode(1252, 193, "#5E6A83", "◈", "قبل 3 أشهر", "بداية المشروع", false);

        var full = ChromePanel("#FBF8FF", "#DCCDF5", 8);
        Place(SecondaryNativeLayer, full, 1300, 185, 128, 31);
        Place(
            SecondaryNativeLayer,
            ChromeText("عرض الجدول الزمني الكامل", 8.8, "#7252C1", FontWeights.SemiBold),
            1314,
            191,
            102,
            20);
    }

    private void AddPulseTimelineNode(
        double left,
        double top,
        string accent,
        string glyph,
        string title,
        string subtitle,
        bool active)
    {
        if (active)
        {
            Place(
                SecondaryNativeLayer,
                new Ellipse
                {
                    Fill = Brush("#EAF4FF"),
                    Stroke = Brush("#AFD3FB"),
                    StrokeThickness = 1.3,
                    IsHitTestVisible = false,
                },
                left - 9,
                top - 9,
                56,
                56);
        }
        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#FAFBFC"),
                Stroke = Brush(accent),
                StrokeThickness = active ? 2.5 : 1.7,
                IsHitTestVisible = false,
            },
            left,
            top,
            38,
            38);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 16, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 10,
            top + 6,
            20,
            24);
        var titleText = ChromeText(title, 10, active ? "#2369C9" : "#3E495A", active ? FontWeights.Bold : FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, titleText, left - 42, top + 45, 122, 20);
        var subtitleText = ChromeText(subtitle, 8.7, active ? "#3171C5" : "#7B8490");
        subtitleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, subtitleText, left - 53, top + 65, 144, 20);
    }

    private void BuildNativePulseStorySurface()
    {
        var card = ChromePanel("#FFFCFBF8", "#E4E0DA", 12);
        Place(SecondaryNativeLayer, card, 244, 300, 1200, 340);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            258,
            312,
            26,
            26);
        Place(
            SecondaryNativeLayer,
            ChromeText("✦", 13, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            265,
            315,
            15,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("القصة المرئية للمشروع", 18, "#18243B", FontWeights.Bold),
            295,
            308,
            225,
            31);
        Place(
            SecondaryNativeLayer,
            ChromeText("من التحدي إلى التأثير", 10.3, "#818895"),
            520,
            314,
            120,
            20);

        AddPulseFilterChip(915, "عمليات التسليم", false);
        AddPulseFilterChip(1020, "الاكتشافات", false);
        AddPulseFilterChip(1112, "التحديات", false);
        AddPulseFilterChip(1198, "الإنجازات", false);
        AddPulseFilterChip(1285, "التحديثات", false);
        AddPulseFilterChip(1372, "الكل", true);

        // Before panel.
        var before = ChromePanel("#FFFDFCFB", "#E8E3DC", 10);
        Place(SecondaryNativeLayer, before, 258, 350, 382, 284);
        var beforeBadge = ChromePanel("#FFE7E8", "#F1C8CD", 8);
        Place(SecondaryNativeLayer, beforeBadge, 271, 362, 62, 28);
        Place(
            SecondaryNativeLayer,
            ChromeText("قبل", 10, "#D64658", FontWeights.Bold),
            290,
            367,
            27,
            18);
        var beforeTitle = ChromeText("تجربة معقدة ومخاوف خصوصية", 14.5, "#273247", FontWeights.Bold);
        beforeTitle.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, beforeTitle, 365, 376, 246, 28);
        var beforeBody = ChromeText(
            "إدارة البيانات كانت يدوية ومعقدة، مع مخاوف\nحول خصوصية المستخدمين.",
            10.3,
            "#697382",
            FontWeights.SemiBold);
        beforeBody.TextAlignment = TextAlignment.Right;
        beforeBody.LineHeight = 18;
        Place(SecondaryNativeLayer, beforeBody, 355, 412, 260, 47);
        var beforeMedia = CreateReferenceCrop(
            "07-pulse_visual_project_story.png",
            new Int32Rect(278, 439, 366, 146));
        Place(SecondaryNativeLayer, beforeMedia, 271, 460, 356, 150);

        // Central media panel.
        var story = ChromePanel("#F8FAFD", "#DDE4ED", 10);
        Place(SecondaryNativeLayer, story, 651, 350, 382, 284);
        var storyMedia = CreateReferenceCrop(
            "07-pulse_visual_project_story.png",
            new Int32Rect(675, 345, 335, 190));
        Place(SecondaryNativeLayer, storyMedia, 666, 362, 352, 205);
        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#D9111A2B"),
                Stroke = Brush("#FFFFFF"),
                StrokeThickness = 2,
                IsHitTestVisible = false,
            },
            808,
            425,
            70,
            70);
        Place(
            SecondaryNativeLayer,
            ChromeText("▶", 31, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            832,
            439,
            33,
            39);
        var duration = ChromePanel("#D9111A2B", "#00FFFFFF", 6, new Thickness(0));
        Place(SecondaryNativeLayer, duration, 949, 536, 55, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText("02:18", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            958,
            540,
            39,
            17);
        Place(
            SecondaryNativeLayer,
            ChromeText("فيديو القصة", 13.5, "#243047", FontWeights.Bold),
            744,
            574,
            110,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("من المشكلة إلى الحل في دقيقتين", 9.4, "#707988", FontWeights.SemiBold),
            744,
            598,
            180,
            18);

        // After panel.
        var after = ChromePanel("#F6FFF9", "#D6EEDC", 10);
        Place(SecondaryNativeLayer, after, 1044, 350, 386, 284);
        var afterBadge = ChromePanel("#E1F8E8", "#BDE8C8", 8);
        Place(SecondaryNativeLayer, afterBadge, 1057, 362, 63, 28);
        Place(
            SecondaryNativeLayer,
            ChromeText("بعد", 10, "#159A4C", FontWeights.Bold),
            1076,
            367,
            27,
            18);
        var afterTitle = ChromeText("خصوصية أقوى وتجربة أبسط", 14.5, "#233447", FontWeights.Bold);
        afterTitle.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, afterTitle, 1152, 376, 246, 28);
        var afterBody = ChromeText(
            "نظام ذكي وآمن لإدارة البيانات مع تحكم كامل\nللمستخدمين وشفافية عالية.",
            10.3,
            "#607063",
            FontWeights.SemiBold);
        afterBody.TextAlignment = TextAlignment.Right;
        afterBody.LineHeight = 18;
        Place(SecondaryNativeLayer, afterBody, 1142, 412, 260, 47);
        var afterMedia = CreateReferenceCrop(
            "07-pulse_visual_project_story.png",
            new Int32Rect(1051, 439, 376, 145));
        Place(SecondaryNativeLayer, afterMedia, 1057, 460, 360, 150);
    }

    private void AddPulseFilterChip(double left, string label, bool active)
    {
        var chip = ChromePanel(active ? "#2475F3" : "#FFFFFF", active ? "#2475F3" : "#E0DDD8", 8);
        Place(SecondaryNativeLayer, chip, left, 308, active ? 61 : 92, 30);
        var text = ChromeText(label, 8.7, active ? "#FFFFFF" : "#596477", FontWeights.SemiBold);
        text.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, text, left + 7, 313, (active ? 61 : 92) - 14, 19);
    }

    private void BuildNativePulseCards()
    {
        AddPulseCard(
            18,
            "#F1FBF4",
            "#BFE7CA",
            "#159A4C",
            "✓",
            "إنجاز رئيسي",
            "VERIFIED",
            "إطلاق طبقة الخصوصية الجديدة",
            "تم تفعيل التشفير الشامل وإدارة الصلاحيات.",
            "لحماية بيانات المستخدمين وبناء الثقة.",
            "تعميم الميزة على جميع المستخدمين.",
            "07-pulse_visual_project_story.png",
            new Int32Rect(31, 657, 276, 83),
            "عرض التفاصيل",
            "فتح في المشروع");

        AddPulseCard(
            323,
            "#FFF3F4",
            "#F0C9CE",
            "#E64457",
            "▲",
            "تحدي / عائق",
            "EVIDENCE-BACKED",
            "ارتفاع زمن استجابة واجهة الإعدادات",
            "زمن الاستجابة زاد إلى 2.8 ثانية.",
            "بسبب زيادة حجم البيانات المؤقتة.",
            "تنفيذ تحسينات الأداء في الأسبوع القادم.",
            "07-pulse_visual_project_story.png",
            new Int32Rect(343, 657, 252, 83),
            "عرض التحليل",
            "إنشاء مهمة");

        AddPulseCard(
            613,
            "#F7F2FF",
            "#DCCDF5",
            "#7D55DB",
            "◇",
            "اكتشاف / غير معروف",
            "UNKNOWN",
            "سؤال حول تخزين البيانات الإقليمية",
            "مطلوب فهم أفضل للقوانين المحلية في بعض الدول.",
            "قد يؤثر على طريقة تخزين البيانات.",
            "إجراء بحث قانوني وتقييم الخيارات.",
            "07-pulse_visual_project_story.png",
            new Int32Rect(627, 657, 258, 83),
            "عرض التفاصيل",
            "بدء البحث");

        AddPulseCard(
            903,
            "#F2F8FF",
            "#CADFF7",
            "#2673D5",
            "▧",
            "تسليم / تعاون",
            "PROPOSAL",
            "محطة تسليم إلى فريق البنية التحتية",
            "جاهز لتسليم نسخة التشفير الجديدة.",
            "للتنفيذ في بيئة الإنتاج.",
            "مراجعة التسليم وتحديد موعد النشر.",
            "07-pulse_visual_project_story.png",
            new Int32Rect(917, 657, 257, 83),
            "عرض الحزمة",
            "تسليم الآن");

        AddPulseCard(
            1192,
            "#F1FBF4",
            "#BFE7CA",
            "#159A4C",
            "✓",
            "نتيجة محققة",
            "VERIFIED",
            "زيادة مستوى الأمان إلى 98%",
            "تحسن معدل الامتثال الأمني من 78% إلى 98%.",
            "بفضل تطبيق طبقة التشفير الجديدة.",
            "الحفاظ على المستوى ومراقبة مستمرة.",
            "07-pulse_visual_project_story.png",
            new Int32Rect(1208, 657, 238, 83),
            "عرض التقرير",
            "مشاركة النتيجة");
    }

    private void AddPulseCard(
        double left,
        string background,
        string border,
        string accent,
        string glyph,
        string category,
        string truth,
        string title,
        string changed,
        string why,
        string next,
        string imageName,
        Int32Rect crop,
        string secondaryAction,
        string primaryAction)
    {
        const double top = 648;
        const double width = 282;
        const double height = 366;

        var card = ChromePanel(background, border, 11);
        Place(SecondaryNativeLayer, card, left, top, width, height);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
            left + 13,
            top + 14,
            29,
            29);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 15, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 21,
            top + 17,
            17,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText(category, 12.5, accent, FontWeights.Bold),
            left + 51,
            top + 14,
            105,
            25);
        var truthBadge = ChromePanel(truth == "UNKNOWN" ? "#F1ECFF" : truth == "PROPOSAL" ? "#E8F3FF" : truth == "EVIDENCE-BACKED" ? "#FFE7EA" : "#E6F8EC", border, 8);
        Place(SecondaryNativeLayer, truthBadge, left + 165, top + 14, 104, 26);
        Place(
            SecondaryNativeLayer,
            ChromeText(truth, 7.8, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 178,
            top + 18,
            80,
            17);

        var media = CreateReferenceCrop(imageName, crop);
        Place(SecondaryNativeLayer, media, left + 14, top + 50, width - 28, 83);

        var titleText = ChromeText(title, 11.7, "#283448", FontWeights.Bold);
        titleText.TextAlignment = TextAlignment.Right;
        titleText.TextWrapping = TextWrapping.Wrap;
        Place(SecondaryNativeLayer, titleText, left + 14, top + 140, width - 28, 31);

        AddPulseFactRow(left, top + 177, width, "ما الذي تغير؟", changed);
        AddPulseFactRow(left, top + 215, width, "لماذا؟", why);
        AddPulseFactRow(left, top + 253, width, "ماذا بعد؟", next);

        var evidence = ChromePanel("#FFFDFCFB", "#E4E0DB", 7);
        Place(SecondaryNativeLayer, evidence, left + 14, top + 289, width - 28, 27);
        Place(
            SecondaryNativeLayer,
            ChromeText("الدليل", 8.3, "#485568", FontWeights.Bold),
            left + 18,
            top + 293,
            40,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("▧  مصدر مرتبط", 8.1, "#677183", FontWeights.SemiBold),
            left + 68,
            top + 293,
            91,
            18);

        var secondary = ChromePanel("#FFFFFF", "#DDD9D3", 7);
        Place(SecondaryNativeLayer, secondary, left + 14, top + 321, 118, 28);
        Place(
            SecondaryNativeLayer,
            ChromeText(secondaryAction, 8.7, "#4D596B", FontWeights.SemiBold),
            left + 28,
            top + 326,
            90,
            18);

        var primary = ChromePanel(truth == "UNKNOWN" ? "#744DE7" : truth == "EVIDENCE-BACKED" ? "#E19A2B" : "#2475F3", "#00FFFFFF", 7, new Thickness(0));
        Place(SecondaryNativeLayer, primary, left + 141, top + 321, 127, 28);
        Place(
            SecondaryNativeLayer,
            ChromeText(primaryAction, 8.7, "#FFFFFF", FontWeights.SemiBold),
            left + 153,
            top + 326,
            101,
            18);
    }

    private void AddPulseFactRow(
        double left,
        double top,
        double width,
        string label,
        string value)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 8.2, "#3B4658", FontWeights.Bold),
            left + width - 91,
            top,
            75,
            18);
        var valueText = ChromeText(value, 8.2, "#687280", FontWeights.SemiBold);
        valueText.TextAlignment = TextAlignment.Right;
        valueText.TextTrimming = TextTrimming.CharacterEllipsis;
        Place(SecondaryNativeLayer, valueText, left + 14, top, width - 111, 18);
    }

    private void BuildNativeWorkReceipt()
    {
        BuildNativeWorkReceiptHero();
        BuildNativeWorkReceiptProjectSummary();
        BuildNativeWorkReceiptStages();
        BuildNativeWorkReceiptMainPanels();
        BuildNativeWorkReceiptBottomPanels();
    }

    private void BuildNativeWorkReceiptHero()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFDF9F3", "#F1ECE4", 0, new Thickness(0)),
            238,
            49,
            1232,
            96);

        AddReceiptHeroPath(
            "M 252,88 C 367,26 468,56 584,126",
            "#58C8E8",
            1.5,
            0.42);
        AddReceiptHeroPath(
            "M 267,121 C 411,47 497,60 618,140",
            "#8C68EA",
            1.5,
            0.33);
        AddReceiptHeroPath(
            "M 1186,127 C 1296,65 1367,68 1458,89",
            "#F0A766",
            1.5,
            0.32);

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#24BE65"),
                Stroke = Brush("#BCE9CB"),
                StrokeThickness = 2,
                IsHitTestVisible = false,
            },
            610,
            69,
            48,
            48);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 28, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            622,
            75,
            27,
            32);

        Place(
            SecondaryNativeLayer,
            ChromeText("تم إنجاز المشروع بنجاح", 34, "#101A30", FontWeights.Bold),
            620,
            63,
            365,
            50);
        Place(
            SecondaryNativeLayer,
            ChromeText("تم تسليم جميع المتطلبات واعتماد مخرجات المشروع", 12, "#697383", FontWeights.SemiBold),
            690,
            108,
            370,
            24);

        var impactTitle = ChromeText("من الفكرة إلى أثر حقيقي", 17, "#364154", FontWeights.Bold);
        impactTitle.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, impactTitle, 1158, 68, 240, 30);
        var impactSub = ChromeText("بناء أسرع · بذكاء أكبر", 10.5, "#7A8391", FontWeights.SemiBold);
        impactSub.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, impactSub, 1180, 102, 215, 22);
    }

    private void AddReceiptHeroPath(
        string data,
        string color,
        double thickness,
        double opacity)
    {
        SecondaryNativeLayer.Children.Add(
            new Path
            {
                Data = Geometry.Parse(data),
                Stroke = Brush(color),
                StrokeThickness = thickness,
                Opacity = opacity,
                IsHitTestVisible = false,
            });
    }

    private void BuildNativeWorkReceiptProjectSummary()
    {
        var card = ChromePanel("#FFFCFBF9", "#E3DED7", 12);
        Place(SecondaryNativeLayer, card, 244, 145, 1200, 140);

        var icon = ChromePanel("#F1F6FF", "#D4E1F7", 12);
        Place(SecondaryNativeLayer, icon, 262, 162, 78, 78);
        Place(
            SecondaryNativeLayer,
            ChromeText("⬡", 43, "#2C7FE9", FontWeights.Bold, FlowDirection.LeftToRight),
            281,
            176,
            40,
            48);

        Place(
            SecondaryNativeLayer,
            ChromeText("Smart Secretary V2", 26, "#101A31", FontWeights.Bold, FlowDirection.LeftToRight),
            357,
            159,
            280,
            40);

        var verified = ChromePanel("#E8F9ED", "#BDE9C8", 8);
        Place(SecondaryNativeLayer, verified, 626, 166, 92, 26);
        Place(
            SecondaryNativeLayer,
            ChromeText("● VERIFIED", 8.5, "#15964B", FontWeights.Bold, FlowDirection.LeftToRight),
            638,
            170,
            68,
            18);

        Place(
            SecondaryNativeLayer,
            ChromeText("تحديث الخصوصية وإدارة البيانات", 14.5, "#677182", FontWeights.SemiBold),
            357,
            198,
            290,
            26);

        AddReceiptMetadata(262, 241, "▦", "#PRJ-2025-042");
        AddReceiptMetadata(443, 241, "⬡", "تطوير منصات");
        AddReceiptMetadata(607, 241, "▣", "بدأ في 25 مايو 2025");
        AddReceiptMetadata(820, 241, "✓", "اكتمل في 20 يونيو 2025");
        AddReceiptMetadata(1058, 241, "◷", "المدة الإجمالية 25 يوماً");

        var share = ChromePanel("#FFFFFF", "#E2DED8", 8);
        Place(SecondaryNativeLayer, share, 1272, 158, 116, 34);
        Place(
            SecondaryNativeLayer,
            ChromeText("مشاركة المشروع  ↗", 9.5, "#4A5566", FontWeights.SemiBold),
            1284,
            164,
            92,
            21);
        var more = ChromePanel("#FFFFFF", "#E2DED8", 8);
        Place(SecondaryNativeLayer, more, 1395, 158, 38, 34);
        Place(
            SecondaryNativeLayer,
            ChromeText("•••", 14, "#526072", FontWeights.Bold, FlowDirection.LeftToRight),
            1404,
            161,
            20,
            22);

        var accepted = ChromePanel("#EEFFF4", "#48CC7D", 10);
        Place(SecondaryNativeLayer, accepted, 1140, 200, 293, 65);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#21B95E"), IsHitTestVisible = false },
            1154,
            214,
            36,
            36);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 20, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1164,
            218,
            20,
            24);
        var acceptedTitle = ChromeText("تم التسليم واعتماد المشروع", 12.5, "#176B3B", FontWeights.Bold);
        acceptedTitle.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, acceptedTitle, 1205, 209, 205, 24);
        var acceptedSub = ChromeText("مغلق · جميع المخرجات مكتملة وموثقة", 9.6, "#5D7867", FontWeights.SemiBold);
        acceptedSub.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, acceptedSub, 1205, 235, 205, 20);
    }

    private void AddReceiptMetadata(
        double left,
        double top,
        string glyph,
        string value)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 14, "#5D6980", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left,
            top,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 9.5, "#596477", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left + 28,
            top,
            164,
            22);
    }

    private void BuildNativeWorkReceiptStages()
    {
        var stages = ChromePanel("#FFFCFBF8", "#E3DED7", 12);
        Place(SecondaryNativeLayer, stages, 244, 295, 1200, 165);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            264,
            309,
            26,
            26);
        Place(
            SecondaryNativeLayer,
            ChromeText("◉", 12, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            271,
            312,
            14,
            17);
        Place(
            SecondaryNativeLayer,
            ChromeText("مراحل المشروع", 17, "#253147", FontWeights.Bold),
            300,
            305,
            145,
            28);

        var allDone = ChromePanel("#E8F9ED", "#BFE8CB", 8);
        Place(SecondaryNativeLayer, allDone, 452, 308, 111, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText("جميع المراحل مكتملة", 8.8, "#15954A", FontWeights.SemiBold),
            468,
            312,
            80,
            17);

        var sevenOfSeven = ChromePanel("#F7F3FF", "#DCCFF3", 8);
        Place(SecondaryNativeLayer, sevenOfSeven, 1310, 307, 118, 27);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓  7 من 7 مراحل مكتملة", 8.5, "#6B50B9", FontWeights.SemiBold),
            1322,
            312,
            95,
            18);

        var path = new Path
        {
            Data = Geometry.Parse("M 307,367 C 393,354 470,376 557,364 S 729,376 815,365 S 988,354 1072,365 S 1248,377 1350,365"),
            Stroke = Brush("#63D9A0"),
            StrokeThickness = 2,
            StrokeDashArray = new DoubleCollection { 1, 4 },
            Opacity = 0.72,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(path);

        AddReceiptStage(286, 347, "الانطلاق", "تم الاكتمال", "25 مايو 2025", "✓");
        AddReceiptStage(467, 347, "الاستراتيجية", "تم الاكتمال", "27 مايو 2025", "⌘");
        AddReceiptStage(648, 347, "البحث", "تم الاكتمال", "30 مايو 2025", "✓");
        AddReceiptStage(830, 347, "التصميم", "تم الاكتمال", "02 يونيو 2025", "✓");
        AddReceiptStage(1011, 347, "التطوير", "تم الاكتمال", "10 يونيو 2025", "✓");
        AddReceiptStage(1192, 347, "الاختبار", "تم الاكتمال", "16 يونيو 2025", "✓");
        AddReceiptStage(1360, 347, "التسليم", "تم الاكتمال", "20 يونيو 2025", "⬡");
    }

    private void AddReceiptStage(
        double left,
        double top,
        string title,
        string state,
        string date,
        string glyph)
    {
        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush("#20BC61"),
                Stroke = Brush("#D4F2DE"),
                StrokeThickness = 4,
                IsHitTestVisible = false,
            },
            left,
            top,
            42,
            42);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 18, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 11,
            top + 8,
            22,
            24);

        var titleText = ChromeText(title, 10.8, "#2B374A", FontWeights.Bold);
        titleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, titleText, left - 28, top + 47, 98, 20);
        var stateText = ChromeText(state, 8.8, "#24A95A", FontWeights.SemiBold);
        stateText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, stateText, left - 28, top + 67, 98, 18);
        var dateText = ChromeText(date, 8, "#79818D");
        dateText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, dateText, left - 35, top + 86, 112, 18);
    }

    private void BuildNativeWorkReceiptMainPanels()
    {
        BuildNativeBusinessReceipt();
        BuildNativeFinalOutputs();
        BuildNativeReceiptEvidence();
        BuildNativeUsageSummary();
    }

    private void BuildNativeBusinessReceipt()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 244, 480, 312, 370);

        Place(
            SecondaryNativeLayer,
            ChromeText("▣", 23, "#20B765", FontWeights.Bold, FlowDirection.LeftToRight),
            260,
            491,
            30,
            30);
        Place(
            SecondaryNativeLayer,
            ChromeText("إيصال الأعمال", 17, "#273247", FontWeights.Bold),
            300,
            487,
            135,
            30);
        var verified = ChromePanel("#E8F9ED", "#BDE8C8", 8);
        Place(SecondaryNativeLayer, verified, 445, 491, 88, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText("● VERIFIED", 8, "#16964B", FontWeights.Bold, FlowDirection.LeftToRight),
            458,
            495,
            64,
            17);

        AddReceiptKeyValue(265, 531, "الجهة الطالبة", "المجلس الداخلي");
        AddReceiptKeyValue(395, 531, "تاريخ الطلب", "25 مايو 2025");

        Place(
            SecondaryNativeLayer,
            ChromeText("المطلوب (الملخص)", 9, "#7A8390", FontWeights.SemiBold),
            265,
            583,
            104,
            18);
        var scope = ChromeText(
            "تحديث إطار الخصوصية وإدارة البيانات مع تطوير واجهات\nSmart Secretary V2 وتحسين تجربة المستخدم.",
            10.4,
            "#435064",
            FontWeights.SemiBold);
        scope.TextAlignment = TextAlignment.Right;
        scope.TextWrapping = TextWrapping.Wrap;
        scope.LineHeight = 19;
        Place(SecondaryNativeLayer, scope, 264, 607, 268, 55);

        var complete = ChromePanel("#F2FBF5", "#D3EEDA", 9);
        Place(SecondaryNativeLayer, complete, 259, 676, 282, 85);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#20B961"), IsHitTestVisible = false },
            272,
            688,
            25,
            25);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 13, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            279,
            691,
            13,
            17);
        Place(
            SecondaryNativeLayer,
            ChromeText("المكتمل", 11, "#1C8F4E", FontWeights.Bold),
            313,
            683,
            68,
            21);
        var completeText = ChromeText(
            "تم تنفيذ جميع المتطلبات وتسليم النظام المحدث بالكامل\nمع التوثيق والتدريب.",
            9.2,
            "#657469",
            FontWeights.SemiBold);
        completeText.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, completeText, 310, 712, 214, 36);

        var accepted = ChromePanel("#E9FFF0", "#BDE9C9", 9);
        Place(SecondaryNativeLayer, accepted, 259, 775, 282, 47);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 16, "#15984C", FontWeights.Bold, FlowDirection.LeftToRight),
            272,
            786,
            18,
            21);
        Place(
            SecondaryNativeLayer,
            ChromeText("تم اعتماد واستلام الأعمال", 10.5, "#177E45", FontWeights.Bold),
            303,
            782,
            183,
            23);
    }

    private void AddReceiptKeyValue(
        double left,
        double top,
        string label,
        string value)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 8.7, "#858C97", FontWeights.SemiBold),
            left,
            top,
            90,
            17);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 10.3, "#364255", FontWeights.SemiBold),
            left,
            top + 18,
            120,
            20);
    }

    private void BuildNativeFinalOutputs()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 567, 480, 528, 256);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#20BB62"), IsHitTestVisible = false },
            582,
            491,
            27,
            27);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 14, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            589,
            494,
            14,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("المخرجات النهائية", 16, "#273247", FontWeights.Bold),
            620,
            486,
            145,
            29);
        Place(
            SecondaryNativeLayer,
            ChromeText("4 ملفات رئيسية", 9, "#7A8391", FontWeights.SemiBold),
            778,
            491,
            90,
            21);
        var verified = ChromePanel("#E8F9ED", "#BDE8C8", 8);
        Place(SecondaryNativeLayer, verified, 981, 490, 92, 25);
        Place(
            SecondaryNativeLayer,
            ChromeText("● VERIFIED", 8, "#15964B", FontWeights.Bold, FlowDirection.LeftToRight),
            994,
            494,
            66,
            17);

        AddFinalArtifact(
            580,
            "واجهات النظام النهائية",
            "Figma · 56 شاشة",
            new Int32Rect(571, 513, 110, 83),
            "تنزيل");
        AddFinalArtifact(
            708,
            "التقرير النهائي",
            "PDF · 42 صفحة",
            new Int32Rect(706, 513, 100, 83),
            "تنزيل");
        AddFinalArtifact(
            836,
            "فيديو العرض النهائي",
            "MP4 · 6 دقائق",
            new Int32Rect(830, 513, 105, 83),
            "تنزيل");
        AddFinalArtifact(
            964,
            "عقد التسليم النهائي",
            "PDF · نسخة موقعة",
            new Int32Rect(954, 513, 105, 83),
            "تنزيل");
    }

    private void AddFinalArtifact(
        double left,
        string title,
        string meta,
        Int32Rect crop,
        string action)
    {
        var artifact = ChromePanel("#FFFDFCFB", "#E5E1DB", 9);
        Place(SecondaryNativeLayer, artifact, left, 524, 118, 199);

        var preview = CreateReferenceCrop(
            "08-project_complete_work_receipt.png",
            crop);
        Place(SecondaryNativeLayer, preview, left + 7, 533, 104, 78);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#22BE63"), IsHitTestVisible = false },
            left + 92,
            529,
            20,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 98,
            530,
            10,
            14);

        var titleText = ChromeText(title, 9.7, "#2F3A4C", FontWeights.Bold);
        titleText.TextAlignment = TextAlignment.Center;
        titleText.TextWrapping = TextWrapping.Wrap;
        Place(SecondaryNativeLayer, titleText, left + 7, 618, 104, 35);

        var metaText = ChromeText(meta, 8.2, "#78818D", FontWeights.SemiBold);
        metaText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, metaText, left + 8, 656, 102, 18);

        var button = ChromePanel("#FFFFFF", "#DFDCD7", 7);
        Place(SecondaryNativeLayer, button, left + 8, 683, 102, 27);
        var actionText = ChromeText(action + "  ↓", 8.7, "#495467", FontWeights.SemiBold);
        actionText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, actionText, left + 17, 660, 84, 18);
    }

    private void BuildNativeReceiptEvidence()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 11);
        Place(SecondaryNativeLayer, card, 1106, 480, 338, 370);

        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 19, "#19A854", FontWeights.Bold, FlowDirection.LeftToRight),
            1122,
            490,
            24,
            26);
        Place(
            SecondaryNativeLayer,
            ChromeText("الأدلة والشواهد", 16, "#273247", FontWeights.Bold),
            1152,
            486,
            145,
            29);
        Place(
            SecondaryNativeLayer,
            ChromeText("6 عناصر موثقة", 8.7, "#7B8491", FontWeights.SemiBold),
            1300,
            492,
            74,
            19);
        var verified = ChromePanel("#E8F9ED", "#BDE8C8", 8);
        Place(SecondaryNativeLayer, verified, 1357, 490, 72, 24);
        Place(
            SecondaryNativeLayer,
            ChromeText("VERIFIED", 7.5, "#15964B", FontWeights.Bold, FlowDirection.LeftToRight),
            1369,
            494,
            49,
            16);

        AddReceiptEvidenceRow(529, "▧", "#E64558", "نتائج الاختبارات النهائية", "PDF · 12 صفحة");
        AddReceiptEvidenceRow(574, "▧", "#E64558", "محضر القبول من المجلس", "PDF · 3 صفحات");
        AddReceiptEvidenceRow(619, "▤", "#20A85A", "سجلات الأداء والاختبارات", "CSV · 5 ميجابايت");
        AddReceiptEvidenceRow(664, "⌘", "#E9A32A", "صور من النظام المنتج", "ZIP · 28 ملف");
        AddReceiptEvidenceRow(709, "▶", "#8256E4", "تسجيل جلسة التسليم", "MP4 · 42 دقيقة");
        AddReceiptEvidenceRow(754, "▧", "#E64558", "التوصيات والاعتماد", "PDF · 2 صفحة");
    }

    private void AddReceiptEvidenceRow(
        double top,
        string glyph,
        string accent,
        string title,
        string meta)
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFDFCFB", "#ECE8E2", 6),
            1118,
            top,
            314,
            39);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 15, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            1128,
            top + 7,
            22,
            23);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 9.5, "#394557", FontWeights.SemiBold),
            1158,
            top + 2,
            167,
            19);
        Place(
            SecondaryNativeLayer,
            ChromeText(meta, 8.2, "#858C97"),
            1158,
            top + 19,
            142,
            16);
        var download = ChromePanel("#FFFFFF", "#E1DED8", 6);
        Place(SecondaryNativeLayer, download, 1350, top + 6, 67, 27);
        var downloadText = ChromeText("تحميل  ↓", 8.5, "#465366", FontWeights.SemiBold);
        downloadText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, downloadText, 1357, top + 10, 52, 18);
    }

    private void BuildNativeUsageSummary()
    {
        var card = ChromePanel("#FFFCFBF8", "#E3DED7", 10);
        Place(SecondaryNativeLayer, card, 567, 742, 528, 82);

        AddUsageMetric(578, 130, "استخدام الاستدلال", "68%", "متوازن", "◎", "#7654DD");
        AddUsageMetric(712, 130, "الأدوات المستخدمة", "8 أدوات", "Figma, …", "▦", "#5367DB");
        AddUsageMetric(846, 118, "الوقت الإجمالي", "25 يوماً", "600 ساعة عمل", "◷", "#4E66DA");
        AddUsageMetric(968, 114, "التكلفة والاستخدام", "$42.50", "1,250,000 توكن", "●", "#D98E26");
    }

    private void AddUsageMetric(
        double left,
        double width,
        string label,
        string value,
        string sub,
        string glyph,
        string accent)
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#F8F9FC", "#E4E1DC", 8),
            left,
            750,
            width,
            66);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 17, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 9,
            757,
            22,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 8.4, "#737D8A", FontWeights.SemiBold),
            left + 35,
            754,
            width - 45,
            17);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 15.5, "#1F2A3D", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 10,
            772,
            width - 20,
            21);
        Place(
            SecondaryNativeLayer,
            ChromeText(sub, 7.8, "#8A919C", FontWeights.SemiBold),
            left + 10,
            792,
            width - 20,
            15);
    }

    private void BuildNativeWorkReceiptBottomPanels()
    {
        AddBottomReceiptPanel(
            244,
            250,
            "#FFF8EF",
            "#E6A32A",
            "المشاكل التي تم تجاوزها نهائياً",
            "2 حالات",
            new[]
            {
                "بطء في استجابة واجهة فرعية — تم الحل",
                "تعارض في إطار الاختبارات — تم الحل",
            });

        AddBottomReceiptPanel(
            503,
            250,
            "#FFF9F0",
            "#D58E23",
            "خطط الرجوع (Fallbacks)",
            "2 خطط",
            new[]
            {
                "التحول إلى نموذج بديل — تم التفعيل",
                "استعادة نسخة مستقرة عند الحاجة",
            });

        AddBottomReceiptPanel(
            762,
            247,
            "#F3FBF5",
            "#1DA85A",
            "نقاط التحقق",
            "6 من 6",
            new[]
            {
                "مراجعة المتطلبات",
                "موافقة التصميم",
                "مراجعة الأمن والخصوصية",
                "اختبار شامل واعتماد نهائي",
            });

        AddBottomReceiptPanel(
            1018,
            220,
            "#F4F8FF",
            "#326ED4",
            "قرارات المجلس",
            "3 قرارات",
            new[]
            {
                "الموافقة على نطاق العمل",
                "الموافقة على التصميم النهائي",
                "اعتماد التسليم وإغلاق المشروع",
            });

        AddNextReceiptAction();
    }

    private void AddBottomReceiptPanel(
        double left,
        double width,
        string background,
        string accent,
        string title,
        string count,
        IReadOnlyList<string> items)
    {
        var card = ChromePanel(background, "#E3DED7", 10);
        Place(SecondaryNativeLayer, card, left, 838, width, 105);

        Place(
            SecondaryNativeLayer,
            ChromeText("◉", 15, accent, FontWeights.Bold, FlowDirection.LeftToRight),
            left + 12,
            850,
            20,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText(title, 10.8, "#2F3B4E", FontWeights.Bold),
            left + 40,
            845,
            width - 100,
            23);
        var countBadge = ChromePanel("#FFFFFF", "#E0DDD7", 7);
        Place(SecondaryNativeLayer, countBadge, left + width - 58, 848, 46, 22);
        var countText = ChromeText(count, 7.8, accent, FontWeights.SemiBold);
        countText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, countText, left + width - 54, 851, 38, 16);

        for (var index = 0; index < items.Count; index++)
        {
            var y = 878 + index * 18;
            Place(
                SecondaryNativeLayer,
                new Ellipse { Fill = Brush(accent), IsHitTestVisible = false },
                left + width - 23,
                y + 6,
                7,
                7);
            var text = ChromeText(items[index], 8.5, "#626D7B", FontWeights.SemiBold);
            text.TextAlignment = TextAlignment.Right;
            text.TextTrimming = TextTrimming.CharacterEllipsis;
            Place(SecondaryNativeLayer, text, left + 12, y, width - 43, 19);
        }
    }

    private void AddNextReceiptAction()
    {
        var card = ChromePanel("#F7F2FF", "#DCCFF2", 10);
        Place(SecondaryNativeLayer, card, 1247, 838, 197, 105);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#7A55DE"), IsHitTestVisible = false },
            1260,
            848,
            31,
            31);
        Place(
            SecondaryNativeLayer,
            ChromeText("✦", 16, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1268,
            852,
            17,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("الإجراء الموصى به الآن", 10.8, "#4B3A80", FontWeights.Bold),
            1301,
            846,
            130,
            24);

        var title = ChromeText("الانتقال إلى مرحلة التشغيل", 12.5, "#2D254E", FontWeights.Bold);
        title.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, title, 1260, 876, 171, 24);
        var sub = ChromeText("يوصى بالتشغيل ومراقبة الأداء والجودة", 8.5, "#716A84", FontWeights.SemiBold);
        sub.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, sub, 1260, 897, 171, 18);

        var primary = ChromePanel("#2875F2", "#2875F2", 7);
        Place(SecondaryNativeLayer, primary, 1260, 919, 171, 25);
        var primaryText = ChromeText("بدء التشغيل الآن  ←", 8.8, "#FFFFFF", FontWeights.SemiBold);
        primaryText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, primaryText, 1280, 923, 132, 17);

        var secondary = ChromePanel("#FFFFFF", "#DDD8D1", 7);
        Place(SecondaryNativeLayer, secondary, 1260, 946, 171, 17);
        var secondaryText = ChromeText("إنشاء مشروع متابعة", 8.5, "#4F5B6B", FontWeights.SemiBold);
        secondaryText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, secondaryText, 1280, 946, 132, 15);
    }

    private Image CreateReferenceCrop(
        string imageName,
        Int32Rect sourceRect,
        Stretch stretch = Stretch.UniformToFill)
    {
        var uri = new Uri(
            $"pack://application:,,,/UniversalCouncil.CommandCenter;component/Assets/VisualReferences/{imageName}",
            UriKind.Absolute);
        var source = new BitmapImage(uri);
        var cropped = new CroppedBitmap(source, sourceRect);
        return new Image
        {
            Source = cropped,
            Stretch = stretch,
            SnapsToDevicePixels = true,
            IsHitTestVisible = false,
        };
    }

    private void BuildNativeStudioHeaderAndPipeline()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFFDFBF8", "#F0EBE4", 0, new Thickness(0)),
            238,
            49,
            1232,
            66);

        Place(
            SecondaryNativeLayer,
            ChromeText("‹   مشاريع الفيديو", 11, "#6D7786", FontWeights.SemiBold),
            250,
            62,
            145,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("إطلاق هوية المجلس الجديدة", 27, "#101A2C", FontWeights.Bold),
            398,
            52,
            390,
            45);
        Place(
            SecondaryNativeLayer,
            ChromeText("✦", 29, "#2F8DFF", FontWeights.Bold, FlowDirection.LeftToRight),
            790,
            55,
            35,
            38);

        AddTagChipToCanvas(SecondaryNativeLayer, 833, 59, 116, "حملة متكاملة", "#F2EEFF", "#7555D0");
        AddTagChipToCanvas(SecondaryNativeLayer, 958, 59, 105, "فيديو رئيسي", "#F5F6F8", "#657083");

        var subtitle = ChromeText(
            "فيلم تعريفي يجسد رؤية المجلس\nلمستقبل أكثر ذكاءً وترابطاً",
            10.5,
            "#3E495A",
            FontWeights.SemiBold);
        subtitle.TextAlignment = TextAlignment.Right;
        Place(SecondaryNativeLayer, subtitle, 1170, 56, 235, 42);

        var pipeline = ChromePanel("#FFFCFBF8", "#E4E0DB", 13);
        Place(SecondaryNativeLayer, pipeline, 244, 116, 1200, 143);

        var connector = new Path
        {
            Data = Geometry.Parse("M 362,166 C 485,138 590,197 710,163 S 950,140 1070,165 S 1255,190 1360,165"),
            Stroke = Brush("#9C75EF"),
            StrokeThickness = 2.2,
            Opacity = 0.72,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(connector);

        AddStudioStage(332, 135, "1", "✎", "الكتابة", "السيناريو والنصوص", false);
        AddStudioStage(552, 135, "2", "▧", "ما قبل الإنتاج", "الستوري بورد والتخطيط", false);
        AddStudioStage(812, 126, "3", "▣", "الإنتاج", "التصوير والمونتاج", true);
        AddStudioStage(1032, 135, "4", "✓", "المراجعة والجودة", "المعاينة والملاحظات", false);
        AddStudioStage(1272, 135, "5", "➤", "التسليم والنشر", "التصدير والتوزيع", false);
    }

    private void AddTagChipToCanvas(
        Canvas canvas,
        double left,
        double top,
        double width,
        string text,
        string background,
        string foreground)
    {
        var chip = ChromePanel(background, "#E4E2DF", 9);
        Place(canvas, chip, left, top, width, 27);
        Place(
            canvas,
            ChromeText(text, 9.5, foreground, FontWeights.SemiBold),
            left + 10,
            top + 4,
            width - 20,
            19);
    }

    private void AddStudioStage(
        double left,
        double top,
        string number,
        string glyph,
        string title,
        string subtitle,
        bool active)
    {
        var ringSize = active ? 72 : 54;
        var ringLeft = left + (active ? -9 : 0);
        var ringTop = top + (active ? -9 : 0);

        if (active)
        {
            Place(
                SecondaryNativeLayer,
                new Ellipse
                {
                    Fill = Brush("#F4EAFF"),
                    Stroke = Brush("#BD92F7"),
                    StrokeThickness = 1,
                    IsHitTestVisible = false,
                },
                ringLeft - 8,
                ringTop - 8,
                ringSize + 16,
                ringSize + 16);
        }

        Place(
            SecondaryNativeLayer,
            new Ellipse
            {
                Fill = Brush(active ? "#8A4DE7" : "#F8F8F7"),
                Stroke = Brush(active ? "#8A4DE7" : "#D9D6D1"),
                StrokeThickness = active ? 2.5 : 1.5,
                IsHitTestVisible = false,
            },
            ringLeft,
            ringTop,
            ringSize,
            ringSize);
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, active ? 28 : 21, active ? "#FFFFFF" : "#7D8490", FontWeights.SemiBold, FlowDirection.LeftToRight),
            ringLeft + (active ? 21 : 15),
            ringTop + (active ? 16 : 12),
            32,
            32);

        var numberBadge = ChromePanel(active ? "#E4CCFF" : "#F0F0EE", active ? "#E4CCFF" : "#F0F0EE", 10);
        Place(SecondaryNativeLayer, numberBadge, left - 7, top + 58, 24, 24);
        Place(
            SecondaryNativeLayer,
            ChromeText(number, 9.5, active ? "#7041C7" : "#737B88", FontWeights.Bold, FlowDirection.LeftToRight),
            left + 1,
            top + 61,
            10,
            16);

        var titleText = ChromeText(title, 12.5, active ? "#7A45D1" : "#495566", active ? FontWeights.Bold : FontWeights.SemiBold);
        titleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, titleText, left - 38, top + 78, 130, 24);

        var subtitleText = ChromeText(subtitle, 9, active ? "#9A62DE" : "#7C8591");
        subtitleText.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, subtitleText, left - 53, top + 102, 160, 21);

        if (active)
        {
            var current = ChromePanel("#8A4DE7", "#8A4DE7", 8);
            Place(SecondaryNativeLayer, current, left - 6, top + 124, 88, 25);
            Place(
                SecondaryNativeLayer,
                ChromeText("القسم الحالي", 9, "#FFFFFF", FontWeights.SemiBold),
                left + 7,
                top + 128,
                63,
                17);
        }
    }

    private void BuildNativeStudioPlayerAndContext()
    {
        var projectInfo = ChromePanel("#FFFCFBF8", "#E5E0D8", 11);
        Place(SecondaryNativeLayer, projectInfo, 244, 270, 202, 310);
        Place(
            SecondaryNativeLayer,
            ChromeText("معلومات المشروع", 15.5, "#273247", FontWeights.SemiBold),
            260,
            280,
            150,
            28);
        AddStudioInfoRow(316, "كود المشروع", "UC-VID-2025-0043");
        AddStudioInfoRow(348, "العميل", "المجلس");
        AddStudioInfoRow(380, "النوع", "فيلم تعريفي");
        AddStudioInfoRow(412, "المدة المستهدفة", "90 ثانية");
        AddStudioInfoRow(444, "الحالة", "قيد الإنتاج");
        AddStudioInfoRow(476, "تاريخ التسليم", "30 أبريل 2025");
        Place(
            SecondaryNativeLayer,
            ChromeText("هوية   ذكاء اصطناعي   مستقبل", 9, "#5E6878", FontWeights.SemiBold),
            260,
            515,
            165,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("الإنجاز العام", 9.5, "#697383"),
            260,
            545,
            75,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("68%", 12, "#2C374A", FontWeights.Bold, FlowDirection.LeftToRight),
            396,
            545,
            35,
            20);
        var infoTrack = ChromePanel("#E3EAF3", "#E3EAF3", 4);
        Place(SecondaryNativeLayer, infoTrack, 260, 567, 166, 7);
        var infoFill = ChromePanel("#2F75F3", "#2F75F3", 4);
        Place(SecondaryNativeLayer, infoFill, 260, 567, 113, 7);

        // Player frame: media crop stays pixel-faithful to canonical reference.
        var player = ChromePanel("#111827", "#111827", 8);
        Place(SecondaryNativeLayer, player, 456, 270, 626, 310);

        var media = CreateReferenceCrop(
            "04-studio_project.png",
            new Int32Rect(465, 282, 608, 255));
        Place(SecondaryNativeLayer, media, 464, 278, 610, 252);

        Place(
            SecondaryNativeLayer,
            ChromePanel("#101827", "#101827", 0),
            464,
            530,
            610,
            42);
        Place(
            SecondaryNativeLayer,
            ChromeText("◀", 16, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            477,
            539,
            24,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("▶", 16, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            511,
            539,
            24,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("00:38 / 01:30", 10, "#FFFFFF", FontWeights.SemiBold, FlowDirection.LeftToRight),
            548,
            540,
            100,
            22);
        var seek = ChromePanel("#4A5363", "#4A5363", 2);
        Place(SecondaryNativeLayer, seek, 651, 549, 286, 4);
        var seekFill = ChromePanel("#A35CF2", "#A35CF2", 2);
        Place(SecondaryNativeLayer, seekFill, 651, 549, 133, 4);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#FFFFFF"), IsHitTestVisible = false },
            778,
            543,
            14,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("◖   ⛶   ↗", 16, "#FFFFFF", null, FlowDirection.LeftToRight),
            965,
            538,
            95,
            25);

        BuildStudioRightContext();
    }

    private void AddStudioInfoRow(double top, string label, string value)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 9.5, "#777F8B"),
            260,
            top,
            75,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 9.6, "#354052", FontWeights.SemiBold),
            337,
            top,
            90,
            20);
        Place(
            SecondaryNativeLayer,
            ChromePanel("#EEEAE4", "#EEEAE4", 0),
            260,
            top + 24,
            166,
            1);
    }

    private void BuildStudioRightContext()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFF9F7F2", "#F0EBE4", 0, new Thickness(0)),
            1088,
            265,
            360,
            320);

        var output = ChromePanel("#FFFCFBF8", "#E5E0D8", 10);
        Place(SecondaryNativeLayer, output, 1092, 270, 352, 116);
        Place(
            SecondaryNativeLayer,
            ChromeText("المخرج الحالي", 14.5, "#283347", FontWeights.SemiBold),
            1128,
            280,
            130,
            26);
        Place(
            SecondaryNativeLayer,
            ChromePanel("#EEE9FF", "#D8CAF6", 6),
            1107,
            310,
            112,
            58);
        var outputThumb = CreateReferenceCrop(
            "04-studio_project.png",
            new Int32Rect(1111, 316, 109, 61));
        Place(SecondaryNativeLayer, outputThumb, 1111, 314, 108, 58);
        Place(
            SecondaryNativeLayer,
            ChromeText("UC_Council_Main_v4.mp4", 10, "#2D394A", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1230,
            312,
            185,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("1.2 GB · 4K · 01:30", 9, "#6C7685", null, FlowDirection.LeftToRight),
            1230,
            337,
            160,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("● نسخة محدثة", 8.5, "#169A50", FontWeights.SemiBold),
            1230,
            357,
            95,
            17);

        var app = ChromePanel("#FFFCFBF8", "#E5E0D8", 10);
        Place(SecondaryNativeLayer, app, 1092, 395, 352, 92);
        Place(
            SecondaryNativeLayer,
            ChromeText("التطبيق الرئيسي", 13.5, "#283347", FontWeights.SemiBold),
            1128,
            405,
            130,
            24);
        var prBadge = ChromePanel("#2A1352", "#2A1352", 8);
        Place(SecondaryNativeLayer, prBadge, 1110, 436, 50, 40);
        Place(
            SecondaryNativeLayer,
            ChromeText("Pr", 18, "#D2A8FF", FontWeights.Bold, FlowDirection.LeftToRight),
            1123,
            443,
            25,
            25);
        Place(
            SecondaryNativeLayer,
            ChromeText("Adobe Premiere Pro", 10.5, "#303A4B", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1173,
            437,
            155,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("المونتاج النهائي والتنسيق اللوني", 8.5, "#727B88"),
            1173,
            457,
            190,
            17);

        var ai = ChromePanel("#FFFCFBF8", "#E5E0D8", 10);
        Place(SecondaryNativeLayer, ai, 1092, 496, 352, 84);
        Place(
            SecondaryNativeLayer,
            ChromeText("معلومات الذكاء الاصطناعي", 13, "#283347", FontWeights.SemiBold),
            1128,
            504,
            180,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("Claude 3.5 Sonnet   ·   عمق التفكير: متوسط", 9, "#475366", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1110,
            535,
            270,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("مدة التشغيل  02:14:37     القضايا المستعادة 3     دقة التحليل 92%", 8.5, "#6B7584"),
            1110,
            557,
            310,
            16);
    }

    private void BuildNativeStudioTimeline()
    {
        var timeline = ChromePanel("#FFFCFBF8", "#E5E0D8", 10);
        Place(SecondaryNativeLayer, timeline, 16, 590, 1027, 230);

        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#2F75F3"), IsHitTestVisible = false },
            34,
            602,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("▣", 10, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            40,
            604,
            12,
            14);
        Place(
            SecondaryNativeLayer,
            ChromeText("الخط الزمني", 15, "#283347", FontWeights.SemiBold),
            66,
            596,
            120,
            28);
        Place(
            SecondaryNativeLayer,
            ChromeText("01:30", 10.5, "#4D596A", FontWeights.SemiBold, FlowDirection.LeftToRight),
            159,
            600,
            55,
            20);

        AddTimelineRuler(124, 632, 900);
        AddStudioTrackLabel(28, 665, "▣", "الفيديو");
        AddStudioTrackLabel(28, 711, "◖", "الصوت");
        AddStudioTrackLabel(28, 757, "T", "النص");
        AddStudioTrackLabel(28, 791, "✦", "المؤثرات");

        for (var i = 0; i < 8; i++)
        {
            var clipColor = i % 3 == 0 ? "#CFE5FA" : i % 3 == 1 ? "#DCEAF6" : "#E8EDF4";
            var clip = ChromePanel(clipColor, "#BFD3E6", 4);
            Place(SecondaryNativeLayer, clip, 124 + (i * 108), 659, 101, 40);
            Place(
                SecondaryNativeLayer,
                ChromePanel("#87ADD1", "#87ADD1", 1),
                134 + (i * 108),
                670,
                70,
                4);
            Place(
                SecondaryNativeLayer,
                ChromePanel("#A9C4DE", "#A9C4DE", 1),
                134 + (i * 108),
                681,
                48,
                4);
        }

        var audioTrack = ChromePanel("#EAD9FA", "#D1B8ED", 4);
        Place(SecondaryNativeLayer, audioTrack, 124, 707, 864, 32);
        for (var i = 0; i < 27; i++)
        {
            var h = 6 + ((i * 7) % 19);
            Place(
                SecondaryNativeLayer,
                ChromePanel("#9E62D5", "#9E62D5", 1),
                133 + (i * 30),
                722 - (h / 2),
                3,
                h);
        }

        AddTimelineTextClip(174, 753, 214, "لمستقبل أكثر ذكاءً وترابطاً");
        AddTimelineTextClip(405, 753, 215, "المجلس");
        AddTimelineTextClip(637, 753, 214, "يبني جسوراً جديدة");
        AddTimelineTextClip(868, 753, 120, "مجتمع أكثر ازدهاراً");

        AddEffectClip(124, 788, 282);
        AddEffectClip(414, 788, 282);
        AddEffectClip(704, 788, 284);

        Place(
            SecondaryNativeLayer,
            ChromePanel("#2F75F3", "#2F75F3", 0),
            516,
            625,
            2,
            188);
        var playhead = ChromePanel("#2F75F3", "#2F75F3", 6);
        Place(SecondaryNativeLayer, playhead, 493, 624, 49, 22);
        Place(
            SecondaryNativeLayer,
            ChromeText("00:38", 8.5, "#FFFFFF", FontWeights.SemiBold, FlowDirection.LeftToRight),
            502,
            627,
            30,
            15);
    }

    private void AddTimelineRuler(double left, double top, double width)
    {
        var line = new Line
        {
            X1 = left,
            Y1 = top + 14,
            X2 = left + width,
            Y2 = top + 14,
            Stroke = Brush("#D9DEE6"),
            StrokeThickness = 1,
            IsHitTestVisible = false,
        };
        SecondaryNativeLayer.Children.Add(line);

        for (var i = 0; i <= 9; i++)
        {
            Place(
                SecondaryNativeLayer,
                ChromeText($"00:{i * 10:00}", 7.5, "#8B929D", null, FlowDirection.LeftToRight),
                left + (i * 100) - 12,
                top,
                38,
                15);
        }
    }

    private void AddStudioTrackLabel(double left, double top, string glyph, string label)
    {
        Place(
            SecondaryNativeLayer,
            ChromeText(glyph, 13, "#53627A", FontWeights.SemiBold, FlowDirection.LeftToRight),
            left,
            top,
            18,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 9.5, "#657083"),
            left + 25,
            top - 2,
            58,
            22);
    }

    private void AddTimelineTextClip(double left, double top, double width, string text)
    {
        var clip = ChromePanel("#E6ECFF", "#C8D5F5", 4);
        Place(SecondaryNativeLayer, clip, left, top, width, 27);
        var label = ChromeText(text, 8.5, "#43526D");
        label.TextAlignment = TextAlignment.Center;
        Place(SecondaryNativeLayer, label, left + 8, top + 4, width - 16, 18);
    }

    private void AddEffectClip(double left, double top, double width)
    {
        var clip = ChromePanel("#E2F7EC", "#C3EAD4", 4);
        Place(SecondaryNativeLayer, clip, left, top, width, 22);
        Place(
            SecondaryNativeLayer,
            ChromeText("◇", 10, "#2EB56B", FontWeights.Bold, FlowDirection.LeftToRight),
            left + (width / 2) - 7,
            top + 2,
            16,
            16);
    }

    private void BuildNativeStudioLowerWorkflow()
    {
        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFF9F7F2", "#F0EBE4", 0, new Thickness(0)),
            12,
            824,
            1436,
            139);

        Place(
            SecondaryNativeLayer,
            ChromePanel("#FFF9F7F2", "#F0EBE4", 0, new Thickness(0)),
            1048,
            585,
            400,
            239);

        var review = ChromePanel("#FFFCFBF8", "#E5E0D8", 9);
        Place(SecondaryNativeLayer, review, 16, 829, 290, 112);
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#EF596A"), IsHitTestVisible = false },
            32,
            842,
            22,
            22);
        Place(
            SecondaryNativeLayer,
            ChromeText("!", 12, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            40,
            843,
            10,
            16);
        Place(
            SecondaryNativeLayer,
            ChromeText("تذكرة المراجعة", 13.5, "#283347", FontWeights.SemiBold),
            64,
            837,
            130,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("TCK-1023", 10, "#4F5B6D", FontWeights.SemiBold, FlowDirection.LeftToRight),
            34,
            878,
            70,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("تعديل توازن الألوان في المشهد 3", 9, "#6C7685"),
            34,
            901,
            225,
            18);

        var handoff = ChromePanel("#FFFCFBF8", "#E5E0D8", 9);
        Place(SecondaryNativeLayer, handoff, 316, 829, 515, 112);
        Place(
            SecondaryNativeLayer,
            ChromeText("تدفق التسليم بين الأقسام", 13.5, "#283347", FontWeights.SemiBold),
            334,
            837,
            190,
            24);
        Place(
            SecondaryNativeLayer,
            ChromeText("▧  →  ▣  →  ◉  →  ◇  →  ➤", 27, "#8A5BE6", FontWeights.SemiBold, FlowDirection.LeftToRight),
            355,
            873,
            420,
            36);
        Place(
            SecondaryNativeLayer,
            ChromeText("الكتابة        ما قبل الإنتاج        الإنتاج        مراجعة الجودة        التسليم", 8.3, "#697383"),
            345,
            909,
            448,
            18);

        var team = ChromePanel("#FFFCFBF8", "#E5E0D8", 9);
        Place(SecondaryNativeLayer, team, 841, 829, 202, 112);
        Place(
            SecondaryNativeLayer,
            ChromeText("أعضاء الفريق النشطون", 12.5, "#283347", FontWeights.SemiBold),
            857,
            838,
            160,
            23);
        Place(
            SecondaryNativeLayer,
            ChromeText("● Pr   ● Ae   ● Ps   ✎", 18, "#6754C5", FontWeights.SemiBold, FlowDirection.LeftToRight),
            864,
            874,
            142,
            27);
        Place(
            SecondaryNativeLayer,
            ChromeText("خالد     سارة     أحمد     ريم", 8.3, "#687384"),
            858,
            905,
            155,
            18);

        var versions = ChromePanel("#FFFCFBF8", "#E5E0D8", 9);
        Place(SecondaryNativeLayer, versions, 1053, 590, 391, 155);
        Place(
            SecondaryNativeLayer,
            ChromeText("النسخ والبدائل", 14, "#283347", FontWeights.SemiBold),
            1090,
            600,
            120,
            25);
        for (var i = 0; i < 4; i++)
        {
            var bg = i == 0 ? "#F6EEFF" : "#F4F6F9";
            var border = i == 0 ? "#A66AE8" : "#DEE3EA";
            var thumb = ChromePanel(bg, border, 6);
            Place(SecondaryNativeLayer, thumb, 1070 + (i * 88), 634, 78, 72);

            var sourceX = 1074 + (i * 88);
            var versionCrop = CreateReferenceCrop(
                "04-studio_project.png",
                new Int32Rect(sourceX, 682, 74, 45));
            Place(SecondaryNativeLayer, versionCrop, 1072 + (i * 88), 636, 74, 45);

            Place(
                SecondaryNativeLayer,
                ChromeText(i == 0 ? "v4" : $"v{4 - i}", 9, i == 0 ? "#7D4ACD" : "#596476", FontWeights.Bold, FlowDirection.LeftToRight),
                1078 + (i * 88),
                683,
                22,
                16);
        }

        var qc = ChromePanel("#FFFCFBF8", "#E5E0D8", 9);
        Place(SecondaryNativeLayer, qc, 1053, 754, 190, 187);
        Place(
            SecondaryNativeLayer,
            ChromeText("مراجعة الجودة (QC)", 12.5, "#283347", FontWeights.SemiBold),
            1078,
            765,
            135,
            23);
        AddQcRow(802, "جودة الصورة", "4K ✓");
        AddQcRow(832, "جودة الصوت", "ممتاز");
        AddQcRow(862, "التناسق البصري", "✓");
        AddQcRow(892, "الالتزام بالهوية", "✓");

        var next = ChromePanel("#FFFCFBF8", "#E5E0D8", 9);
        Place(SecondaryNativeLayer, next, 1252, 754, 192, 187);
        Place(
            SecondaryNativeLayer,
            ChromeText("التسليم القادم", 12.5, "#283347", FontWeights.SemiBold),
            1280,
            765,
            120,
            23);
        Place(
            SecondaryNativeLayer,
            ChromeText("◈", 30, "#7A4EDC", FontWeights.Bold, FlowDirection.LeftToRight),
            1321,
            811,
            38,
            40);
        Place(
            SecondaryNativeLayer,
            ChromeText("مراجعة الجودة", 10.5, "#374254", FontWeights.SemiBold),
            1292,
            860,
            106,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText("فريق الجودة", 9, "#6D7786"),
            1299,
            883,
            90,
            18);
        Place(
            SecondaryNativeLayer,
            ChromeText("موعد متوقع: بعد 2 ساعة", 8.5, "#6D7786"),
            1278,
            914,
            130,
            16);
    }

    private void AddQcRow(double top, string label, string value)
    {
        Place(
            SecondaryNativeLayer,
            new Ellipse { Fill = Brush("#25C86A"), IsHitTestVisible = false },
            1068,
            top + 5,
            12,
            12);
        Place(
            SecondaryNativeLayer,
            ChromeText("✓", 8, "#FFFFFF", FontWeights.Bold, FlowDirection.LeftToRight),
            1071,
            top + 4,
            9,
            12);
        Place(
            SecondaryNativeLayer,
            ChromeText(label, 8.7, "#5F6A79"),
            1088,
            top,
            85,
            20);
        Place(
            SecondaryNativeLayer,
            ChromeText(value, 8.7, "#23975C", FontWeights.SemiBold, FlowDirection.LeftToRight),
            1174,
            top,
            54,
            20);
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

        BuildSecondarySharedInteractions(screen);
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
            e.Key == Key.O)
        {
            _nativeReferenceBlendEnabled = !_nativeReferenceBlendEnabled;
            if (_currentScreen == ScreenKind.Home)
            {
                NativeHomeReconstructionRoot.Opacity = _nativeReferenceBlendEnabled ? 0.46 : 1;
            }
            else
            {
                SecondaryNativeLayer.Opacity = _nativeReferenceBlendEnabled ? 0.46 : 1;
            }

            ShowNotice(
                _nativeReferenceBlendEnabled
                    ? $"وضع مقارنة Overlay مفعّل — {ScreenLabels[_currentScreen]}."
                    : $"وضع المقارنة متوقف — {ScreenLabels[_currentScreen]}.");
            e.Handled = true;
            return;
        }

        if (Keyboard.Modifiers == ModifierKeys.Control && e.Key == Key.K)
        {
            OpenGenericRegion(
                "البحث العام",
                "Ctrl+K",
                "واجهة البحث قابلة للفحص، لكن موفر البحث الفعلي غير متصل في الحالة الحاكمة الحالية.",
                "UNKNOWN / SEARCH PROVIDER NOT CONNECTED");
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
