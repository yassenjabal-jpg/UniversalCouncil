using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;
using System.Windows.Media.Animation;

namespace UniversalCouncil.CommandCenter;

public partial class MainWindow : Window
{
    private readonly MainWindowViewModel _viewModel;
    private FrameworkElement? _lastInteractionTarget;
    private string? _activeRoleId;

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
                "UNKNOWN.")
        };

    internal MainWindow(MainWindowViewModel viewModel)
    {
        _viewModel = viewModel;
        InitializeComponent();
        DataContext = viewModel;
    }

    private void Role_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string roleId)
        {
            return;
        }

        if (!Roles.TryGetValue(roleId, out var role))
        {
            return;
        }

        _activeRoleId = roleId;
        _lastInteractionTarget = button;
        ShowRoleActivation(button);
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

    private void Reasoning_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string roleId)
        {
            return;
        }

        if (!Roles.TryGetValue(roleId, out var role))
        {
            return;
        }

        _activeRoleId = roleId;
        _lastInteractionTarget = button;
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

    private void Route_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string route)
        {
            return;
        }

        _lastInteractionTarget = button;

        var (title, subtitle, explanation) = route switch
        {
            "council-route" => (
                "المجلس",
                "تحليل ومراجعة متعددة الأدوار",
                "هذا الاختيار يحدد مسار العمل دلاليًا؛ لا يفعّل صلاحية تنفيذ حي."),
            "studio-route" => (
                "الاستوديو",
                "إنتاج وتصميم متعدد المراحل",
                "هذا الاختيار يحدد مسار الاستوديو ولا يشغّل أداة خارجية تلقائيًا."),
            _ => (
                "التنفيذ التلقائي",
                "من الفكرة إلى الإنجاز عبر مسار محكوم",
                "Auto لا يمنح صلاحية تنفيذ حي؛ التنفيذ يبقى خاضعًا للسلطة والحالة.")
        };

        OpenDrawer(
            "ROUTING",
            title,
            subtitle,
            explanation,
            "بانتظار أمر مالك صريح وسياق مشروع صالح.",
            _viewModel.ExecutionFabric.LiveDispatchEnabled ? "LIVE DISPATCH ENABLED" : "LIVE DISPATCH DISABLED",
            "يعرض المسار المقترح فقط؛ لا توجد خطوة نفذت من هذا الاختيار.",
            "أي blocker أو authority gate يجب أن يظهر قبل البدء.",
            "لا توجد أدلة تشغيلية مرتبطة بالاختيار بعد.",
            $"Fallback: {_viewModel.ModelFallbackLabel}");
    }

    private void Project_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string projectId)
        {
            return;
        }

        _lastInteractionTarget = button;

        var (title, subtitle) = projectId switch
        {
            "smart-secretary" => ("Smart Secretary V2", "Project Context"),
            "privacy" => ("M2-A: Privacy", "Project Context"),
            _ => ("Erasure Contract", "Project Context")
        };

        OpenDrawer(
            "PROJECT CONTEXT",
            title,
            subtitle,
            "يفتح Living Project Workspace مع الحفاظ على سياق المشروع.",
            "هذه بطاقة مرجعية ضمن Home؛ الربط بمشروع حي يتم عندما تتوفر هوية مشروع فعلية.",
            "REFERENCE FIXTURE",
            "لا يتم اعتبار النسب أو حالات VERIFIED داخل الصورة حقائق تشغيلية.",
            "الاعتراضات تظهر من Decision / Red Team context عند توفرها.",
            "الأدلة ستُفتح من Filmstrip / Evidence Peek في Project Workspace.",
            "Model / Reasoning: UNKNOWN حتى وصول state فعلي.");
    }

    private void Region_Click(object sender, RoutedEventArgs e)
    {
        if (sender is not Button button || button.Tag is not string regionId)
        {
            return;
        }

        _lastInteractionTarget = button;

        var data = regionId switch
        {
            "autopilot" => new RegionContext(
                "Autopilot",
                "الحالة التشغيلية",
                "يفتح Live Execution Detail عندما توجد حالة تشغيل حقيقية.",
                _viewModel.ExecutionFabric.LiveDispatchEnabled ? "LIVE DISPATCH ENABLED" : "LIVE DISPATCH DISABLED"),
            "since-away" => new RegionContext(
                "منذ آخر زيارة",
                "التحديثات ذات القيمة",
                "ملخص زمني يحافظ على المشروع والمصدر عند فتح التفاصيل.",
                "REFERENCE FIXTURE"),
            "needs-decision" => new RegionContext(
                "يحتاج قرارك",
                "Owner Decision Inbox",
                "كل عنصر يجب أن يوضح لماذا يحتاج قرارك وأثر كل اختيار.",
                "REFERENCE FIXTURE"),
            "recent-results" => new RegionContext(
                "النتائج الأخيرة",
                "Recent Results",
                "VERIFIED لا يصبح حقيقة إلا عند وجود evidence-backed state.",
                "REFERENCE FIXTURE"),
            "tool-dock" => new RegionContext(
                "Tool Dock",
                "الأدوات",
                "يفرق بين READY / ACTIVE / BLOCKED / UNKNOWN ويفتح Tool Inspector.",
                _viewModel.ExecutionFabric.LiveDispatchEnabled ? "LIVE DISPATCH ENABLED" : "LIVE DISPATCH DISABLED"),
            _ => new RegionContext(
                "التنقل العام",
                "Command Center Navigation",
                "يحفظ السياق الحالي عند الانتقال إلى وجهة أخرى.",
                "UI INTERACTION LAYER")
        };

        OpenDrawer(
            "SEMANTIC REGION",
            data.Title,
            data.Subtitle,
            data.Explanation,
            "لا توجد مهمة مستقلة داخل هذا العنصر الآن.",
            data.State,
            "تم تفعيل المسار التفاعلي فقط.",
            "لا يوجد اعتراض مرتبط بهذه المنطقة.",
            "Evidence available only when supplied by the underlying state.",
            "N/A");
    }

    private void Start_Click(object sender, RoutedEventArgs e)
    {
        _lastInteractionTarget = sender as FrameworkElement;
        ShowNotice("التنفيذ الحي غير مفعل من Home البصرية. تم اختبار press/feedback فقط بدون إرسال أي أمر.");
    }

    private void AskThis_Click(object sender, RoutedEventArgs e)
    {
        var context = _activeRoleId is not null && Roles.TryGetValue(_activeRoleId, out var role)
            ? role.Title
            : DrawerTitle.Text;
        ShowNotice($"Ask This سيحمل السياق تلقائيًا: {context}. لا توجد محادثة runtime مربوطة بعد.");
    }

    private void OpenEvidence_Click(object sender, RoutedEventArgs e) =>
        ShowNotice("Evidence Peek جاهز دلاليًا، لكن لا توجد أدلة حية متصلة بهذا العنصر الآن.");

    private void ReasoningInspector_Click(object sender, RoutedEventArgs e)
    {
        if (_activeRoleId is not null && Roles.TryGetValue(_activeRoleId, out var role))
        {
            OpenDrawer(
                "MODEL & REASONING",
                role.Title,
                role.Subtitle,
                "يفتح تفاصيل النموذج والاستدلال عند توفرها.",
                "لا توجد مهمة runtime حية مرتبطة بهذه الشاشة.",
                "UNKNOWN",
                $"Provider connection: {_viewModel.ProviderConnectionLabel}",
                "لا يتم اختلاق effort أو fallback.",
                "Usage / cost غير متاح الآن.",
                "Model: UNKNOWN\nEffort: UNKNOWN\nFallback: " + _viewModel.ModelFallbackLabel);
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
            ContextDrawer.Visibility = Visibility.Collapsed;
            ContextDrawer.Opacity = 0;
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
            ContextDrawer.Visibility = Visibility.Collapsed;
            ContextDrawer.Opacity = 0;
            DrawerTransform.X = 430;
            RestoreInteractionFocus();
        };

        DrawerTransform.BeginAnimation(System.Windows.Media.TranslateTransform.XProperty, slide);
        ContextDrawer.BeginAnimation(
            OpacityProperty,
            new DoubleAnimation(1, 0, TimeSpan.FromMilliseconds(150)));
    }

    private void RestoreInteractionFocus()
    {
        _lastInteractionTarget?.Focus();
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
