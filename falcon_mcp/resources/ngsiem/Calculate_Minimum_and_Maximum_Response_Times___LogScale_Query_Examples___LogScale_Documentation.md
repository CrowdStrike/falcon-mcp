# Calculate Minimum and Maximum Response Times | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-min-max-response-squarebrackets.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Minimum and Maximum Response Times

Calculate minimum and maximum response times using multiple aggregate functions in square brackets 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    [min_response := min(responsetime), max_response := max(responsetime)]

### Introduction

The [`min()`](https://library.humio.com/data-analysis/functions-min.html) and [`max()`](https://library.humio.com/data-analysis/functions-max.html) functions can be used together to find the extreme values in an event set, with results assigned to specified field names. 

Square brackets allow multiple aggregations to be performed in a single operation. 

In this example, the [`min()`](https://library.humio.com/data-analysis/functions-min.html) and [`max()`](https://library.humio.com/data-analysis/functions-max.html) functions are used to find the shortest and longest response times, with results stored in named fields. 

Square brackets allow multiple aggregations to be performed in a single operation 

Writing a list of aggregators in square brackets is a shorthand syntax for the [`stats()`](https://library.humio.com/data-analysis/functions-stats.html) function. 

Example incoming data might look like this: 

@timestamp| endpoint| responsetime| status_code  
---|---|---|---  
1686837825000| /api/users| 145| 200  
1686837826000| /api/products| 892| 200  
1686837827000| /api/orders| 167| 200  
1686837828000| /api/payment| 1290| 500  
1686837829000| /api/users| 156| 200  
1686837830000| /api/items| 78| 200  
1686837831000| /api/orders| 934| 200  
1686837832000| /api/checkout| 923| 200  
1686837833000| /api/products| 134| 200  
1686837834000| /api/users| 445| 200  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         [min_response := min(responsetime), max_response := max(responsetime)]

In a single operation, calculates the minimum value from the responsetime field and returns the results in a field named min_response, and calculates the maximum value from the responsetime field and returns the results in a field named max_response. 

Square brackets allow multiple aggregations to be performed in a single operation 

  3. Event Result set.




### Summary and Results

The query is used to find the range of response times by calculating both the minimum and maximum values. 

The results are returned in fields with names specified in the field assignments 

This query is useful, for example, to monitor service performance, identify outliers in response times, or establish performance baselines. 

Sample output from the incoming example data: 

min_response| max_response  
---|---  
78| 1290  
  
Note that only one row is returned containing both calculated values.
