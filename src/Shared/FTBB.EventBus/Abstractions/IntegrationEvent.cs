using System;

namespace FTBB.EventBus.Abstractions;

public abstract class IntegrationEvent
{
    public IntegrationEvent()
    {
        Id = Guid.NewGuid();
        CreationDate = DateTime.UtcNow;
    }

    public Guid Id { get; private set; }
    public DateTime CreationDate { get; private set; }
}