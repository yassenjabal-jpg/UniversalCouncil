using Microsoft.UI.Composition;
using Microsoft.UI.Dispatching;

namespace UniversalCouncil.MotionKit.CompositionRuntimeProbe;

internal static class Program
{
    [STAThread]
    private static int Main()
    {
        var queueController = DispatcherQueueController.CreateOnCurrentThread();

        try
        {
            using var compositor = new Compositor();
            var visual = compositor.CreateSpriteVisual();
            var animation = compositor.CreateScalarKeyFrameAnimation();

            animation.Duration = TimeSpan.FromMilliseconds(120);
            animation.InsertKeyFrame(0f, 0f);
            animation.InsertKeyFrame(1f, 1f);

            visual.Opacity = 0f;
            visual.StartAnimation("Opacity", animation);
            visual.StopAnimation("Opacity");
            visual.Opacity = 1f;

            var propertySet = compositor.CreatePropertySet();
            propertySet.InsertScalar("MotionKitProbe", 1f);

            Console.WriteLine(
                "MotionKit Windows Composition runtime probe: PASS "
                + "(owned DispatcherQueue + Compositor + SpriteVisual + ScalarKeyFrameAnimation)");
        }
        finally
        {
            queueController.ShutdownQueue();
        }

        return 0;
    }
}
