using System.Diagnostics;
using System.Runtime.InteropServices;
using System.Threading;
using Vortice.Direct3D;
using Vortice.Direct3D11;
using Vortice.DXGI;
using Windows.Graphics.Capture;
using Windows.Graphics.DirectX;
using Windows.Graphics.DirectX.Direct3D11;
using WinRT;

namespace UniversalCouncil.CommandCenter.UiSmoke;

internal sealed record MotionEvidenceCapturedFrame(
    int Width,
    int Height,
    byte[] Pixels,
    long SourceFrameSequence);

internal interface IMotionEvidenceCaptureSource : IDisposable
{
    string SourceId { get; }

    int Width { get; }

    int Height { get; }

    long FramesArrived { get; }

    long FrameErrors { get; }

    double FirstFrameLatencyMs { get; }

    bool WaitForFirstFrame(TimeSpan timeout);

    MotionEvidenceCapturedFrame CaptureFrame();
}

/// <summary>
/// Evidence-only persistent Windows.Graphics.Capture source.
///
/// Architecture: one HWND -> one WGC session -> one free-threaded frame pool ->
/// one persistent D3D11 staging texture -> latest actual BGRA frame. The public
/// product does not depend on this type.
///
/// This is a bounded adaptation of the persistent-capture pattern reviewed in
/// WKImods/WKI-Clipper (MIT). See THIRD_PARTY_NOTICES.md.
/// </summary>
internal sealed class PersistentWgcWindowCaptureSource : IMotionEvidenceCaptureSource
{
    private readonly ID3D11Device _device;
    private readonly ID3D11DeviceContext _context;
    private readonly ID3D11Texture2D _staging;
    private readonly IDirect3DDevice _winrtDevice;
    private readonly GraphicsCaptureItem _item;
    private readonly Direct3D11CaptureFramePool _framePool;
    private readonly GraphicsCaptureSession _session;
    private readonly object _frameLock = new();
    private readonly byte[] _latestPixels;
    private readonly ManualResetEventSlim _firstFrame = new(false);
    private readonly AutoResetEvent _frameArrived = new(false);
    private readonly Stopwatch _lifetime = Stopwatch.StartNew();

    private bool _hasFrame;
    private bool _disposed;
    private long _frameSequence;
    private long _frameErrors;
    private double _firstFrameLatencyMs;

    internal PersistentWgcWindowCaptureSource(IntPtr windowHandle)
    {
        if (windowHandle == IntPtr.Zero)
        {
            throw new ArgumentException("Evidence capture requires a non-zero HWND.", nameof(windowHandle));
        }

        if (!GraphicsCaptureSession.IsSupported())
        {
            throw new PlatformNotSupportedException("Windows.Graphics.Capture is not supported on this runner.");
        }

        _item = PersistentWgcInterop.CreateItemForWindow(windowHandle);
        Width = _item.Size.Width;
        Height = _item.Size.Height;
        if (Width <= 0 || Height <= 0)
        {
            throw new InvalidOperationException($"WGC returned invalid item dimensions {Width}x{Height}.");
        }

        _latestPixels = new byte[checked(Width * Height * 4)];

        var result = D3D11.D3D11CreateDevice(
            null,
            DriverType.Hardware,
            DeviceCreationFlags.BgraSupport,
            null,
            out ID3D11Device? device);

        if (result.Failure || device is null)
        {
            throw new InvalidOperationException($"D3D11CreateDevice(Hardware) failed: 0x{result.Code:X8}");
        }

        _device = device;
        _context = _device.ImmediateContext;
        _winrtDevice = PersistentWgcInterop.CreateWinRtDevice(_device);

        _staging = _device.CreateTexture2D(new Texture2DDescription
        {
            Width = (uint)Width,
            Height = (uint)Height,
            MipLevels = 1,
            ArraySize = 1,
            Format = Format.B8G8R8A8_UNorm,
            SampleDescription = new SampleDescription(1, 0),
            Usage = ResourceUsage.Staging,
            BindFlags = BindFlags.None,
            CPUAccessFlags = CpuAccessFlags.Read,
            MiscFlags = ResourceOptionFlags.None,
        });

        _framePool = Direct3D11CaptureFramePool.CreateFreeThreaded(
            _winrtDevice,
            DirectXPixelFormat.B8G8R8A8UIntNormalized,
            2,
            _item.Size);
        _framePool.FrameArrived += OnFrameArrived;

        _session = _framePool.CreateCaptureSession(_item);
        _session.IsCursorCaptureEnabled = false;
        try
        {
            _session.IsBorderRequired = false;
        }
        catch
        {
            // Border suppression is a visual-fidelity preference only.
            // Lack of support must not change the capture surface.
        }

        _session.StartCapture();
    }

