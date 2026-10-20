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
