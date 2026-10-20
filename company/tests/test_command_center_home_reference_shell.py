from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
XAML = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml"
CODE = ROOT / "apps" / "UniversalCouncil.CommandCenter" / "MainWindow.xaml.cs"
APP_ROOT = ROOT / "apps" / "UniversalCouncil.CommandCenter"
CSPROJ = APP_ROOT / "UniversalCouncil.CommandCenter.csproj"


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
