namespace SerenityQuantResearch.Research.Pages;

[PageAuthorize(ResearchPermissionKeys.General)]
public sealed class CpoResearchPage : Controller
{
    [HttpGet, Route("Research/Cpo")]
    public ActionResult Diagram() =>
        View("~/Modules/Research/Diagram/CpoDiagramIndex.cshtml");

    [HttpGet, Route("Research/Parts/{partId}")]
    public ActionResult PartDetail(string partId)
    {
        if (string.IsNullOrWhiteSpace(partId))
            return BadRequest();

        ViewData["PartId"] = partId;
        return View("~/Modules/Research/Diagram/PartDetail.cshtml");
    }
}
