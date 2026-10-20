from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XAML = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml"
CODE = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
APP_ROOT = ROOT / "apps" / "UniversalCouncil.CommandCenter"
CSPROJ = APP_ROOT / "UniversalCouncil.CommandCenter.csproj"
UISMOKE = APP_ROOT.parent / "UniversalCouncil.CommandCenter.UiSmoke" / "Program.cs"


def test_home_uses_canonical_reference_as_visual_shell():
    xaml = XAML.read_text(encoding="utf-8")
    assert "01-home_owner_workspace.png" in xaml
    assert "Assets/VisualReferences" in xaml


def test_home_has_exact_eight_role_interaction_targets():
    xaml = XAML.read_text(encoding="utf-8")
    assert xaml.count('Click="Role_Click"') == 8
    for role in (
        "owner",
        "strategy",
        "research",
        "verification",
        "execution",
        "creative",
        "data",
        "learning",
    ):
        assert f'Tag="{role}"' in xaml


def test_reasoning_and_context_interactions_are_present():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    assert xaml.count('Click="Reasoning_Click"') == 8
    assert 'x:Name="ContextDrawer"' in xaml
    assert "Model &amp; Reasoning Inspector" in xaml
    assert "SystemParameters.ClientAreaAnimation" in code
    assert "AskThis_Click" in code
    assert "OpenEvidence_Click" in code


def test_reference_asset_is_embedded_in_wpf_project():
    project = CSPROJ.read_text(encoding="utf-8")
    assert "01-home_owner_workspace.png" in project
    assert "Assets\\VisualReferences\\01-home_owner_workspace.png" in project


def test_all_eight_canonical_screens_are_embedded_and_mapped():
    project = CSPROJ.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    references = (
        "01-home_owner_workspace.png",
        "02-living_project_workspace.png",
        "03-software_autopilot_project.png",
        "04-studio_project.png",
        "05-owner_decision_mode.png",
        "06-checkpoint_recovery_fork.png",
        "07-pulse_visual_project_story.png",
        "08-project_complete_work_receipt.png",
    )
    for reference in references:
        assert reference in project
        assert reference in code


def test_secondary_screens_use_native_semantic_overlay():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    assert 'x:Name="SecondaryInteractionCanvas"' in xaml
    assert "BuildSecondaryInteractions" in code
    assert "OpenVersionInspector" in code
    assert "HandleDecisionAction" in code
    assert "HandleRecoveryAction" in code
    assert "OpenArtifact" in code
    assert "OpenStageDetail" in code
    assert "OpenPulseDetail" in code


def test_navigation_preserves_reference_screen_family():
    code = CODE.read_text(encoding="utf-8")
    for screen in (
        "ProjectWorkspace",
        "SoftwareAutopilot",
        "StudioProject",
        "DecisionMode",
        "RecoveryFork",
        "PulseStory",
        "WorkReceipt",
    ):
        assert f"ScreenKind.{screen}" in code
    assert "Ctrl+1" not in code
    assert "Key.D1" in code
    assert "Key.D8" in code


def test_interactions_remain_truthful_and_reduced_motion_aware():
    code = CODE.read_text(encoding="utf-8")
    assert "LIVE DISPATCH DISABLED" in code
    assert "CHECKPOINT_RESTORED_VERIFIED" in code
    assert "لم يتم تسجيل قرار" in code
    assert "SystemParameters.ClientAreaAnimation" in code


def test_home_council_pulse_has_first_native_reconstruction_slice():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    assert 'x:Name="NativeHomeLayer"' in xaml
    assert "NativeRoleButtonStyle" in xaml
    assert xaml.count('Click="NativeRole_Click"') == 8
    assert xaml.count('Click="NativeReasoning_Click"') == 8
    assert "CouncilActivity_Click" in code
    assert "AnimateNativeRoleButton" in code


def test_native_reference_overlay_comparison_is_keyboard_gated():
    code = CODE.read_text(encoding="utf-8")
    assert "_nativeReferenceBlendEnabled" in code
    assert "ModifierKeys.Shift" in code
    assert "Key.O" in code
    assert "NativeHomeLayer.Opacity" in code
    assert "0.46" in code


def test_native_home_canvas_uses_ltr_coordinates_inside_rtl_window():
    xaml = XAML.read_text(encoding="utf-8")
    marker = 'x:Name="NativeHomeLayer"'
    start = xaml.index(marker)
    fragment = xaml[start : start + 260]
    assert 'FlowDirection="LeftToRight"' in fragment


def test_ui_smoke_emits_reference_native_and_blend_evidence():
    smoke = UISMOKE.read_text(encoding="utf-8")
    assert "home-reference-only-1440x900.png" in smoke
    assert "home-native-overlay-1440x900.png" in smoke
    assert 'case "reference"' in smoke
    assert 'case "blend"' in smoke
    assert "nativeHomeLayer.Opacity = 0.46" in smoke


