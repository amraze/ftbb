using FTBB.EventBus.Abstractions;
using FTBB.EventBus.Events;

namespace FTBB.PdfWorker.Services;

public class PdfEventPublisher : IPdfEventPublisher
{
    private readonly IEventBus _eventBus;
    private readonly ILogger<PdfEventPublisher> _logger;

    public PdfEventPublisher(IEventBus eventBus, ILogger<PdfEventPublisher> logger)
    {
        _eventBus = eventBus;
        _logger = logger;
    }

    public Task PublishFolderReadyAsync(string folderPath)
    {
        var evt = new PdfDownloadedEvent
        {
            FolderPath = folderPath,
        };

        _eventBus.Publish(evt);
        _logger.LogInformation("Published folder to PdfExtractor : '{FolderPath}'", folderPath);

        return Task.CompletedTask;
    }
}