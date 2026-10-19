using UniversalCouncil.CommandCenter.RemoteTransport;

var baseDirectory = AppContext.BaseDirectory;
var runtimeRoot = Path.Combine(
    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData),
    "UniversalCouncil",
    "CommandCenter",
    "RemoteTransport");
var registryPath = Path.Combine(
    runtimeRoot,
    "remote-owner-registry.json");
var port = 47721;

for (var index = 0; index < args.Length; index++)
{
    switch (args[index])
    {
        case "--port":
            port = int.Parse(args[++index]);
            break;
        case "--registry":
            registryPath = Path.GetFullPath(args[++index]);
            break;
        case "--runtime-root":
            runtimeRoot = Path.GetFullPath(args[++index]);
            break;
        default:
            throw new InvalidOperationException(
                $"Unsupported RemoteTransport argument: {args[index]}");
    }
}

if (port is <= 0 or > 65535)
{
    throw new InvalidOperationException(
        "Product RemoteTransport requires an explicit non-zero loopback port.");
}

var app = RemoteTransportHost.Build(
    new RemoteTransportHostOptions(
        Path.Combine(baseDirectory, "state", "remote-owner-gateway.json"),
        Path.Combine(baseDirectory, "state", "remote-transport.json"),
        registryPath,
        runtimeRoot,
        port));

await app.RunAsync();
