# Searching with Field Aliasing | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-field-aliasing-search.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

/ [Field Aliasing](searching-data-field-aliasing.html)

### Searching with Field Aliasing

Field aliasing affects search behavior in the following ways: 

  * The aliased fields will exist on an event at search time, whenever the [tag conditions](searching-data-field-aliasing-configure.html#searching-data-field-aliasing-configure-step7) are met on the same event. 

  * The aliased fields contain the exact same data as the original field, and they behave identically to other fields when operating on them in the query language. 

  * If an event contains a field with the same name as an alias, then the alias will overshadow the existing field. 

  * [Keep original field?](searching-data-field-aliasing-configure.html "Configuring Field Aliasing") option (see [Figure 121, “Match fields and aliases”](searching-data-field-aliasing-configure.html#figure_searching-data-field-aliasing-configure7 "Figure 121. Match fields and aliases")): 

    * If **disabled** , only the alias can be searched. The original field is no longer searchable. 

    * If **enabled** , the original field will still be searchable. Source fields and aliases are independent copies — modifying one in a query will not affect the other: this means that existing queries that use the original/source field names will still continue to work. This behavior can, however, come at the cost of some performance. 




flowchart LR classDef behavior fill:#E6F3FF,stroke:#0066CC,stroke-width:2px A1[Tag conditions met on event] -->|Creates| A2[Aliased fields exist at search time] B1[Original fields] -->|Same data & behavior| B2[Aliased fields] C1[Original and alias have same name] -->|Results in| C2[Alias overshadows existing field] D1[Keep Original Field Option] --> D2{Enabled?} D2 -->|No| D3[Only alias searchable Original field not searchable] D2 -->|Yes| D4[Both fields searchable Independent copies Original queries work May impact performance] class A1,A2,B1,B2,C1,C2 behavior class D1,D2,D3,D4 option

**Figure 128. Field Aliasing Search**

  


#### Searches with Live Queries

Whenever you activate a schema or make changes to an existing active schema, these changes will take effect immediately, meaning any new search will use the new configuration. 

For existing running live queries (such as alerts, or an already opened dashboard), these queries need to be restarted in order for the new configuration to take effect. 

An exception to this rule is if the query contains a [`join()`](functions-join.html "join\(\)"), [`selfJoin()`](functions-selfjoin.html "selfJoin\(\)") or [`selfJoinFilter()`](functions-selfjoinfilter.html "selfJoinFilter\(\)") function: these will use the new configuration on their next refresh. See [Searches with Join Queries](searching-data-field-aliasing-search.html#searching-data-field-aliasing-search-joins "Searches with Join Queries") for more details. 

#### Searches with Join Queries

As described in [Join Operation and Optimization](query-joins-performance.html#summary_query-joins-performance), queries with join functions simulate liveness by executing in repeated intervals. For queries with join functions where field aliasing is enabled (that is, there is an active schema on the view where the query is executed), the latest configuration of schema and alias mappings are used on each repeated execution. 

Unlike live queries without joins (changes in the configuration does not impact an already running query) live queries using joins must be restarted at each schema or alias mappings configuration change. 

As [Join Query Functions](functions-join-functions.html "Join Query Functions") allow specifying the repository for which the subquery should execute, the subquery will use the field alias configuration of the specified repository. 

#### Searches in a Multi-Cluster Setup

Field aliasing can be used with [LogScale Multi-Cluster Search](https://library.humio.com/falcon-logscale-self-hosted/admin-multi-cluster.html). Only the schema active on the local cluster (either organization level or applied on the Multi-Cluster view) will be effective and applied to data from all remote views connected in the multi-cluster view. You can still use field aliasing on the remote clusters, however it will be effective only when searching the remote cluster directly. When running the search from the multi cluster view, schemas active on remote clusters will be ignored. 

If you want to apply different mappings for each remote cluster, _Multi-Cluster Views_ allow setting up an additional tag (#clusteridentity which is set to the value [Cluster identity tag](https://library.humio.com/falcon-logscale-self-hosted/admin-multi-cluster-creating-view-ui.html#admin-multi-cluster-creating-view-ui-view) when configuring a connection) that can be used in the [tag conditions](searching-data-field-aliasing-configure.html#searching-data-field-aliasing-configure-step7) of alias mappings. 

For more information, see [LogScale Multi-Cluster Search](https://library.humio.com/falcon-logscale-self-hosted/admin-multi-cluster.html) documentation. 

#### Searches with Query Prefixes

LogScale has several types of query prefixes that are implicitly added to any query; field aliasing cannot always be used with these query prefixes. This means that those filters will not work with aliased fields, which are disabled for those queries. Query prefixes are: 

Query Prefix |  Field Aliasing   
---|---  
View Connection filters, explained at [Views Filtering](https://library.humio.com/training/training-fc-repositories.html#training-fc-repositories-views) |  Disabled. Aliased fields cannot be accessed in the view connection filter.   
Deletion prefixes in [Redact Events API](https://library.humio.com/logscale-api/api-redact-events.html) |  Disabled. Aliased fields are not available in a filter query used with this API (it only operates on the parsed fields). If the same query is run on the Search page (for example, to check which events to delete before running the API) where field aliasing is set up, the search will produce different results. To avoid such a discrepancy, you may either disable the field aliasing configuration when running the query on search, or ensure you are not using aliased fields in the filter query executed through the API.   
Role/User query prefix, explained at [Assign Roles to Groups](https://library.humio.com/falcon-logscale-cloud/security-authorization-groups-assign-permission.html) |  Enabled. You can access aliased fields when you define a query prefix for the role/user filter query.
