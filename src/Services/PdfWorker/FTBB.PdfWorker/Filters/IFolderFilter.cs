namespace FTBB.PdfWorker.Filters
{
    public interface IFolderFilter
    {
        Task<IEnumerable<(string Id, string Name)>> FilterAsync(CancellationToken cancellationToken);
    }
}
