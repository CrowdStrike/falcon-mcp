"""
Contains Cloud Insights resources.
"""

from falcon_mcp.common.fql import FQL_BASE_OPERATORS
from falcon_mcp.common.utils import generate_md_table

FQL_DOCUMENTATION = FQL_BASE_OPERATORS

CLOUD_INSIGHTS_FQL_FILTERS = [
    ("Name", "Type", "Description"),
    (
        "insights.id",
        "String",
        """
        Filter assets to those carrying a specific insight ID. Supports single value or list (OR).
        To filter by category, first call list_cloud_insight_definitions to get the insight_ids
        for that category, then pass them here.

        Ex: insights.id:'publiclyExposedToTheInternet'
        Ex: insights.id:['publiclyExposedToTheInternet', 'identityIsAdmin']

        Category workflow:
          1. list_cloud_insight_definitions(categories=['Network'])
             -> returns entries with insight_id values
          2. filter="insights.id:['id1','id2',...]"
        """,
    ),
    (
        "insights.boolean_value",
        "Boolean",
        """
        Filter assets where at least one insight has the given boolean value.
        Maps to the `value` field in output when the insight stores a boolean
        (e.g. identityIsAdmin, publiclyExposedToTheInternet).

        NOTE: FQL filter field names use snake_case (insights.boolean_value),
        while the response payload uses camelCase (booleanValue). These are the same field.

        NOTE: Asset-level semantics — insights.id:'X'+insights.boolean_value:true matches
        any asset that has insight X AND has at least one boolean-true insight. Those two
        conditions may be satisfied by different insight entries on the same asset.
        For precise per-entry filtering combine this with insights.id.

        Ex: insights.boolean_value:true
        Ex: insights.id:'identityIsAdmin'+insights.boolean_value:true
        """,
    ),
    (
        "insights.string_value",
        "String",
        """
        Filter assets where at least one insight has the given string value.
        Maps to the `value` field in output when the insight stores a string
        (e.g. publiclyExposedAccessRange). Supports wildcards.

        Ex: insights.string_value:'Internet (0.0.0.0/0)'
        Ex: insights.string_value:*'*Internet*'
        """,
    ),
    (
        "insights.integer_value",
        "Number",
        """
        Filter assets where at least one insight has the given integer value.
        Maps to the `value` field in output when the insight stores an integer
        (e.g. groupsMembers). Supports comparison operators.

        Ex: insights.integer_value:>0
        Ex: insights.integer_value:>=5
        """,
    ),
    (
        "insights.date_value",
        "Timestamp",
        """
        Filter assets where at least one insight has the given date value.
        Maps to the `value` field in output when the insight stores a date
        (e.g. accessKeyLastRotated). Supports comparison operators.
        Use ISO-8601 format.

        Ex: insights.date_value:<'2025-01-01T00:00:00Z'
        Ex: insights.date_value:>'2024-06-01T00:00:00Z'
        """,
    ),
    (
        "insights.string_list_value",
        "String",
        """
        Filter assets where at least one insight has a list value containing the given member.
        Maps to the `value` field in output when the insight stores a list of strings
        (e.g. llmModelsUsed). Matches if the list contains the specified value.

        Ex: insights.string_list_value:'claude-sonnet-4-20250514'
        """,
    ),
    (
        "cloud_provider",
        "String",
        """
        Filter by cloud provider. Matches the `cloud_provider` field in output.

        Ex: cloud_provider:'aws'
        Ex: cloud_provider:['aws', 'azure']
        """,
    ),
    (
        "account_id",
        "String",
        """
        Filter by cloud account ID.

        Ex: account_id:'123456789012'
        """,
    ),
    (
        "resource_type",
        "String",
        """
        Filter by cloud resource type.

        Ex: resource_type:'AWS::S3::Bucket'
        Ex: resource_type:*'*EC2*'
        """,
    ),
    (
        "region",
        "String",
        """
        Filter by cloud region.

        Ex: region:'us-east-1'
        """,
    ),
]

