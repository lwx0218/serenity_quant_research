using MyRow = SerenityQuantResearch.Administration.LanguageRow;

namespace SerenityQuantResearch.Administration;

public interface ILanguageSaveHandler : ISaveHandler<MyRow> { }

public class LanguageSaveHandler(IRequestContext context)
    : SaveRequestHandler<MyRow>(context), ILanguageSaveHandler
{
}