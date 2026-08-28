namespace SerenityQuantResearch.Research.Pages;

[PageAuthorize(ResearchPermissionKeys.General)]
public sealed class ResearchWorkspacePage : Controller
{
    [HttpGet, Route("Research/Workspace")]
    public ActionResult Index() =>
        View("~/Modules/Research/Workspace/ResearchWorkspacePlaceholder.cshtml");
}