    public string SourceId => "RAW_WGC_PERSISTENT/WKI_CLIPPER_PATTERN";

    public int Width { get; }

    public int Height { get; }

    public long FramesArrived => Interlocked.Read(ref _frameSequence);

    public long FrameErrors => Interlocked.Read(ref _frameErrors);

    public double FirstFrameLatencyMs
    {
        get
        {
            lock (_frameLock)
            {
                return _firstFrameLatencyMs;
            }
        }
    }

    public bool WaitForFirstFrame(TimeSpan timeout)
    {
        return _firstFrame.Wait(timeout);
    }

    public MotionEvidenceCapturedFrame CaptureFrame()
    {
        var pixels = GC.AllocateUninitializedArray<byte>(_latestPixels.Length);
        var sequence = CopyLatestFrameTo(pixels);
        return new MotionEvidenceCapturedFrame(Width, Height, pixels, sequence);
    }

    internal long CopyLatestFrameTo(byte[] destination)
    {
        lock (_frameLock)
        {
            if (!_hasFrame)
            {
                throw new InvalidOperationException("Persistent WGC session has not delivered a frame.");
            }

            if (destination.Length < _latestPixels.Length)
            {
                throw new ArgumentException(
                    "Destination buffer is smaller than the persistent WGC frame.",
                    nameof(destination));
            }

            Buffer.BlockCopy(_latestPixels, 0, destination, 0, _latestPixels.Length);
            return _frameSequence;
        }
    }

    internal bool WaitForFrameAfter(long sourceFrameSequence, TimeSpan timeout)
    {
        var clock = Stopwatch.StartNew();
        while (clock.Elapsed < timeout)
        {
            if (Interlocked.Read(ref _frameSequence) > sourceFrameSequence)
            {
                return true;
            }

            var remaining = timeout - clock.Elapsed;
            if (remaining <= TimeSpan.Zero || !_frameArrived.WaitOne(remaining))
            {
                break;
            }
        }

        return Interlocked.Read(ref _frameSequence) > sourceFrameSequence;
    }

    private void OnFrameArrived(Direct3D11CaptureFramePool sender, object args)
    {
        if (_disposed)
        {
            return;
        }

        try
        {
            using var frame = sender.TryGetNextFrame();
            if (frame is null)
            {
                return;
            }

            var size = frame.ContentSize;
            if (size.Width != Width || size.Height != Height)
            {
                Interlocked.Increment(ref _frameErrors);
                return;
            }

            using var texture = PersistentWgcInterop.GetTextureFromSurface(frame.Surface);
            _context.CopyResource(_staging, texture);

            var mapped = _context.Map(
                _staging,
                0,
                MapMode.Read,
                Vortice.Direct3D11.MapFlags.None);

            try
            {
                var rowBytes = checked(Width * 4);
                lock (_frameLock)
                {
                    for (var y = 0; y < Height; y++)
                    {
                        Marshal.Copy(
                            IntPtr.Add(mapped.DataPointer, y * (int)mapped.RowPitch),
                            _latestPixels,
                            y * rowBytes,
                            rowBytes);
                    }

                    _frameSequence++;
                    if (!_hasFrame)
                    {
                        _firstFrameLatencyMs = _lifetime.Elapsed.TotalMilliseconds;
                    }

                    _hasFrame = true;
                }

                _firstFrame.Set();
                _frameArrived.Set();
            }
            finally
            {
                _context.Unmap(_staging, 0);
            }
        }
        catch
        {
            Interlocked.Increment(ref _frameErrors);
        }
    }

    public void Dispose()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;
        try
        {
            _framePool.FrameArrived -= OnFrameArrived;
        }
        catch
        {
        }

