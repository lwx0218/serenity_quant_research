using MyRow = SerenityQuantResearch.Administration.LanguageRow;

namespace SerenityQuantResearch.Administration;

public interface ILanguageListHandler : IListHandler<MyRow> { }

public class LanguageListHandler(IRequestContext context)
    : ListRequestHandler<MyRow>(context), ILanguageListHandler
{
}