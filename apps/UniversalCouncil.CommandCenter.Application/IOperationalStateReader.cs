namespace UniversalCouncil.CommandCenter.Application;

public interface IOperationalStateReader
{
    OperationalStateDocument Read();
}

public sealed class OperationalStateReadException : Exception
{
    public OperationalStateReadException(string message)
        : base(message)
    {
    }

    public OperationalStateReadException(string message, Exception innerException)
        : base(message, innerException)
    {
    }
}
