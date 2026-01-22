using FTBB.PdfWorker.Utils;
using Google.Apis.Drive.v3;

namespace FTBB.PdfWorker.Filters
{
    public class GoogleDriveFolderFilter : IFolderFilter
    {
        private readonly DriveService _driveService;
        private readonly string _folderId;
        private readonly string _downloadBasePath;
        private readonly ILogger<GoogleDriveFolderFilter> _logger;

        public GoogleDriveFolderFilter(DriveService driveService, string folderId, string downloadBasePath, ILogger<GoogleDriveFolderFilter> logger)
        {
            _driveService = driveService;
            _folderId = folderId;
            _downloadBasePath = downloadBasePath;
            _logger = logger;
        }

        public async Task<IEnumerable<(string Id, string Name)>> FilterAsync(CancellationToken cancellationToken)
        {
            var request = _driveService.Files.List();
            request.Q = $"'{_folderId}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false";
            request.Fields = "files(id, name)";
            request.PageSize = 100;

            var result = await request.ExecuteAsync(cancellationToken);
            var foldersToDownload = new List<(string Id, string Name)>();

            if (result.Files != null)
            {
                foreach (var folder in result.Files)
                {
                    string sanitizedName = FileNameSanitizer.SanitizeName(folder.Name);
                    string localPath = Path.Combine(_downloadBasePath, sanitizedName);

                    if (!Directory.Exists(localPath))
                    {
                        foldersToDownload.Add((folder.Id, sanitizedName));
                    }
                }

                if (foldersToDownload.Count > 0)
                {
                    _logger.LogInformation("Queued {count} folders for download", foldersToDownload.Count);
                }
            }

            return foldersToDownload;
        }
    }
}
