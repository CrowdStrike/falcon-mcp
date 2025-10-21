# Create Frequency Count With Formatted Links | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-top-format-links.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create Frequency Count With Formatted Links

Transform field values into clickable links with occurrence count using the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function with [`format()`](https://library.humio.com/data-analysis/functions-format.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    top(repo)
    | format("[Link](https://example.com/%s)", field=repo, as=link)

### Introduction

The [`top()`](https://library.humio.com/data-analysis/functions-top.html) function can be used to count occurrences of field values and sort them by frequency, providing insights into the most common values in your data. 

In this example, the [`top()`](https://library.humio.com/data-analysis/functions-top.html) is used to count occurrences of repository names in the field [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html), followed by the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function to create clickable links for each repository. 

Example incoming data might look like this: 

@timestamp| repo| action| user  
---|---|---|---  
2023-06-15T10:00:00Z| frontend-app| push| alice  
2023-06-15T10:05:00Z| backend-api| clone| bob  
2023-06-15T10:10:00Z| frontend-app| pull| charlie  
2023-06-15T10:15:00Z| database-service| push| alice  
2023-06-15T10:20:00Z| frontend-app| pull| bob  
2023-06-15T10:25:00Z| backend-api| push| alice  
2023-06-15T10:30:00Z| monitoring-tool| clone| charlie  
2023-06-15T10:35:00Z| frontend-app| push| bob  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         top(repo)

Groups events by the [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field and counts their occurrences. Creates a result set with two fields: the repository name ([repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html)) and _count. Results are automatically sorted by count in descending order. If no limit is specified, the [`top()`](https://library.humio.com/data-analysis/functions-top.html) function returns all unique values. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | format("[Link](https://example.com/%s)", field=repo, as=link)

Creates formatted markdown-style links based on repository values in [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) and returns the results in a new field named link. 

The [_`field`_](https://library.humio.com/data-analysis/functions-format.html#query-functions-format-field) parameter specifies to use the [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field value in the formatting string (represented by `%s`). 

  4. Event Result set.




### Summary and Results

The query is used to analyze the frequency of repository interactions and create clickable links for each repository. 

This query is useful, for example, to create interactive reports showing which repositories are most actively used, or to build dashboards where users can quickly access frequently accessed repositories. 

Sample output from the incoming example data: 

repo| _count| link  
---|---|---  
frontend-app| 4| [Link](https://example.com/ frontend-app)  
backend-api| 2| [Link](https://example.com/ backend-api)  
monitoring-tool| 1| [Link](https://example.com/ monitoring-tool)  
database-service| 1| [Link](https://example.com/ database-service)  
  
Note that the results are automatically sorted by count in descending order, showing the most frequently accessed repositories first. The original field value is preserved in the [repo](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field while the formatted link is available in the link field.
