using FTBB.EventBus.Abstractions;
using FTBB.EventBus.RabbitMQ;
using FTBB.PdfWorker;
using FTBB.PdfWorker.Services;
using RabbitMQ.Client;

var builder = Host.CreateApplicationBuilder(args);

// Configure Logging
builder.Logging.ClearProviders();
builder.Logging.AddConsole();
builder.Logging.SetMinimumLevel(LogLevel.Information);

// RabbitMQ Connection Factory
builder.Services.AddSingleton<IConnectionFactory>(sp =>
{
    var config = sp.GetRequiredService<IConfiguration>();
    return new ConnectionFactory
    {
        HostName = config["RabbitMQ:HostName"] ?? "localhost",
        Port = int.Parse(config["RabbitMQ:Port"] ?? "5672"),
        UserName = config["RabbitMQ:UserName"] ?? "guest",
        Password = config["RabbitMQ:Password"] ?? "guest",
        VirtualHost = "/",
        AutomaticRecoveryEnabled = true,
        NetworkRecoveryInterval = TimeSpan.FromSeconds(10),
        RequestedHeartbeat = TimeSpan.FromSeconds(60)
    };
});

// RabbitMQ Connection
builder.Services.AddSingleton<IRabbitMqConnection, RabbitMqConnection>();

// Event Bus
builder.Services.AddSingleton<IEventBus>(sp =>
{
    var connection = sp.GetRequiredService<IRabbitMqConnection>();
    var logger = sp.GetRequiredService<ILogger<RabbitMqEventBus>>();
    return new RabbitMqEventBus(connection, logger);
});

builder.Services.AddSingleton<IPdfEventPublisher, PdfEventPublisher>();

// Worker
builder.Services.AddHostedService<Worker>();

var host = builder.Build();
host.Run();