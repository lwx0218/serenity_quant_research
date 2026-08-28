
using SerenityQuantResearch.Research;

namespace SerenityQuantResearch.Common.Pages;

[Route("Dashboard/[action]")]
public class DashboardPage : Controller
{
    [PageAuthorize(ResearchPermissionKeys.General), HttpGet, Route("~/")]
    public ActionResult Index()
    {
        return View("~/Modules/Research/Diagram/CpoDiagramIndex.cshtml");
    }

    [PageAuthorize, HttpGet, Route("~/Dashboard")]
    public ActionResult LegacyDashboard()
    {
        return View(MVC.Views.Common.Dashboard.DashboardIndex, new DashboardPageModel());
    }
}
