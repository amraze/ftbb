using FTBB.PdfWorker.Filters;
using FTBB.PdfWorker.Pipes;
using FTBB.PdfWorker.Services;
using Google.Apis.Auth.OAuth2;
using Google.Apis.Drive.v3;
using Google.Apis.Services;
using Google.Apis.Util.Store;

namespace FTBB.PdfWorker
{
    public class Worker : BackgroundService
    {
        private readonly ILogger<Worker> _logger;
        private readonly ILoggerFactory _loggerFactory;
        private readonly IPdfEventPublisher _eventPublisher;
        private DriveService? _driveService;
        private IFolderFilter? _filter;
        private IFolderPipe? _pipeline;
        private Queue<(string Id, string Name)> _queue = new Queue<(string, string)>();
        
        private const string FolderId = "1T1Ys0l2xyAQiz7QVIUe-hzlT3OqmKRQM";
        private const string DownloadBasePath = "./Downloads";

        public Worker(ILogger<Worker> logger,ILoggerFactory loggerFactory,IPdfEventPublisher eventPublisher)
        {
            _logger = logger;
            _loggerFactory = loggerFactory;
            _eventPublisher = eventPublisher;
        }

        protected override async Task ExecuteAsync(CancellationToken stoppingToken)
        {
            await InitializeAsync();
            Directory.CreateDirectory(DownloadBasePath);
            DateTime nextCheck = DateTime.UtcNow;

            while (!stoppingToken.IsCancellationRequested)
            {
                try
                {
                    if (DateTime.UtcNow >= nextCheck)
                    {
                        var folders = await _filter!.FilterAsync(stoppingToken);
                        foreach (var folder in folders)
                        {
                            _queue.Enqueue(folder);
                        }
                        nextCheck = DateTime.UtcNow.AddHours(1);
                    }

                    if (_queue.Count > 0)
                    {
                        var folder = _queue.Dequeue();
                        await _pipeline!.ProcessAsync(folder, stoppingToken);
                        var folderPath = Path.Combine(DownloadBasePath, folder.Name);
                        await _eventPublisher.PublishFolderReadyAsync(folder.Id, folder.Name, folderPath);
                    }

                    await Task.Delay(60000, stoppingToken);
                }
                catch (Exception ex)
                {
                    _logger.LogError(ex, "Processing error");
                    await Task.Delay(5000, stoppingToken);
                }
            }
        }

        private async Task InitializeAsync()
        {
            UserCredential credential;
            string[] scopes = { DriveService.Scope.DriveReadonly };

            using (var stream = new FileStream("credentials.json", FileMode.Open, FileAccess.Read))
            {
                credential = await GoogleWebAuthorizationBroker.AuthorizeAsync(
                    GoogleClientSecrets.FromStream(stream).Secrets,
                    scopes,
                    "user",
                    CancellationToken.None,
                    new FileDataStore("token.json", true));
            }

            _driveService = new DriveService(new BaseClientService.Initializer()
            {
                HttpClientInitializer = credential,
                ApplicationName = "FTBB PDF Worker",
            });

            _filter = new GoogleDriveFolderFilter(
                _driveService,
                FolderId,
                DownloadBasePath,
                _loggerFactory.CreateLogger<GoogleDriveFolderFilter>());

            _pipeline = new FolderDownloadPipe(
                _driveService,
                DownloadBasePath,
                _loggerFactory.CreateLogger<FolderDownloadPipe>());

            _logger.LogInformation("Initialized");
        }

        public override void Dispose()
        {
            _driveService?.Dispose();
            base.Dispose();
        }
    }
}