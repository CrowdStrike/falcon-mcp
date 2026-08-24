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

        NOTE: FQL filter field names are snake_case (insights.boolean_value) — do NOT
        write them as camelCase (insights.booleanValue). Insight ID values used in
        insights.id: remain camelCase (e.g. insights.id:'publiclyExposedToTheInternet').

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
        (e.g. publiclyExposedAccessRange, publiclyExposedExposureMethod).

        Substring match requires the :* operator with wildcards on both sides.
        A trailing-only wildcard ('Global*') returns nothing, and the ~ operator
        is rejected outright on this endpoint.

        Ex: insights.string_value:'Global Access'
        Ex: insights.string_value:*'*Internet*'
        """,
    ),
    (
        "insights.integer_value",
        "Number",
        """
        Filter assets where at least one insight has the given integer value.
        Maps to the `value` field in output when the insight stores an integer.

        Ex: insights.integer_value:>0
        Ex: insights.integer_value:>=5
        """,
    ),
    (
        "insights.date_value",
        "Timestamp",
        """
        Filter assets where at least one insight has the given date value.
        Maps to the `value` field in output when the insight stores a date.
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
        (e.g. identityAssumableByService, enabledLoggingSources, identityExternallyAssumableBy).
        Matches if the list contains the specified value exactly — pass one member, not a list.

        Ex: insights.string_list_value:'ssm.amazonaws.com'
        Ex: insights.string_list_value:'Cloud Logging Scope'
        """,
    ),
    (
        "cloud_provider",
        "String",
        """
        Filter by cloud provider. Matches the `cloud_provider` field in output.
        Use lowercase — it is the value the API returns, and the only spelling that
        works across every cloud tool.

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
the catalog so only assets with insights are returned. The response then carries
`auto_filter_applied: true` and `auto_filter_insight_count` instead of `filter_used`,
since you did not supply a filter.

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

Most insights are boolean. To find the right filter field for a specific insight,
query it by ID first and look at the `value` type in the response.

IMPORTANT: FQL filter field names are snake_case (e.g. insights.boolean_value),
Insight ID values in insights.id: are in camelCase (e.g. insights.id:'publiclyExposedToTheInternet').

=== The `category` field in search output is always null ===

Each entry in a search result's `insights` array carries `category: null`. The
per-insight category lives in the Policy Framework catalog, not on the asset record,
so resolving it during a search would add a round-trip to every query. To map an
insight_id to its category, call list_cloud_insight_definitions — its entries carry
the real category. The six categories are Identity, Network, Vulnerabilities, Data,
AI and Application.

=== Sorting ===

Pass `sort` as `field.asc` or `field.desc`. The pipe form (`field|desc`) is
equivalent. An invalid sort field is rejected with an error naming the valid ones,
so a sort is never silently ignored — but note the direction suffix is
case-sensitive: `updated_at.DESC` is an error.

Asset fields commonly worth sorting on:

| Field           | Notes                                            |
|-----------------|--------------------------------------------------|
| updated_at      | Most recently changed assets first with .desc    |
| creation_time   | Asset creation time                              |
| first_seen      | When the asset was first observed                |
| resource_name   | Alphabetical by asset name                       |
| account_id      | Group by cloud account                           |
| account_name    | Group by cloud account name                      |
| cloud_provider  | Group by provider                                |
| resource_type   | Group by resource type                           |
| region          | Group by region                                  |
| service         | Group by cloud service                           |

Three insight fields are also sortable, and only these three:

  publiclyExposedToTheInternet
  publiclyExposedAccessRange
  publiclyExposedExposureMethod

**Any other insight ID is NOT a valid sort field.** `identityIsAdmin.desc` returns an
error even though `insights.id:'identityIsAdmin'` is a perfectly good filter — the
filterable and sortable field sets are different. `severity` is another example: a
valid filter field, not a valid sort field.

Ex: sort="updated_at.desc"
Ex: sort="publiclyExposedToTheInternet.desc"   # exposed assets first

=== falcon_search_cloud_insights FQL filter examples ===

For any question about a security property that is not obviously covered by a known
insight_id, call list_cloud_insight_definitions first to discover the correct IDs.
The examples below show only a few representative IDs per category — the actual catalog
contains many more. Always discover IDs from the catalog rather than guessing.

--- Network category ---
# Find publicly exposed assets (boolean insight)
insights.id:'publiclyExposedToTheInternet'+insights.boolean_value:true

# Find assets with internet-facing exposure (string value, substring match)
insights.string_value:*'*Internet*'

# Find assets open to the full internet by access range
insights.id:'publiclyExposedAccessRange'+insights.string_value:'Internet (0.0.0.0/0)'

# Rank exposed assets, most exposed first (one of the three sortable insight fields)
insights.id:'publiclyExposedToTheInternet'   with sort="publiclyExposedToTheInternet.desc"

--- Identity category ---
# Find admin identities
insights.id:'identityIsAdmin'+insights.boolean_value:true

# Find unused identities
insights.id:'unusedIdentity'+insights.boolean_value:true

# Find identities with unrotated credentials
insights.id:'identityUnrotatedAccessKeys'+insights.boolean_value:true

# Find identities assumable by a specific AWS service (string list insight)
insights.string_list_value:'ssm.amazonaws.com'

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
# Pass one list member, not a list. Discover the members an insight actually holds by
# querying it by ID first and reading the `value` arrays.
insights.id:'llmModelsUsed'+insights.string_list_value:'claude-sonnet-4-20250514'

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
