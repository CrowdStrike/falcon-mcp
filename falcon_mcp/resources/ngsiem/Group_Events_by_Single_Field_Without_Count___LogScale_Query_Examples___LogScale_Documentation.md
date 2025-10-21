# Group Events by Single Field Without Count | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-single-field-emptylist.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Group Events by Single Field Without Count

Basic grouping of events by status_code field with explicit empty [_`function`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-function) parameter using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(status_code, function=[])

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to group events based on unique values in specified fields, with an optional [_`function`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-function) parameter to specify aggregate calculations. 

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function can be used to execute aggregate functions on each group. The results are returned in the [_`field`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-field) parameter for each aggregate function. For example, the _count field if the [`count()`](https://library.humio.com/data-analysis/functions-count.html) function is used. The default is to use [`count()`](https://library.humio.com/data-analysis/functions-count.html) as an aggregate function, since the most common use-case is to count the distinct values of a field. 

If [`count()`](https://library.humio.com/data-analysis/functions-count.html) should not be used as an aggregate function, it is therefore necessary to add an empty list as the aggregate function to prevent something from being counted. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) is used to group events by their status codes without calculating count. 

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
         
         groupBy(status_code, function=[])

Groups events by unique values in the status_code field. The empty function array ([_`function`_](https://library.humio.com/data-analysis/functions-groupby.html#query-functions-groupby-function)=`[]`) prevents automatic counting. 

This approach helps conserve memory while identifying the unique status codes in the events. 

  3. Event Result set.




### Summary and Results

The query is used to identify unique field values (in this case different status codes) while minimizing memory usage. 

This query is useful, for example, to quickly discover unique values in large event sets and support initial data exploration before detailed analysis. 

For other examples with [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html), see [`groupBy()` Syntax Examples](https://library.humio.com/data-analysis/functions-groupby.html#functions-groupby-syntax-examples). 

Sample output from the incoming example data: 

status_code  
---  
200  
404  
500
