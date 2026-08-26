using SerenityQuantResearch.Administration;

namespace SerenityQuantResearch.AppServices;

public class RolePermissionService(ITwoLevelCache cache, ISqlConnections sqlConnections, ITypeSource typeSource)
    : BaseRolePermissionService<RolePermissionRow>(cache, sqlConnections, typeSource)
{
}