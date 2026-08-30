
using SerenityQuantResearch.Research;

namespace SerenityQuantResearch.Common.Pages;

public class DashboardPage : Controller
{
    [PageAuthorize(ResearchPermissionKeys.General), HttpGet, Route("~/")]
    public ActionResult Index()
    {
        return View("~/Modules/Research/Diagram/CpoDiagramIndex.cshtml");
    }

    [PageAuthorize(ResearchPermissionKeys.General), HttpGet, Route("~/Dashboard")]
    public ActionResult Dashboard()
    {
        return Redirect("~/");
    }
}
