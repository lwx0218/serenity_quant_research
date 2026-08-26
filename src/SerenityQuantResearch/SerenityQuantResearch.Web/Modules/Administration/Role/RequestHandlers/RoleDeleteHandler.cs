using MyRow = SerenityQuantResearch.Administration.RoleRow;

namespace SerenityQuantResearch.Administration;

public interface IRoleDeleteHandler : IDeleteHandler<MyRow> { }

public class RoleDeleteHandler(IRequestContext context)
    : DeleteRequestHandler<MyRow>(context), IRoleDeleteHandler
{
}