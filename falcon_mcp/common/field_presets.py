"""Curated SOC field presets for token-optimized response shaping.
Each preset defines the investigation-essential fields for a specific entity type.
Used by view="summary" (default) to strip responses to signal-only output.
"""

DETECTION_SUMMARY_FIELDS: list[str] = [
    "timestamp", "created_timestamp", "updated_timestamp", "status", "severity_name",
    "confidence", "display_name", "description", "mitre_attack",
    "device.device_id", "device.hostname", "device.local_ip", "device.external_ip",
    "device.os_version", "device.tags",
    "user_name", "user_principal", "filename", "filepath", "cmdline",
    "parent_details.filename", "parent_details.cmdline", "grandparent_details.filename",
    "detection_context.target_file_name", "pattern_disposition_description",
]

HOST_SUMMARY_FIELDS: list[str] = [
    "device_id", "hostname", "local_ip", "external_ip", "platform_name",
    "os_version", "os_build", "product_type_desc", "status", "last_seen",
    "first_seen", "last_reboot", "last_login_timestamp", "last_login_user",
    "last_login_user_sid", "machine_domain", "site_name", "tags", "criticality",
    "filesystem_containment_status", "rtr_state", "agent_version",
    "device_policies.sensor_update.uninstall_protection", "device_policies.prevention.applied",
]

PROCESS_TELEMETRY_FIELDS: list[str] = [
    "@timestamp", "ComputerName", "aid", "TargetProcessId", "RawProcessId",
    "ParentProcessId", "RpcClientProcessId", "UserName", "UserSid", "AuthenticationId",
    "SessionId", "FileName", "FilePath", "ImageFileName", "CommandLine",
    "ParentBaseFileName", "SHA256HashData", "MD5HashData", "AuthenticodeHashData",
    "SignInfoFlags", "IntegrityLevel", "TokenType", "ProcessStartTime", "ProcessEndTime",
]

LOGON_TELEMETRY_FIELDS: list[str] = [
    "@timestamp", "ComputerName", "aid", "UserName", "UserPrincipal", "UserSid",
    "LogonDomain", "LogonType", "AuthenticationPackage", "AuthenticationId",
    "UserIsAdmin", "RemoteAccount", "ClientComputerName", "RemoteAddressIP4",
    "LocalAddressIP4", "UserLogonFlags", "UserGroupsBitmask", "PrivilegesBitmask",
    "EnabledPrivilegesBitmask", "ContextProcessId", "LogonTime",
]

NETWORK_TELEMETRY_FIELDS: list[str] = [
    "@timestamp", "ComputerName", "aid", "ContextProcessId", "ContextBaseFileName",
    "LocalAddressIP4", "LocalPort", "RemoteAddressIP4", "RemotePort",
    "RemoteAddressString", "Protocol", "ConnectionDirection", "ConnectionFlags",
    "InContext", "CommunityID", "UserName", "event_simpleName", "Technique",
    "TechniqueId", "Tactic",
]

FILE_DETECTION_CONTEXT_FIELDS: list[str] = [
    "@timestamp", "ComputerName", "aid", "UserName", "UserSid", "TargetProcessId",
    "TreeId", "TreeRoot", "PatternId", "DetectName", "DetectDescription",
    "DetectSeverity", "DetectScenario", "PatternDisposition", "DetectionContext",
    "EventCorrelationId", "TemplateInstanceId", "ProcessBehavioralContext",
    "ParentProcessBehavioralContext", "GrandparentProcessBehavioralContext",
]

PE_METADATA_FIELDS: list[str] = [
    "@timestamp", "ComputerName", "aid", "TargetProcessId", "FileName", "FilePath",
    "ImageFileName", "OriginalFilename", "CompanyName", "FileVersion",
    "FixedFileVersion", "SHA256HashData", "MD5HashData", "AuthenticodeHashData",
    "SignInfoFlags", "LanguageId",
]

ENTRA_SIGNIN_FIELDS: list[str] = [
    "@timestamp", "user.email", "Vendor.appDisplayName", "Vendor.resourceDisplayName",
    "Vendor.clientAppUsed", "Vendor.isInteractive", "source.ip",
    "Vendor.location.city", "Vendor.location.countryOrRegion",
    "#event.outcome", "Vendor.status.errorCode", "Vendor.status.additionalDetails",
    "Vendor.conditionalAccessStatus", "Vendor.appliedConditionalAccessPolicies",
    "Vendor.riskState", "Vendor.riskLevelDuringSignIn",
    "Vendor.deviceDetail.displayName", "Vendor.deviceDetail.isManaged",
    "Vendor.deviceDetail.isCompliant", "Vendor.correlationId",
]

ZSCALER_ZIA_FIELDS: list[str] = [
    "@timestamp", "Vendor.user", "Vendor.department", "Vendor.locationname",
    "Vendor.devicehostname", "Vendor.deviceowner", "Vendor.tuntype",
    "Vendor.csip", "Vendor.ssip", "Vendor.tsip",
    "destination.ip", "destination.port", "network.protocol", "network.application",
    "Vendor.nwsvc", "Vendor.action", "Vendor.rulelabel",
    "Vendor.ipcat", "Vendor.threatcat", "Vendor.threatname",
]

AWS_CLOUDTRAIL_FIELDS: list[str] = [
    "@timestamp", "event.provider", "event.action", "event.outcome",
    "cloud.account.id", "cloud.region", "user.name",
    "aws.userIdentity.type", "aws.userIdentity.arn",
    "aws.userIdentity.sessionContext.sessionIssuer.arn",
    "source.ip", "user_agent.original",
    "aws.requestParameters.roleName", "aws.requestParameters.policyDocument",
    "aws.errorCode", "aws.errorMessage", "event.id", "@ingesttimestamp",
]

AWS_GUARDDUTY_FIELDS: list[str] = [
    "@timestamp", "cloud.account.id", "cloud.region",
    "Vendor.findingType", "Vendor.severity", "Vendor.title",
    "Vendor.resource.accessKeyDetails.userName",
    "Vendor.resource.accessKeyDetails.principalId",
    "Vendor.service.action.actionType",
    "Vendor.service.action.awsApiCallAction.api",
    "Vendor.service.action.awsApiCallAction.serviceName",
    "Vendor.service.action.awsApiCallAction.remoteIpDetails.ipAddressV4",
    "Vendor.service.action.awsApiCallAction.remoteIpDetails.organization.asn",
    "Vendor.service.action.awsApiCallAction.remoteIpDetails.organization.org",
    "Vendor.service.eventFirstSeen", "Vendor.service.eventLastSeen",
    "Vendor.service.count", "Vendor.id",
]
