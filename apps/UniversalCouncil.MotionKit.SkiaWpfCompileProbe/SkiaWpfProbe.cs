using System.Windows.Media;
using System.Windows.Media.Imaging;
using SkiaSharp;

namespace UniversalCouncil.MotionKit.SkiaWpfCompileProbe;

public static class SkiaWpfProbe
{
    public static BitmapSource CreateBitmapSource()
    {
        using var bitmap = new SKBitmap(
            new SKImageInfo(64, 64, SKColorType.Bgra8888, SKAlphaType.Premul));
        using var canvas = new SKCanvas(bitmap);
        canvas.Clear(SKColors.Transparent);
        canvas.DrawCircle(32, 32, 16, new SKPaint
        {
            Color = SKColors.White,
            IsAntialias = true
        });
        canvas.Flush();

        var source = BitmapSource.Create(
            bitmap.Width,
            bitmap.Height,
            96,
            96,
            PixelFormats.Bgra32,
            palette: null,
            bitmap.GetPixels(),
            bitmap.ByteCount,
            bitmap.RowBytes);
        source.Freeze();
        return source;
    }
}
