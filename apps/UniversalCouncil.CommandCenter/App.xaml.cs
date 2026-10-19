using System.Windows;
using UniversalCouncil.CommandCenter.Host;

namespace UniversalCouncil.CommandCenter;

public partial class App : System.Windows.Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);

        MainWindow = CreateMainWindow(AppContext.BaseDirectory);
        MainWindow.Show();
    }

    public static MainWindow CreateMainWindow(string baseDirectory)
    {
        var services = CommandCenterComposition.Create(baseDirectory);
        var viewModel = new MainWindowViewModel(
            services.Shell,
            services.Operational,
            services.Orchestration,
            services.ExecutionFabric,
            services.RemoteOwnerGateway);

        return new MainWindow(viewModel);
    }
}
