using System.Runtime.InteropServices;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal sealed record WgcHostGeometryDiagnostics(
    int? WindowLeft,
    int? WindowTop,
    int? WindowWidth,
    int? WindowHeight,
    int? ClientWidth,
    int? ClientHeight,
    uint? WindowDpi,
    double? DpiScale,
    int PrimaryScreenWidth,
    int PrimaryScreenHeight,
    int VirtualScreenWidth,
    int VirtualScreenHeight,
    int? MonitorWidth,
    int? MonitorHeight,
    int? MonitorWorkAreaWidth,
    int? MonitorWorkAreaHeight,
    string? DiagnosticError);

internal static class WgcHostGeometryProbe
{
    [StructLayout(LayoutKind.Sequential)]
    private struct NativeRect
    {
        internal int Left;
        internal int Top;
        internal int Right;
        internal int Bottom;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Auto)]
    private struct MonitorInfo
    {
        internal uint Size;
        internal NativeRect Monitor;
        internal NativeRect WorkArea;
        internal uint Flags;
    }

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetWindowRect(
        IntPtr window,
        out NativeRect rectangle);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetClientRect(
        IntPtr window,
        out NativeRect rectangle);

    [DllImport("user32.dll")]
    private static extern uint GetDpiForWindow(IntPtr window);

    [DllImport("user32.dll")]
    private static extern IntPtr MonitorFromWindow(
        IntPtr window,
        uint flags);

    [DllImport("user32.dll", CharSet = CharSet.Auto, SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetMonitorInfo(
        IntPtr monitor,
        ref MonitorInfo info);

    [DllImport("user32.dll")]
    private static extern int GetSystemMetrics(int index);

    private const uint MonitorDefaultToNearest = 2;
    private const int SmCxScreen = 0;
    private const int SmCyScreen = 1;
    private const int SmCxVirtualScreen = 78;
    private const int SmCyVirtualScreen = 79;

    internal static WgcHostGeometryDiagnostics Capture(IntPtr window)
    {
        if (window == IntPtr.Zero)
        {
            return new WgcHostGeometryDiagnostics(
                null, null, null, null,
                null, null, null, null,
                GetSystemMetrics(SmCxScreen),
                GetSystemMetrics(SmCyScreen),
                GetSystemMetrics(SmCxVirtualScreen),
                GetSystemMetrics(SmCyVirtualScreen),
                null, null, null, null,
                "HWND_ZERO");
        }

        string? diagnosticError = null;

        int? windowLeft = null;
        int? windowTop = null;
        int? windowWidth = null;
        int? windowHeight = null;
        if (GetWindowRect(window, out var windowRect))
        {
            windowLeft = windowRect.Left;
            windowTop = windowRect.Top;
            windowWidth = windowRect.Right - windowRect.Left;
            windowHeight = windowRect.Bottom - windowRect.Top;
        }
        else
        {
            diagnosticError =
                $"GetWindowRect:{Marshal.GetLastWin32Error()}";
        }

        int? clientWidth = null;
        int? clientHeight = null;
        if (GetClientRect(window, out var clientRect))
        {
            clientWidth = clientRect.Right - clientRect.Left;
            clientHeight = clientRect.Bottom - clientRect.Top;
        }
        else
        {
            diagnosticError = AppendError(
                diagnosticError,
                $"GetClientRect:{Marshal.GetLastWin32Error()}");
        }

        uint? dpi = null;
        double? dpiScale = null;
        var windowDpi = GetDpiForWindow(window);
        if (windowDpi > 0)
        {
            dpi = windowDpi;
            dpiScale = Math.Round(windowDpi / 96d, 4);
        }
        else
        {
            diagnosticError = AppendError(
                diagnosticError,
                "GetDpiForWindow:0");
        }

        int? monitorWidth = null;
        int? monitorHeight = null;
        int? workAreaWidth = null;
        int? workAreaHeight = null;
        var monitor = MonitorFromWindow(
            window,
            MonitorDefaultToNearest);
        if (monitor != IntPtr.Zero)
        {
            var info = new MonitorInfo
            {
                Size = (uint)Marshal.SizeOf<MonitorInfo>(),
            };

            if (GetMonitorInfo(monitor, ref info))
            {
                monitorWidth =
                    info.Monitor.Right - info.Monitor.Left;
                monitorHeight =
                    info.Monitor.Bottom - info.Monitor.Top;
                workAreaWidth =
                    info.WorkArea.Right - info.WorkArea.Left;
                workAreaHeight =
                    info.WorkArea.Bottom - info.WorkArea.Top;
            }
            else
            {
                diagnosticError = AppendError(
                    diagnosticError,
                    $"GetMonitorInfo:{Marshal.GetLastWin32Error()}");
            }
        }
        else
        {
            diagnosticError = AppendError(
                diagnosticError,
                "MonitorFromWindow:0");
        }

        return new WgcHostGeometryDiagnostics(
            windowLeft,
            windowTop,
            windowWidth,
            windowHeight,
            clientWidth,
            clientHeight,
            dpi,
            dpiScale,
            GetSystemMetrics(SmCxScreen),
            GetSystemMetrics(SmCyScreen),
            GetSystemMetrics(SmCxVirtualScreen),
            GetSystemMetrics(SmCyVirtualScreen),
            monitorWidth,
            monitorHeight,
            workAreaWidth,
            workAreaHeight,
            diagnosticError);
    }

    private static string AppendError(
        string? existing,
        string next) =>
        string.IsNullOrWhiteSpace(existing)
            ? next
            : $"{existing};{next}";
}
