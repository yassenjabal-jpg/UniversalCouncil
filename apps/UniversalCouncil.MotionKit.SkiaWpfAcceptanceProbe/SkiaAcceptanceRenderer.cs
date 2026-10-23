using System.Windows.Media;
using System.Windows.Media.Imaging;
using SkiaSharp;

namespace UniversalCouncil.MotionKit.SkiaWpfAcceptanceProbe;

internal enum SceneKind
{
    InteractiveIcon,
    RouteTransfer,
    SemanticHandoff,
    DenseStress
}

internal sealed record SceneState(
    SceneKind Kind,
    float Progress = 0f,
    bool Focused = false,
    bool Pressed = false,
    bool Selected = false,
    bool Returning = false,
    bool DestinationAvailable = true,
    float DensePhase = 0f,
    bool Reduced = false);

internal sealed class SkiaAcceptanceRenderer : IDisposable
{
    public const int PixelWidth = 800;
    public const int PixelHeight = 420;

    private readonly SKBitmap _bitmap = new(
        new SKImageInfo(PixelWidth, PixelHeight, SKColorType.Bgra8888, SKAlphaType.Premul));
    private readonly SKCanvas _canvas;
    private readonly SKPaint _stroke = new()
    {
        IsAntialias = true,
        Style = SKPaintStyle.Stroke,
        StrokeWidth = 4f,
        StrokeCap = SKStrokeCap.Round
    };
    private readonly SKPaint _fill = new()
    {
        IsAntialias = true,
        Style = SKPaintStyle.Fill
    };

    public SkiaAcceptanceRenderer()
    {
        _canvas = new SKCanvas(_bitmap);
    }

    public BitmapSource Render(SceneState state)
    {
        _canvas.Clear(state.Reduced
            ? new SKColor(20, 24, 32)
            : new SKColor(16, 20, 28));

        switch (state.Kind)
        {
            case SceneKind.InteractiveIcon:
                DrawInteractiveIcon(state);
                break;
            case SceneKind.RouteTransfer:
                DrawRouteTransfer(state);
                break;
            case SceneKind.SemanticHandoff:
                DrawSemanticHandoff(state);
                break;
            case SceneKind.DenseStress:
                DrawDenseStress(state);
                break;
        }

        _canvas.Flush();

        var source = BitmapSource.Create(
            _bitmap.Width,
            _bitmap.Height,
            96,
            96,
            PixelFormats.Bgra32,
            palette: null,
            _bitmap.GetPixels(),
            _bitmap.ByteCount,
            _bitmap.RowBytes);
        source.Freeze();
        return source;
    }

    public void Dispose()
    {
        _fill.Dispose();
        _stroke.Dispose();
        _canvas.Dispose();
        _bitmap.Dispose();
    }

    private void DrawInteractiveIcon(SceneState state)
    {
        var center = new SKPoint(400, 210);
        var focusProgress = Math.Clamp(state.Progress, 0f, 1f);
        var scale = state.Pressed
            ? 0.88f
            : state.Focused
                ? 1f + 0.08f * focusProgress
                : 1f;
        var radius = 62f * scale;

        if (state.Focused)
        {
            _stroke.Color = new SKColor(83, 197, 255, 180);
            _stroke.StrokeWidth = 5f;
            _canvas.DrawCircle(center, radius + 18f, _stroke);
        }

        _fill.Color = state.Selected
            ? new SKColor(48, 199, 132)
            : new SKColor(60, 112, 190);
        _canvas.DrawCircle(center, radius, _fill);

        _stroke.Color = new SKColor(235, 245, 255);
        _stroke.StrokeWidth = 7f;
        if (state.Selected)
        {
            using var builder = new SKPathBuilder();
            builder.MoveTo(center.X - 28, center.Y);
            builder.LineTo(center.X - 5, center.Y + 24);
            builder.LineTo(center.X + 34, center.Y - 28);
            using var path = builder.Detach();
            _canvas.DrawPath(path, _stroke);
        }
        else
        {
            _canvas.DrawLine(center.X - 28, center.Y, center.X + 28, center.Y, _stroke);
            _canvas.DrawLine(center.X, center.Y - 28, center.X, center.Y + 28, _stroke);
        }

        DrawModeMarker(state.Reduced);
    }

