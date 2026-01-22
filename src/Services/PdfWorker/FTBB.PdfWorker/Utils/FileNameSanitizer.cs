namespace FTBB.PdfWorker.Utils
{
    public class FileNameSanitizer
    {
        public static string SanitizeName(string name)
        {
            char[] invalidChars = Path.GetInvalidFileNameChars();
            string sanitized = name.Replace('/', '-').Replace('\\', '-');

            foreach (char c in invalidChars)
            {
                if (c != '/' && c != '\\')
                {
                    sanitized = sanitized.Replace(c, '_');
                }
            }

            return sanitized;
        }
    }
}
