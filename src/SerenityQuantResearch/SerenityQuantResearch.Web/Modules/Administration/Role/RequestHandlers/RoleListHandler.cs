using MyRow = SerenityQuantResearch.Administration.RoleRow;

namespace SerenityQuantResearch.Administration;

public interface IRoleListHandler : IListHandler<MyRow> { }

public class RoleListHandler(IRequestContext context)
    : ListRequestHandler<MyRow>(context), IRoleListHandler
{
}