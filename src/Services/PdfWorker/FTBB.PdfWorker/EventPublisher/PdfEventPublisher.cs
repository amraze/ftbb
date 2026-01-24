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

    public Task PublishFolderReadyAsync(string folderId, string folderName, string folderPath)
    {
        var evt = new PdfDownloadedEvent
        {
            FolderPath = folderPath,
            FolderName = folderName,
            GoogleDriveFolderId = folderId
        };

        _eventBus.Publish(evt);
        _logger.LogInformation("Published folder ready: '{FolderName}' at {Path}", folderName, folderPath);

        return Task.CompletedTask;
    }
}