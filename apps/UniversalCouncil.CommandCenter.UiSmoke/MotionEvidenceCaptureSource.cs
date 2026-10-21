using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using WgcSharp;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal sealed record MotionEvidenceCapturedFrame(
    int Width,
    int Height,
    byte[] Pixels);

internal interface IMotionEvidenceCaptureSource : IDisposable
{
    string SourceId { get; }

    MotionEvidenceCapturedFrame CaptureFrame();
}

internal sealed class WgcSharpWindowCaptureSource : IMotionEvidenceCaptureSource
{
    private readonly IntPtr _windowHandle;

    internal WgcSharpWindowCaptureSource(IntPtr windowHandle)
    {
        if (windowHandle == IntPtr.Zero)
        {
            throw new ArgumentException("Evidence capture requires a non-zero HWND.", nameof(windowHandle));
        }

        _windowHandle = windowHandle;
    }

    public string SourceId => "WgcSharp-1.1.1/WGC_ONLY";

    public MotionEvidenceCapturedFrame CaptureFrame()
    {
        using var bitmap = WindowCapture.CaptureWindow(
            _windowHandle,
            CaptureStrategy.WgcOnly,
            timeoutMs: 1500);

        if (bitmap is null)
        {
            throw new InvalidOperationException("WgcSharp WGC-only capture returned no frame.");
        }

        var width = bitmap.Width;
        var height = bitmap.Height;
        var rowBytes = checked(width * 4);
        var pixels = new byte[checked(rowBytes * height)];
        var rectangle = new Rectangle(0, 0, width, height);
        var data = bitmap.LockBits(
            rectangle,
            ImageLockMode.ReadOnly,
            PixelFormat.Format32bppArgb);

        try
        {
            for (var y = 0; y < height; y++)
            {
                Marshal.Copy(
                    data.Scan0 + (y * data.Stride),
                    pixels,
                    y * rowBytes,
                    rowBytes);
            }
        }
        finally
        {
            bitmap.UnlockBits(data);
        }

        return new MotionEvidenceCapturedFrame(width, height, pixels);
    }

    public void Dispose()
    {
    }
}
