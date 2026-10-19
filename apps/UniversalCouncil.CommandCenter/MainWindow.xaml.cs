using System.Windows;

namespace UniversalCouncil.CommandCenter;

public partial class MainWindow : Window
{
    internal MainWindow(MainWindowViewModel viewModel)
    {
        InitializeComponent();
        DataContext = viewModel;
    }
}
