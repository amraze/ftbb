namespace FTBB.PdfWorker.Services;

public interface IPdfEventPublisher
{
    Task PublishFolderReadyAsync(string folderId, string folderName, string folderPath);
}