namespace FTBB.PdfWorker.Pipes
{
    public interface IFolderPipe
    {
        Task ProcessAsync((string Id, string Name) folder, CancellationToken cancellationToken);
    }
}
