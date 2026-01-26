using FTBB.EventBus.Abstractions;
using System;

namespace FTBB.EventBus.Events;

public class PdfDownloadedEvent : IntegrationEvent
{
    public string FolderPath { get; set; } = string.Empty;
}