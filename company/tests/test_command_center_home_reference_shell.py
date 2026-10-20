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