CLOUD_INSIGHTS_FQL_DOCUMENTATION = (
    FQL_DOCUMENTATION
    + """
=== falcon_search_cloud_insights FQL filter available fields ===

The `filter` parameter is the sole filter mechanism. Pass an `insights.id` filter to
scope by insight type or category. All filter fields operate at the ASSET level:
a condition matches if ANY insight entry on the asset satisfies it.

To filter by category:
  1. Call list_cloud_insight_definitions (optionally with categories=['Network']) to get insight_ids.
  2. Pass insights.id:['id1','id2'] in the filter param here.

NOTE: When filter is omitted, the tool automatically queries all known insight IDs from
the catalog so only assets with insights are returned.

"""
    + generate_md_table(CLOUD_INSIGHTS_FQL_FILTERS)
    + """

=== Value field → FQL filter field mapping ===

The `value` field in each insight record is polymorphic. The FQL filter field to use
depends on the insight's value type:

| Output `value` type | FQL filter field            |
|---------------------|-----------------------------|
| boolean             | insights.boolean_value      |
| string              | insights.string_value       |
| integer             | insights.integer_value      |
| date/timestamp      | insights.date_value         |
| list of strings     | insights.string_list_value  |

IMPORTANT: FQL filter field names are snake_case (insights.boolean_value), but the
response payload uses camelCase (booleanValue). Do not use camelCase in filters —
the API rejects them with HTTP 400.

=== falcon_search_cloud_insights FQL filter examples ===

For any question about a security property that is not obviously covered by a known
insight_id, call list_cloud_insight_definitions first to discover the correct IDs.
The examples below show one representative ID per category — the actual catalog
contains many more. Always discover IDs from the catalog rather than guessing.

--- Network category ---
# Find publicly exposed assets (boolean insight)
insights.id:'publiclyExposedToTheInternet'+insights.boolean_value:true

# Find assets with internet-facing exposure (string value)
insights.string_value:*'*Internet*'

# Find assets open to the full internet by access range
insights.id:'publiclyExposedAccessRange'+insights.string_value:'Internet (0.0.0.0/0)'

--- Identity category ---
# Find admin identities
insights.id:'identityIsAdmin'+insights.boolean_value:true

# Find identities where MFA is not enabled
# (call list_cloud_insight_definitions(categories=['Identity']) to get the exact ID)
insights.id:'identityMfaEnabled'+insights.boolean_value:false

# Find unused identities
insights.id:'unusedIdentity'+insights.boolean_value:true

# Find identities with unrotated credentials
insights.id:'identityUnrotatedAccessKeys'+insights.boolean_value:true

# Find identities with stale access keys (rotated before a date)
insights.id:'accessKey1LastRotated'+insights.date_value:<'2025-01-01T00:00:00Z'

# Find identities belonging to large groups
insights.id:'groupsMembers'+insights.integer_value:>5

--- Vulnerabilities category ---
# Find assets with reachable critical CVEs
# NOTE: falcon_search_cloud_risks reports aggregated risk severity; this tool reports
# the underlying per-asset vulnerability facts. Use this for "which assets have
# reachable CVEs"; use falcon_search_cloud_risks for overall risk posture/severity.
insights.id:'reachableCriticalVulnerabilities'+insights.boolean_value:true

# Find assets with reachable RCE vulnerabilities
insights.id:'reachableRceVulnerabilities'+insights.boolean_value:true

# Find assets without a Falcon sensor
insights.id:'hasSensor'+insights.boolean_value:false

--- Data category ---
# Find assets containing secrets
insights.id:'hasSecrets'+insights.boolean_value:true

# Find assets with sensitive data
insights.id:'hasSensitiveData'+insights.boolean_value:true

# Find assets where logging is not enabled
insights.id:'loggingEnabled'+insights.boolean_value:false

--- AI category ---
# Find resources using AI services
insights.id:'usesAiServices'+insights.boolean_value:true

# Find assets using a specific LLM model (string list insight)
insights.string_list_value:'claude-sonnet-4-20250514'

# Find assets exposing an MCP server interface
insights.id:'exposesMcpServerInterface'+insights.boolean_value:true

--- Application category ---
# Find apps with excessive actions
insights.id:'hasExcessiveActions'+insights.boolean_value:true

--- Cross-provider scoping ---
# Combine insight filter with cloud provider
insights.id:'identityIsAdmin'+insights.boolean_value:true+cloud_provider:'gcp'

# Combine insight filter with account
insights.id:'publiclyExposedToTheInternet'+insights.boolean_value:true+account_id:'158366397675'
"""
)
