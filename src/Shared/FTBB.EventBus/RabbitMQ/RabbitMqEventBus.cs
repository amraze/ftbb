using FTBB.EventBus.Abstractions;
using Microsoft.Extensions.Logging;
using Newtonsoft.Json;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace FTBB.EventBus.RabbitMQ;

public class RabbitMqEventBus : IEventBus, IDisposable
{
    private readonly IRabbitMqConnection _connection;
    private readonly ILogger<RabbitMqEventBus> _logger;
    private readonly string _exchangeName;
    private readonly string _queueName;
    private IModel? _consumerChannel;

    private readonly Dictionary<string, List<Type>> _handlers;
    private readonly List<Type> _eventTypes;

    public RabbitMqEventBus(IRabbitMqConnection connection,ILogger<RabbitMqEventBus> logger,string exchangeName = "ftbb_event_bus",string queueName = "ftbb_queue")
    {
        _connection = connection ?? throw new ArgumentNullException(nameof(connection));
        _logger = logger ?? throw new ArgumentNullException(nameof(logger));
        _exchangeName = exchangeName;
        _queueName = queueName;
        _handlers = new Dictionary<string, List<Type>>();
        _eventTypes = new List<Type>();
        _connection.TryConnect();
    }

    public void Publish(IntegrationEvent @event)
    {
        if (!_connection.IsConnected)
        {
            _connection.TryConnect();
        }

        var eventName = @event.GetType().Name;
        using var channel = _connection.CreateModel();

        channel.ExchangeDeclare(
            exchange: _exchangeName,
            type: ExchangeType.Topic,
            durable: true,
            autoDelete: false);

        var message = JsonConvert.SerializeObject(@event);
        var body = Encoding.UTF8.GetBytes(message);

        var properties = channel.CreateBasicProperties();
        properties.DeliveryMode = 2;

        channel.BasicPublish(exchange: _exchangeName,routingKey: string.Empty,basicProperties: properties,body: body);
    }

    public void Subscribe<T, TH>() where T : IntegrationEvent where TH : IIntegrationEventHandler<T>
    {
        var eventName = typeof(T).Name;
        var handlerType = typeof(TH);

        if (!_eventTypes.Contains(typeof(T)))
        {
            _eventTypes.Add(typeof(T));
        }

        if (!_handlers.ContainsKey(eventName))
        {
            _handlers.Add(eventName, new List<Type>());
        }

        if (_handlers[eventName].Any(s => s == handlerType))
        {
            throw new ArgumentException(
                $"Handler Type {handlerType.Name} already registered for '{eventName}'", nameof(handlerType));
        }

        _handlers[eventName].Add(handlerType);
        StartBasicConsume();
    }

    private void StartBasicConsume()
    {
        if (_consumerChannel != null)
        {
            return;
        }

        if (!_connection.IsConnected)
        {
            _connection.TryConnect();
        }

        _consumerChannel = _connection.CreateModel();

        _consumerChannel.ExchangeDeclare(
            exchange: _exchangeName,
            type: ExchangeType.Topic,
            durable: true,
            autoDelete: false);

        _consumerChannel.QueueDeclare(
            queue: _queueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: null);

        _consumerChannel.QueueBind(
            queue: _queueName,
            exchange: _exchangeName,
            routingKey: string.Empty);

        var consumer = new EventingBasicConsumer(_consumerChannel);

        consumer.Received += async (model, ea) =>
        {
            var eventName = ea.RoutingKey;
            var message = Encoding.UTF8.GetString(ea.Body.ToArray());

            try
            {
                await ProcessEvent(eventName, message);
                _consumerChannel.BasicAck(ea.DeliveryTag, false);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error processing message: {Message}", message);
                _consumerChannel.BasicNack(ea.DeliveryTag, false, false);
            }
        };

        _consumerChannel.BasicConsume(
            queue: _queueName,
            autoAck: false,
            consumer: consumer);
    }

    private async Task ProcessEvent(string eventName, string message)
    {
        if (_handlers.ContainsKey(eventName))
        {
            var subscriptions = _handlers[eventName];
            foreach (var subscription in subscriptions)
            {
                var handler = Activator.CreateInstance(subscription);
                if (handler == null) continue;

                var eventType = _eventTypes.SingleOrDefault(t => t.Name == eventName);
                if (eventType == null) continue;

                var integrationEvent = JsonConvert.DeserializeObject(message, eventType);
                var concreteType = typeof(IIntegrationEventHandler<>).MakeGenericType(eventType);

                await (Task)concreteType.GetMethod("Handle")!.Invoke(handler, new object[] { integrationEvent! })!;
            }
        }
        else
        {
            _logger.LogWarning("No subscription for RabbitMQ event: {EventName}", eventName);
        }
    }

    public void Dispose()
    {
        _consumerChannel?.Dispose();
    }
}