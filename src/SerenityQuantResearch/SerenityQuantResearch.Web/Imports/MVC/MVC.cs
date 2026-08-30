
namespace SerenityQuantResearch.MVC;

public static partial class Views
{
    public static partial class Common
    {
        public static partial class Dashboard
        {
            public const string DashboardIndex = "~/Modules/Common/Dashboard/DashboardIndex.cshtml";
        }
    }

    public static partial class Errors
    {
        public const string AccessDenied = "~/Views/Errors/AccessDenied.cshtml";
        public const string ValidationError = "~/Views/Errors/ValidationError.cshtml";
    }

    public static partial class Membership
    {
        public static partial class Account
        {
            public static partial class Login
            {
                public const string LoginPage = "~/Modules/Membership/Account/Login/LoginPage.cshtml";
            }

            public static partial class SignUp
            {
                public const string ActivateEmail = "~/Modules/Membership/Account/SignUp/ActivateEmail.cshtml";
                public const string SignUpPage = "~/Modules/Membership/Account/SignUp/SignUpPage.cshtml";
            }
        }
    }

    public static partial class Research
    {
        public static partial class Company
        {
            public const string ChainNodeDetail = "~/Modules/Research/Company/ChainNodeDetail.cshtml";
            public const string CompanyDetail = "~/Modules/Research/Company/CompanyDetail.cshtml";
            public const string CompanyUniverse = "~/Modules/Research/Company/CompanyUniverse.cshtml";
        }

        public static partial class Diagram
        {
            public const string CpoDiagramIndex = "~/Modules/Research/Diagram/CpoDiagramIndex.cshtml";
            public const string PartDetail = "~/Modules/Research/Diagram/PartDetail.cshtml";
        }

        public static partial class Workspace
        {
            public const string ResearchWorkspace = "~/Modules/Research/Workspace/ResearchWorkspace.cshtml";
            public const string ResearchWorkspacePlaceholder = "~/Modules/Research/Workspace/ResearchWorkspacePlaceholder.cshtml";
        }
    }

    public static partial class Shared
    {
        public const string _Layout = "~/Views/Shared/_Layout.cshtml";
        public const string _LayoutHead = "~/Views/Shared/_LayoutHead.cshtml";
        public const string _LayoutNoNavigation = "~/Views/Shared/_LayoutNoNavigation.cshtml";
        public const string _Sidebar = "~/Views/Shared/_Sidebar.cshtml";
        public const string Error = "~/Views/Shared/Error.cshtml";
    }
}