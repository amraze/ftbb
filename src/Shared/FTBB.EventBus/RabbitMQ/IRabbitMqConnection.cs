using RabbitMQ.Client;
using System;

namespace FTBB.EventBus.RabbitMQ;

public interface IRabbitMqConnection : IDisposable
{
    bool IsConnected { get; }
    bool TryConnect();
    IModel CreateModel();
}