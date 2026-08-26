import { proxyTexts } from "@serenity-is/corelib";

namespace texts {
    export declare namespace Db {
        export function asKey(): typeof Db;
        export function asTry(): typeof Db;
        namespace Administration {
            export function asKey(): typeof Administration;
            export function asTry(): typeof Administration;
            namespace Language {
                export function asKey(): typeof Language;
                export function asTry(): typeof Language;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const LanguageId: string;
                export const LanguageName: string;
            }
            namespace Role {
                export function asKey(): typeof Role;
                export function asTry(): typeof Role;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const RoleId: string;
                export const RoleName: string;
            }
            namespace RolePermission {
                export function asKey(): typeof RolePermission;
                export function asTry(): typeof RolePermission;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const PermissionKey: string;
                export const RoleId: string;
                export const RoleName: string;
                export const RolePermissionId: string;
            }
            namespace User {
                export function asKey(): typeof User;
                export function asTry(): typeof User;
                export const ActorType: string;
                export const DisplayName: string;
                export const Email: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const IsActive: string;
                export const LastDirectoryUpdate: string;
                export const Password: string;
                export const PasswordConfirm: string;
                export const PasswordHash: string;
                export const PasswordSalt: string;
                export const Roles: string;
                export const Source: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
                export const UserId: string;
                export const UserImage: string;
                export const Username: string;
            }
            namespace UserPermission {
                export function asKey(): typeof UserPermission;
                export function asTry(): typeof UserPermission;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const Granted: string;
                export const PermissionKey: string;
                export const User: string;
                export const UserId: string;
                export const UserPermissionId: string;
                export const Username: string;
            }
            namespace UserRole {
                export function asKey(): typeof UserRole;
                export function asTry(): typeof UserRole;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const RoleId: string;
                export const RoleName: string;
                export const User: string;
                export const UserId: string;
                export const UserRoleId: string;
                export const Username: string;
            }
        }
        namespace Research {
            export function asKey(): typeof Research;
            export function asTry(): typeof Research;
            namespace Company {
                export function asKey(): typeof Company;
                export function asTry(): typeof Company;
                export const CompanyId: string;
                export const CountryRegion: string;
                export const CoveragePriority: string;
                export const EnglishName: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const Exchange: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Name: string;
                export const OfficialUrl: string;
                export const StableId: string;
                export const Ticker: string;
                export const UniverseLayer: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace CompanyExposure {
                export function asKey(): typeof CompanyExposure;
                export function asTry(): typeof CompanyExposure;
                export const CompanyExposureId: string;
                export const CompanyId: string;
                export const Confidence: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const IndustryChainNodeId: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const PhysicalPartId: string;
                export const Relevance: string;
                export const Role: string;
                export const ScopeNote: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
                export const VerificationState: string;
            }
            namespace CompanyExposureEvidence {
                export function asKey(): typeof CompanyExposureEvidence;
                export function asTry(): typeof CompanyExposureEvidence;
                export const CompanyExposureEvidenceId: string;
                export const CompanyExposureId: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const EvidenceId: string;
                export const InsertDate: string;
                export const InsertUserId: string;
            }
            namespace ConclusionEvidence {
                export function asKey(): typeof ConclusionEvidence;
                export function asTry(): typeof ConclusionEvidence;
                export const ConclusionEvidenceId: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const EvidenceId: string;
                export const EvidenceVersion: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const ResearchConclusionId: string;
            }
            namespace Event {
                export function asKey(): typeof Event;
                export function asTry(): typeof Event;
                export const CompanyId: string;
                export const Description: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const EventId: string;
                export const EventTime: string;
                export const EventType: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const SourceDocumentId: string;
                export const StableId: string;
                export const Title: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace Evidence {
                export function asKey(): typeof Evidence;
                export function asTry(): typeof Evidence;
                export const AnalystNote: string;
                export const CompanyId: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const EventId: string;
                export const EvidenceId: string;
                export const IndustryChainNodeId: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Locator: string;
                export const OriginalQuote: string;
                export const PhysicalPartId: string;
                export const Proposition: string;
                export const ReviewState: string;
                export const ReviewedAt: string;
                export const ReviewedBy: string;
                export const SourceDocumentId: string;
                export const StableId: string;
                export const Stance: string;
                export const TechnologyLinkId: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
                export const Version: string;
            }
            namespace IndustryChain {
                export function asKey(): typeof IndustryChain;
                export function asTry(): typeof IndustryChain;
                export const Description: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const IndustryChainId: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Name: string;
                export const StableId: string;
                export const ThemeId: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace IndustryChainNode {
                export function asKey(): typeof IndustryChainNode;
                export function asTry(): typeof IndustryChainNode;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const IndustryChainId: string;
                export const IndustryChainNodeId: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Name: string;
                export const NodeType: string;
                export const ParentNodeId: string;
                export const SortOrder: string;
                export const StableId: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace PhysicalModule {
                export function asKey(): typeof PhysicalModule;
                export function asTry(): typeof PhysicalModule;
                export const Description: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Name: string;
                export const PhysicalModuleId: string;
                export const SortOrder: string;
                export const StableId: string;
                export const ThemeId: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace PhysicalPart {
                export function asKey(): typeof PhysicalPart;
                export function asTry(): typeof PhysicalPart;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const FunctionSummary: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Name: string;
                export const ParentPartId: string;
                export const PhysicalModuleId: string;
                export const PhysicalPartId: string;
                export const ResearchStatus: string;
                export const SortOrder: string;
                export const StableId: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace PhysicalPartIndustryChainNode {
                export function asKey(): typeof PhysicalPartIndustryChainNode;
                export function asTry(): typeof PhysicalPartIndustryChainNode;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const IndustryChainNodeId: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const PhysicalPartId: string;
                export const PhysicalPartIndustryChainNodeId: string;
            }
            namespace PhysicalPartTechnologyLink {
                export function asKey(): typeof PhysicalPartTechnologyLink;
                export function asTry(): typeof PhysicalPartTechnologyLink;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const PhysicalPartId: string;
                export const PhysicalPartTechnologyLinkId: string;
                export const TechnologyLinkId: string;
            }
            namespace ReportConclusion {
                export function asKey(): typeof ReportConclusion;
                export function asTry(): typeof ReportConclusion;
                export const ConclusionVersion: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const ReportConclusionId: string;
                export const ResearchConclusionId: string;
                export const ResearchReportId: string;
            }
            namespace ReportEvidence {
                export function asKey(): typeof ReportEvidence;
                export function asTry(): typeof ReportEvidence;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const EvidenceId: string;
                export const EvidenceVersion: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const ReportEvidenceId: string;
                export const ResearchReportId: string;
            }
            namespace ResearchConclusion {
                export function asKey(): typeof ResearchConclusion;
                export function asTry(): typeof ResearchConclusion;
                export const Confidence: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const InvalidationConditions: string;
                export const PublicationState: string;
                export const ResearchConclusionId: string;
                export const Risks: string;
                export const StableId: string;
                export const Statement: string;
                export const ThemeId: string;
                export const TimeHorizon: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
                export const Version: string;
            }
            namespace ResearchReport {
                export function asKey(): typeof ResearchReport;
                export function asTry(): typeof ResearchReport;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const GeneratedAt: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const PublicationState: string;
                export const ResearchReportId: string;
                export const StableId: string;
                export const ThemeId: string;
                export const Title: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
                export const Version: string;
            }
            namespace SourceDocument {
                export function asKey(): typeof SourceDocument;
                export function asTry(): typeof SourceDocument;
                export const CaptureTime: string;
                export const ContentFingerprint: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const OriginalUrl: string;
                export const PublicationTime: string;
                export const Publisher: string;
                export const RightsNote: string;
                export const SourceDocumentId: string;
                export const SourceLevel: string;
                export const StableId: string;
                export const Title: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace TechnologyLink {
                export function asKey(): typeof TechnologyLink;
                export function asTry(): typeof TechnologyLink;
                export const Description: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Name: string;
                export const StableId: string;
                export const TechnologyLinkId: string;
                export const ThemeId: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
            namespace Theme {
                export function asKey(): typeof Theme;
                export function asTry(): typeof Theme;
                export const Description: string;
                export const EntityPlural: string;
                export const EntitySingular: string;
                export const InsertDate: string;
                export const InsertUserId: string;
                export const Name: string;
                export const StableId: string;
                export const ThemeId: string;
                export const UpdateDate: string;
                export const UpdateUserId: string;
            }
        }
    }
    export declare namespace Forms {
        export function asKey(): typeof Forms;
        export function asTry(): typeof Forms;
        namespace Membership {
            export function asKey(): typeof Membership;
            export function asTry(): typeof Membership;
            namespace Login {
                export function asKey(): typeof Login;
                export function asTry(): typeof Login;
                export const ForgotPassword: string;
                export const LoginToYourAccount: string;
                export const RememberMe: string;
                export const SignInButton: string;
                export const SignUpButton: string;
            }
            namespace SignUp {
                export function asKey(): typeof SignUp;
                export function asTry(): typeof SignUp;
                export const ActivateEmailSubject: string;
                export const ActivationCompleteMessage: string;
                export const ConfirmEmail: string;
                export const ConfirmPassword: string;
                export const DisplayName: string;
                export const Email: string;
                export const FormInfo: string;
                export const FormTitle: string;
                export const Password: string;
                export const SubmitButton: string;
                export const Success: string;
            }
        }
        export const SiteTitle: string;
    }
    export declare namespace Site {
        export function asKey(): typeof Site;
        export function asTry(): typeof Site;
        namespace AccessDenied {
            export function asKey(): typeof AccessDenied;
            export function asTry(): typeof AccessDenied;
            export const ClickToChangeUser: string;
            export const ClickToLogin: string;
            export const LackPermissions: string;
            export const NotLoggedIn: string;
            export const PageTitle: string;
        }
        namespace Layout {
            export function asKey(): typeof Layout;
            export function asTry(): typeof Layout;
            export const Language: string;
            export const Theme: string;
        }
        namespace RolePermissionDialog {
            export function asKey(): typeof RolePermissionDialog;
            export function asTry(): typeof RolePermissionDialog;
            export const DialogTitle: string;
            export const EditButton: string;
            export const SaveSuccess: string;
        }
        namespace UserDialog {
            export function asKey(): typeof UserDialog;
            export function asTry(): typeof UserDialog;
            export const EditPermissionsButton: string;
            export const EditRolesButton: string;
        }
        namespace UserPermissionDialog {
            export function asKey(): typeof UserPermissionDialog;
            export function asTry(): typeof UserPermissionDialog;
            export const DialogTitle: string;
            export const Grant: string;
            export const Permission: string;
            export const Revoke: string;
            export const SaveSuccess: string;
        }
        namespace ValidationError {
            export function asKey(): typeof ValidationError;
            export function asTry(): typeof ValidationError;
            export const Title: string;
        }
    }
    export declare namespace Validation {
        export function asKey(): typeof Validation;
        export function asTry(): typeof Validation;
        export const AuthenticationError: string;
        export const CurrentPasswordMismatch: string;
        export const DeleteForeignKeyError: string;
        export const EmailConfirm: string;
        export const EmailInUse: string;
        export const InvalidActivateToken: string;
        export const InvalidResetToken: string;
        export const MinRequiredPasswordLength: string;
        export const PasswordConfirmMismatch: string;
        export const SavePrimaryKeyError: string;
    }

}

const Texts: typeof texts = proxyTexts({}, '', {
    Db: {
        Administration: {
            Language: {},
            Role: {},
            RolePermission: {},
            User: {},
            UserPermission: {},
            UserRole: {}
        },
        Research: {
            Company: {},
            CompanyExposure: {},
            CompanyExposureEvidence: {},
            ConclusionEvidence: {},
            Event: {},
            Evidence: {},
            IndustryChain: {},
            IndustryChainNode: {},
            PhysicalModule: {},
            PhysicalPart: {},
            PhysicalPartIndustryChainNode: {},
            PhysicalPartTechnologyLink: {},
            ReportConclusion: {},
            ReportEvidence: {},
            ResearchConclusion: {},
            ResearchReport: {},
            SourceDocument: {},
            TechnologyLink: {},
            Theme: {}
        }
    },
    Forms: {
        Membership: {
            Login: {},
            SignUp: {}
        }
    },
    Site: {
        AccessDenied: {},
        Layout: {},
        RolePermissionDialog: {},
        UserDialog: {},
        UserPermissionDialog: {},
        ValidationError: {}
    },
    Validation: {}
}) as any;

export const AccessDeniedViewTexts = Texts.Site.AccessDenied;
export const LoginFormTexts = Texts.Forms.Membership.Login;
export const MembershipValidationTexts = Texts.Validation;
export const RolePermissionDialogTexts = Texts.Site.RolePermissionDialog;
export const SignUpFormTexts = Texts.Forms.Membership.SignUp;
export const SiteFormTexts = Texts.Forms;
export const SiteLayoutTexts = Texts.Site.Layout;
export const SqlExceptionHelperTexts = Texts.Validation;
export const UserDialogTexts = Texts.Site.UserDialog;
export const UserPermissionDialogTexts = Texts.Site.UserPermissionDialog;
export const ValidationErrorViewTexts = Texts.Site.ValidationError;