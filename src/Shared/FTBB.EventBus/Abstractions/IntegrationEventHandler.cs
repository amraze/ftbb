using System.Threading.Tasks;

namespace FTBB.EventBus.Abstractions;

public interface IIntegrationEventHandler<in TIntegrationEvent>
    where TIntegrationEvent : IntegrationEvent
{
    Task Handle(TIntegrationEvent @event);
}