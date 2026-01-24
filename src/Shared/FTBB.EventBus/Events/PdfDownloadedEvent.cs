using FTBB.EventBus.Abstractions;
using System;

namespace FTBB.EventBus.Events;

public class PdfDownloadedEvent : IntegrationEvent
{
    public string EventId { get; set; } = Guid.NewGuid().ToString();
    public DateTime Timestamp { get; set; } = DateTime.UtcNow;
    public string FolderPath { get; set; } = string.Empty;
    public string FolderName { get; set; } = string.Empty;
    public string GoogleDriveFolderId { get; set; } = string.Empty;
}