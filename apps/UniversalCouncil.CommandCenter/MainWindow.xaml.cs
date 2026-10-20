using System.Windows;
using System.Windows.Automation;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Animation;
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
            ChromePanel("#FFFCF8F3", "#E5E0D8", 0, new Thickness(0, 0, 0, 1)),
            0,
            0,
            1536,
            49);

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

        var autoCard = ChromePanel("#FFFCFBF8", "#DDE2E7", 14);
        Place(NativeHomeChromeLayer, autoCard, 16, 62, 215, 159);
        Place(
            NativeHomeChromeLayer,
            new Ellipse { Fill = Brush("#24C85A"), IsHitTestVisible = false },
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
            ChromeText("يعمل الآن", 10, "#16A452", FontWeights.SemiBold),
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
        Place(NativeHomeChromeLayer, waveform, 46, 113, 150, 40);
        var autoMessage = ChromeText("لا يوجد شيء مطلوب\nمنك الآن", 11.5, "#485161", FontWeights.SemiBold);
        autoMessage.TextAlignment = TextAlignment.Center;
        Place(NativeHomeChromeLayer, autoMessage, 45, 158, 155, 48);
        Place(
            NativeHomeChromeLayer,
            ChromeText("›", 24, "#647083", null, FlowDirection.LeftToRight),
            199,
            75,
            20,
            30);
        AddChromeHotspot(16, 62, 215, 159, "autopilot", "Autopilot — يعمل الآن", NativeStatus_Click);

        AddNativeStatusCard(
            228,
            "3",
            "#2F75F3",
            "المشاريع النشطة",
            "جميع النظم تعمل بسلاسة",
            "projects");
        AddNativeStatusCard(
            316,
            "0",
            "#E7A629",
            "المهام بانتظارك",
            "لا توجد قرارات مطلوبة حالياً",
            "waiting");
        AddNativeStatusCard(
            404,
            "0",
            "#F06679",
            "تنبيهات مهمة",
            "كل شيء تحت السيطرة",
            "alerts");

        // Right global navigation rail.
        Place(
            NativeHomeChromeLayer,
            ChromePanel("#FFFCFBF8", "#E5E0D8", 0, new Thickness(1, 0, 0, 0)),
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
            new Ellipse { Fill = Brush("#28C767"), IsHitTestVisible = false },
            118,
            981,
            8,
            8);
        Place(
            NativeHomeChromeLayer,
            ChromeText("نشط الآن", 9, "#15974C"),
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
        var card = ChromePanel("#FFFCFBF8", "#E7E2DA", 12);
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
                    "REFERENCE FIXTURE");
                break;
            default:
                OpenGenericRegion(
                    "تنبيهات مهمة",
                    "Owner alerts",
                    "لا توجد تنبيهات حية مفترضة من المرجع؛ الحالة الفعلية تأتي من runtime.",
                    "REFERENCE FIXTURE");
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
            ChromeText("●  قيد التنفيذ", 10.5, "#1A9F52", FontWeights.SemiBold),
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
            ChromeText("يعمل الآن", 10, "#16A452", FontWeights.SemiBold),
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
            ChromeText("68%", 17, "#263247", FontWeights.Bold, FlowDirection.LeftToRight),
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
        Place(SecondaryNativeLayer, decision, 260, 760, 431, 250);
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
        Place(SecondaryNativeLayer, tools, 702, 760, 397, 250);
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
        Place(SecondaryNativeLayer, execution, 1110, 760, 334, 250);
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
            ChromeText("68%", 14, "#243049", FontWeights.Bold, FlowDirection.LeftToRight),
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