def test_native_pulse_has_overlay_calibrated_translation():
    xaml = XAML.read_text(encoding="utf-8")
    marker = 'x:Name="NativeHomeLayer"'
    start = xaml.index(marker)
    fragment = xaml[start : start + 520]
    assert '<TranslateTransform Y="23" />' in fragment


def test_home_command_composer_is_native_and_editable():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    assert 'x:Name="NativeHomeReconstructionRoot"' in xaml
    assert 'x:Name="NativeHomeComposerLayer"' in xaml
    assert 'x:Name="OwnerPromptBox"' in xaml
    assert xaml.count('Style="{StaticResource NativeComposerRouteStyle}"') == 3
    assert "ComposerControl_Click" in code
    assert "OwnerPromptBox_GotKeyboardFocus" in code
    assert "OwnerPromptBox_LostKeyboardFocus" in code


def test_ui_smoke_toggles_complete_native_home_root():
    smoke = UISMOKE.read_text(encoding="utf-8")
    assert 'FindName("NativeHomeReconstructionRoot")' in smoke


def test_native_composer_has_overlay_calibrated_translation():
    xaml = XAML.read_text(encoding="utf-8")
    marker = 'x:Name="NativeHomeComposerLayer"'
    start = xaml.index(marker)
    fragment = xaml[start : start + 520]
    assert '<TranslateTransform Y="10" />' in fragment


def test_home_active_work_cards_are_native_and_navigable():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    assert 'x:Name="NativeHomeActiveWorkLayer"' in xaml
    assert "NativeProjectCardStyle" in xaml
    assert xaml.count('Style="{StaticResource NativeProjectCardStyle}"') == 3
    for project in ("smart-secretary", "privacy", "erasure"):
        assert f'Tag="{project}"' in xaml
    assert 'Click="ShowAllProjects_Click"' in xaml
    assert "ShowAllProjects_Click" in code


def test_home_owner_summary_panels_are_native_and_interactive():
    xaml = XAML.read_text(encoding="utf-8")
    assert 'x:Name="NativeHomeOwnerSummaryLayer"' in xaml
    for region in ("since-away", "needs-decision", "recent-results"):
        assert f'Tag="{region}"' in xaml
    assert xaml.count('AutomationProperties.Name="منذ آخر زيارة"') >= 1
    assert xaml.count('AutomationProperties.Name="يحتاج قرارك"') >= 1
    assert xaml.count('AutomationProperties.Name="النتائج الأخيرة"') >= 1


def test_native_summary_panels_cover_full_reference_height():
    xaml = XAML.read_text(encoding="utf-8")
    marker = 'x:Name="NativeHomeOwnerSummaryLayer"'
    start = xaml.index(marker)
    fragment = xaml[start : start + 22000]
    assert 'Width="257" Height="215"' in fragment
    assert 'Width="503" Height="215"' in fragment
    assert 'Width="439" Height="215"' in fragment


def test_home_remaining_chrome_is_native_wpf():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    assert 'x:Name="NativeHomeChromeLayer"' in xaml
    assert "BuildNativeHomeChrome" in code
    assert "AddNativeStatusCard" in code
    assert "AddNativeNavItem" in code
    assert "AddDockChip" in code
    assert "NativeStatus_Click" in code
    assert "NativeHomeNav_Click" in code
    assert "NativeDockTool_Click" in code


def test_home_native_chrome_preserves_canonical_identity_and_regions():
    code = CODE.read_text(encoding="utf-8")
    for value in (
        "UniversalCouncil",
        "Command Center",
        "ماذا تريد أن تنجز؟",
        "Autopilot",
        "المشاريع النشطة",
        "المهام بانتظارك",
        "تنبيهات مهمة",
        "الرئيسية",
        "المشاريع",
        "المجلس",
        "الاستوديو",
        "المعرفة",
        "الأدوات",
        "التقارير",
        "الإعدادات",
        "GitHub",
        "Photoshop",
        "After Effects",
        "Premiere",
        "YASSIN",
        "Tailscale",
        "Models",
        "Evidence",
        "Android Owner",
    ):
        assert value in code


def test_project_workspace_has_native_core_reconstruction():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    assert 'x:Name="SecondaryNativeLayer"' in xaml
    assert "BuildSecondaryNative" in code
    assert "BuildNativeProjectWorkspaceCore" in code
    assert "AddTimelineNode" in code
    assert "AddProjectCouncilRole" in code
    assert "Smart Secretary V2" in code
    for role in ("Evidence", "UX", "Red Team", "Studio", "Security", "Synthesis"):
        assert role in code


def test_home_macro_native_reconstruction_regions_are_all_present():
    xaml = XAML.read_text(encoding="utf-8")
    code = CODE.read_text(encoding="utf-8")
    for marker in (
        'x:Name="NativeHomeLayer"',
        'x:Name="NativeHomeComposerLayer"',
        'x:Name="NativeHomeActiveWorkLayer"',
        'x:Name="NativeHomeOwnerSummaryLayer"',
        'x:Name="NativeHomeChromeLayer"',
    ):
        assert marker in xaml
    assert "BuildNativeHomeChrome" in code


