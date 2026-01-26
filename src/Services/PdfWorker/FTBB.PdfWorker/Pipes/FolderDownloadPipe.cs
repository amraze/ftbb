using FTBB.PdfWorker.Utils;
using Google.Apis.Drive.v3;

namespace FTBB.PdfWorker.Pipes
{
    public class FolderDownloadPipe : IFolderPipe
    {
        private readonly DriveService _driveService;
        private readonly string _downloadBasePath;
        private readonly ILogger<FolderDownloadPipe> _logger;

        public FolderDownloadPipe(DriveService driveService, string downloadBasePath, ILogger<FolderDownloadPipe> logger)
        {
            _driveService = driveService;
            _downloadBasePath = downloadBasePath;
            _logger = logger;
        }

        public async Task ProcessAsync((string Id, string Name) folder, CancellationToken cancellationToken)
        {
            string localPath = Path.Combine(_downloadBasePath, folder.Name);
            await DownloadFolderAsync(folder.Id, folder.Name, localPath, cancellationToken);
        }

        private async Task DownloadFolderAsync(string folderId, string folderName, string localPath, CancellationToken cancellationToken)
        {
            Directory.CreateDirectory(localPath);

            var request = _driveService.Files.List();
            request.Q = $"'{folderId}' in parents and trashed=false";
            request.Fields = "files(id, name, mimeType)";
            request.PageSize = 1000;

            var result = await request.ExecuteAsync(cancellationToken);

            if (result.Files != null)
            {
                foreach (var file in result.Files)
                {
                    string sanitizedName = FileNameSanitizer.SanitizeName(file.Name);
                    if (file.MimeType == "application/vnd.google-apps.folder")
                    {
                        string subPath = Path.Combine(localPath, sanitizedName);
                        await DownloadFolderAsync(file.Id, sanitizedName, subPath, cancellationToken);
                    }
                    else
                    {
                        await DownloadFileAsync(file.Id, sanitizedName, localPath, cancellationToken);
                    }
                }
            }
        }

        private async Task DownloadFileAsync(string fileId, string fileName, string localPath, CancellationToken cancellationToken)
        {
            string filePath = Path.Combine(localPath, fileName);
            var request = _driveService.Files.Get(fileId);

            using var stream = new FileStream(filePath, FileMode.Create, FileAccess.Write);
            await request.DownloadAsync(stream, cancellationToken);
        }
    }
}
