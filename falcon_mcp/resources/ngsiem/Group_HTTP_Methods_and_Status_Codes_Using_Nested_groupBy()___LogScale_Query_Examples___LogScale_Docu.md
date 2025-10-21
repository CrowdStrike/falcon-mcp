# Group HTTP Methods and Status Codes Using Nested groupBy()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-nested-http-methods-total.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Group HTTP Methods and Status Codes Using Nested [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html)

Analyze HTTP traffic patterns by method and status code using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(method, function=[count(as=method_total), groupBy(statuscode, function=count(as=method_status_count))])

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to group events by one or more fields and perform aggregate calculations on each group. When nested within another [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html), it enables multi-level grouping and analysis. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to analyze HTTP traffic patterns by grouping requests first by HTTP method and then by status code within each method. 

Example incoming data might look like this: 

@timestamp| method| statuscode| path| bytes  
---|---|---|---|---  
2025-08-06T10:00:00Z| GET| 200| /index.html| 1024  
2025-08-06T10:00:01Z| POST| 201| /api/users| 512  
2025-08-06T10:00:02Z| GET| 404| /missing.html| 256  
2025-08-06T10:00:03Z| GET| 200| /about.html| 768  
2025-08-06T10:00:04Z| POST| 400| /api/users| 128  
2025-08-06T10:00:05Z| PUT| 200| /api/users/1| 384  
2025-08-06T10:00:06Z| GET| 200| /contact.html| 896  
2025-08-06T10:00:07Z| DELETE| 204| /api/users/2| 0  
2025-08-06T10:00:08Z| GET| 500| /error.html| 1024  
2025-08-06T10:00:09Z| POST| 201| /api/orders| 756  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(method, function=[count(as=method_total), groupBy(statuscode, function=count(as=method_status_count))])

Groups events by the [method](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-request.html) field and performs two aggregations: 

     * Counts total events for each HTTP method using [`count()`](https://library.humio.com/data-analysis/functions-count.html), and returns the result in a new field named method_total. 

     * Creates a nested grouping by statuscode within each method group, counting occurrences using [`count()`](https://library.humio.com/data-analysis/functions-count.html) and returns the result in a new field named method_status_count. 

  3. Event Result set.




### Summary and Results

The query is used to analyze HTTP traffic patterns by providing a hierarchical view of request methods and their associated status codes. 

This query is useful, for example, to identify patterns in API usage, detect potential issues with specific HTTP methods, or monitor the distribution of success and error responses across different request types. 

Sample output from the incoming example data: 

method| method_total| statuscode| method_status_count  
---|---|---|---  
GET| 5| 200| 3  
GET| 5| 404| 1  
GET| 5| 500| 1  
POST| 3| 201| 2  
POST| 3| 400| 1  
PUT| 1| 200| 1  
DELETE| 1| 204| 1  
  
Note that the output shows the total count for each HTTP method in method_total and a breakdown of status codes and their counts within each method in method_status_count. 

This data is well-suited for visualization using a Sankey diagram widget, which can effectively show the flow from HTTP methods to status codes.