        try
        {
            _session.Dispose();
        }
        catch
        {
        }

        try
        {
            _framePool.Dispose();
        }
        catch
        {
        }

        try
        {
            _winrtDevice.Dispose();
        }
        catch
        {
        }

        try
        {
            _staging.Dispose();
        }
        catch
        {
        }

        try
        {
            _context.Dispose();
        }
        catch
        {
        }

        try
        {
            _device.Dispose();
        }
        catch
        {
        }

        _frameArrived.Dispose();
        _firstFrame.Dispose();
    }
}

internal static class PersistentWgcInterop
{
    [DllImport("combase.dll", CharSet = CharSet.Unicode)]
    private static extern int WindowsCreateString(
        string sourceString,
        int length,
        out IntPtr hstring);

    [DllImport("combase.dll")]
    private static extern int WindowsDeleteString(IntPtr hstring);

    [DllImport("combase.dll")]
    private static extern int RoGetActivationFactory(
        IntPtr activatableClassId,
        ref Guid iid,
        out IntPtr factory);

    [DllImport("d3d11.dll")]
    private static extern int CreateDirect3D11DeviceFromDXGIDevice(
        IntPtr dxgiDevice,
        out IntPtr graphicsDevice);

    [ComImport]
    [Guid("3628E81B-3CAC-4C60-B7F4-23CE0E0C3356")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IGraphicsCaptureItemInterop
    {
        IntPtr CreateForWindow([In] IntPtr window, [In] ref Guid iid);

        IntPtr CreateForMonitor([In] IntPtr monitor, [In] ref Guid iid);
    }

    [ComImport]
    [Guid("A9B3D012-3DF2-4EE3-B8D1-8695F457D3C1")]
    [InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
    private interface IDirect3DDxgiInterfaceAccess
    {
        IntPtr GetInterface([In] ref Guid iid);
    }

    private static readonly Guid GraphicsCaptureItemIid =
        new("79C3F95B-31F7-4EC2-A464-632EF5D30760");

    internal static GraphicsCaptureItem CreateItemForWindow(IntPtr windowHandle)
    {
        const string className = "Windows.Graphics.Capture.GraphicsCaptureItem";
        Marshal.ThrowExceptionForHR(
            WindowsCreateString(className, className.Length, out var classId));

        try
        {
            var interopIid = typeof(IGraphicsCaptureItemInterop).GUID;
            Marshal.ThrowExceptionForHR(
                RoGetActivationFactory(classId, ref interopIid, out var factoryPtr));

            try
            {
                var interop = (IGraphicsCaptureItemInterop)Marshal.GetObjectForIUnknown(factoryPtr);
                var itemIid = GraphicsCaptureItemIid;
                var itemPtr = interop.CreateForWindow(windowHandle, ref itemIid);
                try
                {
                    return GraphicsCaptureItem.FromAbi(itemPtr);
                }
                finally
                {
                    Marshal.Release(itemPtr);
                }
            }
            finally
            {
                Marshal.Release(factoryPtr);
            }
        }
        finally
        {
            WindowsDeleteString(classId);
        }
    }

    internal static IDirect3DDevice CreateWinRtDevice(ID3D11Device device)
    {
        using var dxgi = device.QueryInterface<IDXGIDevice>();
        Marshal.ThrowExceptionForHR(
            CreateDirect3D11DeviceFromDXGIDevice(
                dxgi.NativePointer,
                out var inspectable));

        try
        {
            return MarshalInterface<IDirect3DDevice>.FromAbi(inspectable);
        }
        finally
        {
            Marshal.Release(inspectable);
        }
    }

    internal static ID3D11Texture2D GetTextureFromSurface(IDirect3DSurface surface)
    {
        var unknown = MarshalInterface<IDirect3DSurface>.FromManaged(surface);
        try
        {
            var access =
                (IDirect3DDxgiInterfaceAccess)Marshal.GetObjectForIUnknown(unknown);
            var textureIid = typeof(ID3D11Texture2D).GUID;
            var texturePointer = access.GetInterface(ref textureIid);
            return new ID3D11Texture2D(texturePointer);
        }
        finally
        {
            Marshal.Release(unknown);
        }
    }
}
