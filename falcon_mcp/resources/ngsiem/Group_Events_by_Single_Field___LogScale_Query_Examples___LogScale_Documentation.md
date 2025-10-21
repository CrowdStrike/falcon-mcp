# Group Events by Single Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-single-field-statuscode.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Group Events by Single Field

Basic grouping of events by status_code field using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(status_code)

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to group events based on unique values in specified fields, automatically providing a count of events for each group. 

This is similar to the `GROUP BY` method in SQL databases. 

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to execute aggregate functions on each group. The results are returned in the [_`field`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-field) parameter for each aggregate function. For example, the _count field if the [`count()`](https://library.humio.com/data-analysis/functions-count.html) function is used. The default is to use [`count()`](https://library.humio.com/data-analysis/functions-count.html) as an aggregate function, since the most common use-case is to count the distinct values of a field. 

If [`count()`](https://library.humio.com/data-analysis/functions-count.html) should not be used as an aggregate function, it is therefore necessary to add an empty list as the aggregate function to prevent something from being counted. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) is used to group events by their status codes to analyze the distribution of different response statuses. 

Example incoming data might look like this: 

@timestamp| status_code| endpoint| response_time  
---|---|---|---  
1686837825000| 200| /api/users| 145  
1686837826000| 404| /api/products| 89  
1686837827000| 200| /api/orders| 167  
1686837828000| 500| /api/payment| 890  
1686837829000| 200| /api/users| 156  
1686837830000| 404| /api/items| 78  
1686837831000| 200| /api/orders| 178  
1686837832000| 500| /api/checkout| 923  
1686837833000| 200| /api/products| 134  
1686837834000| 404| /api/users| 92  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(status_code)

Groups events by unique values in the status_code field. When used without any aggregate functions, [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) automatically creates a field named _count showing the number of events for each unique value. 

It is the same as: `groupBy(status_code, function=count())`

  3. Event Result set.




### Summary and Results

The query is used to analyze the distribution of status codes across all events. 

The _count field is automatically added to show the number of events in each group. 

This query is useful, for example, to monitor system health, identify error patterns, or track the frequency of different response types in a service. 

For other examples with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html), see [`groupBy()` Syntax Examples](https://library.humio.com/data-analysis/functions-groupby.html#functions-groupby-syntax-examples). 

Sample output from the incoming example data: 

status_code| _count  
---|---  
200| 5  
404| 3  
500| 2
