# Group HTTP Methods and Count Status Codes | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-nested-count-nested-groupby.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Group HTTP Methods and Count Status Codes

Analyze HTTP traffic patterns using nested [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(method, function=[count(as=method_total),
            groupBy(statuscode, function=count(as=method_status_count))])

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to group events by one or more fields and perform aggregate functions on each group. When nested, it enables multi-level analysis of data relationships. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to analyze HTTP traffic patterns by grouping requests first by HTTP method and then by status code, providing counts at both levels. 

Example incoming data might look like this: 

@timestamp| method| statuscode| path| bytes  
---|---|---|---|---  
2025-08-06T10:00:00Z| GET| 200| /index.html| 1024  
2025-08-06T10:00:01Z| POST| 201| /api/users| 512  
2025-08-06T10:00:02Z| GET| 404| /missing.html| 256  
2025-08-06T10:00:03Z| GET| 200| /about.html| 768  
2025-08-06T10:00:04Z| POST| 400| /api/users| 128  
2025-08-06T10:00:05Z| PUT| 200| /api/users/1| 896  
2025-08-06T10:00:06Z| GET| 200| /contact.html| 645  
2025-08-06T10:00:07Z| POST| 201| /api/orders| 789  
2025-08-06T10:00:08Z| GET| 404| /old-page.html| 234  
2025-08-06T10:00:09Z| DELETE| 204| /api/users/2| 0  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(method, function=[count(as=method_total),
                 groupBy(statuscode, function=count(as=method_status_count))])

Groups events first by the [method](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field and performs two functions: 

     * Counts the total number of events for each HTTP method using [`count()`](https://library.humio.com/data-analysis/functions-count.html) and returns the result in a new field named method_total. 

     * Creates a nested grouping by statuscode within each method group, counting occurrences using [`count()`](https://library.humio.com/data-analysis/functions-count.html) and returns the result in a new field named method_status_count. 

  3. Event Result set.




### Summary and Results

The query is used to analyze HTTP traffic patterns by providing a hierarchical view of request methods and their associated status codes. 

This query is useful, for example, to identify patterns in API usage, detect potential issues with specific HTTP methods, or monitor the distribution of success and error responses across different request types. 

Sample output from the incoming example data: 

method| method_total| statuscode| method_status_count  
---|---|---|---  
GET| 5| 200| 3  
GET| 5| 404| 2  
POST| 3| 201| 2  
POST| 3| 400| 1  
PUT| 1| 200| 1  
DELETE| 1| 204| 1  
  
Note that the output shows both the total count per method (method_total) and the breakdown of status codes (method_status_count) within each method, providing a comprehensive view of the HTTP traffic distribution. 

This data would be effectively visualized using a Sankey diagram widget to show the flow from HTTP methods to status codes, or a nested pie chart to display the distribution.