    private void DrawRouteTransfer(SceneState state)
    {
        var source = new SKPoint(120, 210);
        var destination = new SKPoint(680, 210);

        _stroke.Color = new SKColor(91, 104, 124);
        _stroke.StrokeWidth = 7f;
        _canvas.DrawLine(source, destination, _stroke);

        DrawNode(source, new SKColor(75, 126, 216));
        DrawNode(destination, new SKColor(48, 199, 132));

        var x = source.X + (destination.X - source.X) * Math.Clamp(state.Progress, 0f, 1f);
        _fill.Color = state.Returning
            ? new SKColor(255, 184, 77)
            : new SKColor(119, 92, 230);
        _canvas.DrawCircle(x, source.Y, 22, _fill);

        if (state.Returning)
        {
            _stroke.Color = new SKColor(255, 184, 77);
            _stroke.StrokeWidth = 4f;
            _canvas.DrawLine(x - 46, source.Y - 42, x - 18, source.Y - 42, _stroke);
            _canvas.DrawLine(x - 46, source.Y - 42, x - 34, source.Y - 54, _stroke);
            _canvas.DrawLine(x - 46, source.Y - 42, x - 34, source.Y - 30, _stroke);
        }

        DrawModeMarker(state.Reduced);
    }

    private void DrawSemanticHandoff(SceneState state)
    {
        var source = new SKPoint(145, 210);
        var destination = new SKPoint(655, 210);
        _stroke.Color = new SKColor(91, 104, 124);
        _stroke.StrokeWidth = 6f;
        _canvas.DrawLine(source, destination, _stroke);

        DrawNode(source, new SKColor(75, 126, 216));
        DrawNode(
            destination,
            state.DestinationAvailable
                ? new SKColor(48, 199, 132)
                : new SKColor(121, 129, 145));

        if (!state.DestinationAvailable)
        {
            _stroke.Color = new SKColor(240, 92, 92);
            _stroke.StrokeWidth = 6f;
            _canvas.DrawLine(destination.X - 28, destination.Y - 28, destination.X + 28, destination.Y + 28, _stroke);
            _canvas.DrawLine(destination.X + 28, destination.Y - 28, destination.X - 28, destination.Y + 28, _stroke);
        }

        var x = source.X + (destination.X - source.X) * Math.Clamp(state.Progress, 0f, 1f);
        _fill.Color = new SKColor(240, 196, 90);
        _canvas.DrawRoundRect(
            new SKRect(x - 26, source.Y - 20, x + 26, source.Y + 20),
            8,
            8,
            _fill);

        DrawModeMarker(state.Reduced);
    }

    private void DrawDenseStress(SceneState state)
    {
        const int columns = 8;
        const int rows = 8;
        const float startX = 95f;
        const float startY = 75f;
        const float gapX = 86f;
        const float gapY = 43f;

        for (var row = 0; row < rows; row++)
        {
            for (var column = 0; column < columns; column++)
            {
                var index = row * columns + column;
                var phase = state.DensePhase + index * 0.31f;
                var dx = state.Reduced ? 0f : MathF.Sin(phase) * 13f;
                var dy = state.Reduced ? 0f : MathF.Cos(phase * 0.8f) * 7f;
                var center = new SKPoint(
                    startX + column * gapX + dx,
                    startY + row * gapY + dy);
                var alpha = (byte)(150 + (index * 11) % 90);
                _fill.Color = new SKColor(
                    (byte)(70 + (index * 13) % 140),
                    (byte)(90 + (index * 17) % 120),
                    (byte)(120 + (index * 7) % 120),
                    alpha);
                _canvas.DrawCircle(center, 10 + index % 4, _fill);
            }
        }

        DrawModeMarker(state.Reduced);
    }

    private void DrawNode(SKPoint center, SKColor color)
    {
        _fill.Color = color;
        _canvas.DrawCircle(center, 42, _fill);
        _stroke.Color = new SKColor(235, 245, 255, 220);
        _stroke.StrokeWidth = 4f;
        _canvas.DrawCircle(center, 42, _stroke);
    }

    private void DrawModeMarker(bool reduced)
    {
        _fill.Color = reduced
            ? new SKColor(160, 170, 186)
            : new SKColor(83, 197, 255);
        _canvas.DrawRoundRect(new SKRect(30, 360, reduced ? 120 : 190, 382), 8, 8, _fill);
    }
}
