namespace SerenityQuantResearch.Research.Pages;

[PageAuthorize(ResearchPermissionKeys.General)]
public sealed class CompanyResearchPage : Controller
{
    [HttpGet, Route("Research/Companies")]
    public ActionResult Universe() =>
        View("~/Modules/Research/Company/CompanyUniverse.cshtml");

    [HttpGet, Route("Research/Companies/{companyId}")]
    public ActionResult Detail(string companyId)
    {
        if (string.IsNullOrWhiteSpace(companyId))
            return BadRequest();
        ViewData["CompanyId"] = companyId;
        return View("~/Modules/Research/Company/CompanyDetail.cshtml");
    }

    [HttpGet, Route("Research/ChainNodes/{chainNodeId}")]
    public ActionResult ChainNodeDetail(string chainNodeId)
    {
        if (string.IsNullOrWhiteSpace(chainNodeId))
            return BadRequest();
        ViewData["ChainNodeId"] = chainNodeId;
        return View("~/Modules/Research/Company/ChainNodeDetail.cshtml");
    }
}
