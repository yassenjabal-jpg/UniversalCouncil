using Microsoft.UI.Composition;
using Microsoft.UI.Dispatching;

namespace UniversalCouncil.MotionKit.CompositionRuntimeProbe;

internal static class Program
{
    [STAThread]
    private static int Main(string[] args)
    {
        if (args.Length == 2 && args[0] == "--interactive") return InteractiveWindowProbe.Run(args[1]);
        var queueController = DispatcherQueueController.CreateOnCurrentThread();
        var dispatcherQueue = queueController.DispatcherQueue;

        if (!dispatcherQueue.HasThreadAccess)
        {
            throw new InvalidOperationException(
                "Owned DispatcherQueue does not have access to the probe thread.");
        }

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

            // CreateOnCurrentThread requires the owner to run a USER32/message loop.
            // Queue an explicit exit, run the owned loop, then synchronously shut it down.
            dispatcherQueue.EnqueueEventLoopExit();
            dispatcherQueue.RunEventLoop();

            Console.WriteLine(
                "MotionKit Windows Composition runtime probe: PASS "
                + "(owned DispatcherQueue loop + Compositor + SpriteVisual + ScalarKeyFrameAnimation)");
        }
        finally
        {
            queueController.ShutdownQueue();
        }

        return 0;
    }
}