def test_project_workspace_native_reconstruction_covers_full_reference_structure():
    code = CODE.read_text(encoding="utf-8")
    for method in (
        "BuildNativeProjectWorkspaceLeftRail",
        "BuildNativeProjectWorkspaceFilmstrip",
        "BuildNativeProjectWorkspaceBottomPanels",
        "AddProjectRailItem",
        "AddVersionCard",
        "AddDecisionRow",
        "AddActiveToolTile",
        "AddExecutionRow",
    ):
        assert method in code
    for content in (
        "نظرة عامة على المشروع",
        "أهداف المشروع",
        "حالة المشروع",
        "شريط إصدارات المشروع",
        "Decision Stack",
        "الأدوات النشطة في هذا المشروع",
        "معلومات التنفيذ الحالية",
    ):
        assert content in code


def test_project_workspace_bottom_panels_cover_reference_to_lower_edge():
    code = CODE.read_text(encoding="utf-8")
    assert "decision, 260, 760, 431, 250" in code
    assert "tools, 702, 760, 397, 250" in code
    assert "execution, 1110, 760, 334, 250" in code


def test_software_autopilot_has_native_checkpoint_branch_and_history_reconstruction():
    code = CODE.read_text(encoding="utf-8")
    for method in (
        "BuildNativeSoftwareAutopilot",
        "BuildNativeAutopilotHeader",
        "BuildNativeAutopilotTimeline",
        "BuildNativeAutopilotDiffAndBranches",
        "BuildNativeAutopilotHistory",
        "AddCheckpointNode",
        "AddBranchScorecard",
        "AddOwnerBranchChoice",
        "AddHistoryFrame",
    ):
        assert method in code
    for content in (
        "Memory Fabric Repair",
        "Checkpoint",
        "Branch A",
        "Branch B",
        "مقارنة التغييرات",
        "قرار المالك",
        "تاريخ المشروع",
    ):
        assert content in code


def test_studio_project_has_native_pipeline_player_timeline_and_handoff():
    code = CODE.read_text(encoding="utf-8")
    for method in (
        "BuildNativeStudioProject",
        "BuildNativeStudioHeaderAndPipeline",
        "BuildNativeStudioPlayerAndContext",
        "BuildNativeStudioTimeline",
        "BuildNativeStudioLowerWorkflow",
        "CreateReferenceCrop",
        "AddStudioStage",
        "AddStudioTrackLabel",
        "AddTimelineTextClip",
        "AddEffectClip",
        "AddQcRow",
    ):
        assert method in code
    for content in (
        "إطلاق هوية المجلس الجديدة",
        "الكتابة",
        "ما قبل الإنتاج",
        "الإنتاج",
        "المراجعة والجودة",
        "التسليم والنشر",
        "Adobe Premiere Pro",
        "مراجعة الجودة (QC)",
        "تدفق التسليم بين الأقسام",
    ):
        assert content in code


def test_studio_player_media_uses_canonical_reference_crop_not_generated_media():
    code = CODE.read_text(encoding="utf-8")
    assert '"04-studio_project.png"' in code
    assert "new Int32Rect(465, 282, 608, 255)" in code
    assert "CroppedBitmap" in code


def test_owner_decision_mode_has_native_reconstruction():
    code = CODE.read_text(encoding="utf-8")
    assert "BuildNativeOwnerDecision" in code
    assert "BuildNativeDecisionSurface" in code
    assert "BuildNativeDecisionRolesAndRouting" in code
    assert "BuildNativeDecisionEvidencePeek" in code
    assert "BuildNativeDecisionActions" in code
    for role in ("الأدلة", "الفريق المعارض", "المركزي", "تجربة المستخدم", "الأمن والخصوصية"):
        assert role in code
    for action in ("الموافقة", "طلب تعديلات", "رفض", "طرح سؤال", "فحص الأدلة"):
        assert action in code


def test_owner_decision_keeps_dissent_evidence_and_impacts_visible():
    code = CODE.read_text(encoding="utf-8")
    for value in (
        "مسار الاعتراض",
        "أقوى اعتراض",
        "ملخص الأدلة",
        "أثر الموافقة",
        "أثر الرفض",
        "معاينة دليل",
        "VERIFIED",
    ):
        assert value in code


def test_owner_decision_native_vertical_calibration_matches_reference_bands():
    code = CODE.read_text(encoding="utf-8")
    assert 'Place(SecondaryNativeLayer, surface, 400, 155, 735, 785);' in code
    assert 'Place(SecondaryNativeLayer, dock, 381, 941, 796, 70);' in code
    assert 'Place(SecondaryNativeLayer, group, 32, 610, 325, 322);' in code
    assert 'AddDecisionRole(146, 388, 112' in code
    assert 'AddDecisionRole(1269, 391, 106' in code
