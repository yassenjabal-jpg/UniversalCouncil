using System.Windows;
using UniversalCouncil.CommandCenter.Host;

namespace UniversalCouncil.CommandCenter;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();

        var services = CommandCenterComposition.Create(AppContext.BaseDirectory);
        DataContext = new MainWindowViewModel(
            services.Shell,
            services.Operational,
            services.Orchestration);
    }
}
