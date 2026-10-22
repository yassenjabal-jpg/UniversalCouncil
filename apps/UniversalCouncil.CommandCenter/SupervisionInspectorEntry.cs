using System.Windows;
using System.Windows.Controls;
using System.Windows.Input;

namespace UniversalCouncil.CommandCenter;

internal static class SupervisionInspectorEntry
{
    public static void Install(Window owner)
    {
        SupervisionInspectorWindow? inspector = null;
        void Open()
        {
            if (inspector is not null) { inspector.Activate(); return; }
            inspector = new SupervisionInspectorWindow { Owner = owner };
            inspector.Closed += (_, _) => inspector = null;
            inspector.Show();
        }
        var command = new RoutedCommand();
        owner.CommandBindings.Add(new CommandBinding(command, (_, _) => Open()));
        owner.InputBindings.Add(new KeyBinding(command, Key.R, ModifierKeys.Control | ModifierKeys.Shift));
        owner.ContextMenu ??= new ContextMenu();
        var item = new MenuItem { Header = "فحص جلسة المراجعة", InputGestureText = "Ctrl+Shift+R", Command = command, CommandTarget = owner };
        owner.ContextMenu.Items.Add(item);
    }
}
