# Field Aliasing | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/searching-data-field-aliasing.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Search Data](searching-data.html)

Content was updated:Sep 19, 2024

## Field Aliasing

##### Security Requirements and Controls

  *  _`Change field aliases`_ permission




Field Aliasing in LogScale applies custom data models at query time by assigning alternative names to parsed fields, making it easier to search and correlate data from different sources. The feature offers improved performance over traditional rename functions, supports historical data queries without parser changes, and can be implemented across an entire organization or specific repositories through a three-step process of creating schemas, defining field alias mappings, and activating the schema. 

_Field aliasing_ allows to apply any data model at query time, simplifying query writing and making it easier to search and correlate data originating from different sources. This functionality allows assigning alternative names — or _Aliases_ — to fields created at parse time. 

With field aliasing, the search will produce results similar to adding [`rename()`](functions-rename.html "rename\(\)") statements at the beginning of your queries — however, using field aliasing instead of [`rename()`](functions-rename.html "rename\(\)") will provide additional benefits: 

  * Ease of use: field aliasing is applied to each query, to simplify query writing. 

  * Performance: using field aliasing is more efficient than aliasing your fields with case-rename statements. 

  * Flexibility: 

    * As field aliasing is applied at search time, you can use it to query historical data. 

    * No changes in the parser are required when you want to apply a new schema (that is, your list of common aliases). 

  * Multiple application level for a variety of use cases and scenarios: 

    * Entire organization — if your organization uses one schema, you can set it up as a default for all repositories and views, including any new repositories/views created in the future. 

    * Selected repository/views — if you want to apply a schema to specific use cases only. 




### Warning

When a field is renamed to a field that already exists, the existing field and its content is overwritten by the new aliased field. If you wish to keep existing fields and prevent them from being overwritten, enable the [Keep original field?](searching-data-field-aliasing-configure.html "Configuring Field Aliasing") checkbox when [configuring field aliasing](searching-data-field-aliasing-configure.html "Configuring Field Aliasing"). 

Field overwriting also happens when the field is renamed using the [`rename()`](functions-rename.html "rename\(\)") function - even if the original field doesn't exist, it gets overwritten showing `NULL`. 

An example of field aliasing configured in the web interface is depicted here: 

![screenshot showing an example of Field Aliasing schema configured](images/search-data/field-aliasing.png)  
---  
  
**Figure 114. Field aliasing configuration**

  


Field aliasing configuration in LogScale is defined as a three-step process: 

  1. Create a new _Schema_. Schemas define a list of common aliases that you want to use in your queries. 

     * Aliases can be used instead of, or in addition to the original fields. 

     * Schemas can be applied on the organization or repository view level. 

     * You can still use event fields in your searches that are not included in the schema for aliasing. 

  2. Create _Field Alias Mappings_. Mappings define rules on how to map original field names to the aliases specified in the schema. A mapping contains: 

     * A pair of original (parsed) field name and its alias 

     * A condition when to apply the alias to the event (based on tag fields). 

  3. Activate the schema for the entire organization or selected repositories/views. 




The following diagram represents the process: 

graph TD subgraph "Schema // Aliasing to" D[source_ip_address] E[destination_ip_address] end subgraph "Field aliasing mapping // syslog events" F[ip_src] G[ip_dst] end subgraph "Field aliasing mapping // weblog events" H[source_ip] I[target_ip] end subgraph "Activated for // Scope" direction LR A[Repository A] B[Repository B] C[View C] end F -->|maps to| D G -->|maps to| E H -->|maps to| D I -->|maps to| E

**Figure 115. Field Aliasing Process**

  


For more information about field aliasing, see the following sections: 

  * [Configuring Field Aliasing](searching-data-field-aliasing-configure.html "Configuring Field Aliasing")

  * [Managing Field Aliasing](searching-data-field-aliasing-manage.html "Managing Field Aliasing")

  * [Searching with Field Aliasing](searching-data-field-aliasing-search.html "Searching with Field Aliasing")

  * [Understanding Field Mapping Requirements](searching-data-field-aliasing-mapping-requirements.html "Understanding Field Mapping Requirements")

  * [Understanding Schema Requirements](searching-data-field-aliasing-schema-requirements.html "Understanding Schema Requirements").
