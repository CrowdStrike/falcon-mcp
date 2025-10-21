# Parse JSON Content With Specific Parameters

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsejson-specific-parameters.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

##  Parse JSON Content With Specific Parameters 

Parse JSON content with specific parameters while excluding the actual query content using the [`parseJson()`](https://library.humio.com/data-analysis/functions-parsejson.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2[/Filter/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #type=audit-log
    | /"type":"alert.update"/
    | parseJson(exclude="query", include="queryStart")

### Introduction

The [`parseJson()`](https://library.humio.com/data-analysis/functions-parsejson.html) function can be used to parse data or a field as JSON, converting the data into named fields and arrays within the event. It is possible to perform both path-based exclusion and array-based exclusion using the [_`exclude`_](https://library.humio.com/data-analysis/functions-parsejson.html#query-functions-parsejson-exclude) parameter (all non-nested fields are also excluded), but at the same time include some of the extracted fields using the [_`include`_](https://library.humio.com/data-analysis/functions-parsejson.html#query-functions-parsejson-include) parameter. 

Prefixes can also be defined - or removed - for a field name using the parameters [_`prefix`_](https://library.humio.com/data-analysis/functions-parsejson.html#query-functions-parsejson-prefix) or [_`removePrefixes`_](https://library.humio.com/data-analysis/functions-parsejson.html#query-functions-parsejson-removeprefixes). For more information, see [`parseJson()` Syntax Examples](https://library.humio.com/data-analysis/functions-parsejson.html#functions-parsejson-syntax-examples). 

In this example, the [`parseJson()`](https://library.humio.com/data-analysis/functions-parsejson.html) function is used to search audit logs for alert update events, specifically looking at the queryStart field (timestamp), while excluding the actual query content (query.xxx). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2[/Filter/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=audit-log

Filters for all events from repository `audit-log`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2[/Filter/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | /"type":"alert.update"/

Filters for events (audit logs) where the @rawstring field contains the string `/"type":"alert.update"/`. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2[/Filter/] 3[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseJson(exclude="query", include="queryStart")

With specific parameters set, parses the JSON content excluding the query field and including only the queryStart field. 

The exclusion works as a wildcard match for the given field; for example, the value `query` will match both nested fields (like query.string) and similarly non-nested named fields (like queryString, queryStart, and queryEnd). In this example, to retain the specific non-nested field queryStart while excluding the others, the [_`include`_](https://library.humio.com/data-analysis/functions-parsejson.html#query-functions-parsejson-include) parameter is used. 

  5. Event Result set.




### Summary and Results

The query is used to search audit logs for alert update events, specifically looking at the non-nested queryStart field, while excluding the actual query content (query.xxx). The query is useful if, for example, you want to review alert activity without the overhead of full query contents, track temporal patterns in alert updates, or investigate alert timing issues further.
