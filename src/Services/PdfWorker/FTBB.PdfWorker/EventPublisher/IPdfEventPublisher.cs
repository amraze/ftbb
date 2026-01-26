namespace FTBB.PdfWorker.Services;

public interface IPdfEventPublisher
{
    Task PublishFolderReadyAsync(string folderPath);
}