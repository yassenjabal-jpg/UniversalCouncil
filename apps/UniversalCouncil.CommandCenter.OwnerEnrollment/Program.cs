using System.Text.Json;
using UniversalCouncil.CommandCenter.Application;
using UniversalCouncil.CommandCenter.Infrastructure;

var json = new JsonSerializerOptions
{
    PropertyNamingPolicy = JsonNamingPolicy.SnakeCaseLower,
    WriteIndented = true
};

if (args.Length == 0)
{
    Usage();
    return 2;
}

try
{
    var command = args[0];

    switch (command)
    {
        case "enroll-device":
        {
            RequireCount(args, 5);
            var registryPath = Path.GetFullPath(args[1]);
            var ownerId = args[2];
            var deviceId = args[3];
            var validityHours = int.Parse(args[4]);
            if (validityHours is <= 0 or > 24 * 30)
            {
                throw new InvalidOperationException(
                    "Device validity must be between 1 hour and 30 days.");
            }

            var now = DateTimeOffset.UtcNow;
            var service = NewService(registryPath);
            service.EnrollDevice(
                new(
                    ownerId,
                    deviceId,
                    now,
                    now.AddHours(validityHours)));

            Console.WriteLine(
                JsonSerializer.Serialize(
                    new
                    {
                        state = "DEVICE_ENROLLED",
                        owner_id = ownerId,
                        device_id = deviceId,
                        expires_at = now.AddHours(validityHours)
                    },
                    json));
            return 0;
        }

        case "issue-session":
        {
            RequireCount(args, 7);
            var registryPath = Path.GetFullPath(args[1]);
            var ownerId = args[2];
            var deviceId = args[3];
            var ttlMinutes = int.Parse(args[4]);
            var targets = SplitScope(args[5]);
            var effects = SplitScope(args[6]);

            if (ttlMinutes is <= 0 or > 60)
            {
                throw new InvalidOperationException(
                    "Session TTL must be between 1 and 60 minutes.");
            }

            var now = DateTimeOffset.UtcNow;
            var service = NewService(registryPath);
            var credential = service.IssueSession(
                new(
                    ownerId,
                    deviceId,
                    now,
                    now.AddMinutes(ttlMinutes),
                    targets,
                    effects));

            Console.WriteLine(
                JsonSerializer.Serialize(
                    new
                    {
                        state = "SESSION_ISSUED_ONCE",
                        warning = "Bearer token is shown once and is not persisted by the application.",
                        credential.OwnerId,
                        credential.DeviceId,
                        credential.SessionId,
                        credential.BearerToken,
                        credential.ValidFrom,
                        credential.ExpiresAt,
                        credential.AllowedTargets,
                        credential.AllowedEffects
                    },
                    json));
            return 0;
        }

        case "revoke-session":
        {
            RequireCount(args, 3);
            var service = NewService(Path.GetFullPath(args[1]));
            var receipt = service.RevokeSession(args[2]);
            Console.WriteLine(JsonSerializer.Serialize(receipt, json));
            return 0;
        }

        case "status":
        {
            RequireCount(args, 2);
            var service = NewService(Path.GetFullPath(args[1]));
            Console.WriteLine(
                JsonSerializer.Serialize(
                    service.Snapshot(),
                    json));
            return 0;
        }

        default:
            Usage();
            return 2;
    }
}
catch (Exception exc)
{
    Console.Error.WriteLine($"{exc.GetType().Name}: {exc.Message}");
    return 4;
}

static OwnerEnrollmentService NewService(string registryPath) =>
    new(new JsonOwnerEnrollmentRegistry(registryPath));

static string[] SplitScope(string value) =>
    value.Split(
        ',',
        StringSplitOptions.RemoveEmptyEntries |
        StringSplitOptions.TrimEntries);

static void RequireCount(string[] arguments, int expected)
{
    if (arguments.Length != expected)
    {
        throw new InvalidOperationException(
            $"Expected {expected - 1} arguments after the command.");
    }
}

static void Usage()
{
    Console.Error.WriteLine(
        "Allowed commands:\n" +
        "  enroll-device <registry> <owner-id> <device-id> <validity-hours>\n" +
        "  issue-session <registry> <owner-id> <device-id> <ttl-minutes> <targetsCsv> <effectsCsv>\n" +
        "  revoke-session <registry> <session-id>\n" +
        "  status <registry>");
}
