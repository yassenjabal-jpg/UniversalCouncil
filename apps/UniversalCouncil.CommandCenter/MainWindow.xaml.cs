using System.Windows;

namespace UniversalCouncil.CommandCenter;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        DataContext = new MainWindowViewModel(new PrototypeCommandCenterSnapshotProvider());
    }
}
