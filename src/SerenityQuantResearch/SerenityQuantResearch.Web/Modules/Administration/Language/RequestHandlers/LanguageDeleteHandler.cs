using MyRow = SerenityQuantResearch.Administration.LanguageRow;

namespace SerenityQuantResearch.Administration;

public interface ILanguageDeleteHandler : IDeleteHandler<MyRow> { }

public class LanguageDeleteHandler(IRequestContext context)
    : DeleteRequestHandler<MyRow>(context), ILanguageDeleteHandler
{
}