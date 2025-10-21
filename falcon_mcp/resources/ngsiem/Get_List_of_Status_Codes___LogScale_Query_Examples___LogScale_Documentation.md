# Get List of Status Codes | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-groupby-list-statuscodes.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Get List of Status Codes

Get list of status codes returned and a count of each for a given period using the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function with [`count()`](https://library.humio.com/data-analysis/functions-count.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(field=status, function=count())

### Introduction

The [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to group together events by one or more specified fields. It is used to extract additional aggregations from the data and then add calculation to it using the [`count()`](https://library.humio.com/data-analysis/functions-count.html)function. 

In this example, the [`groupBy()`](https://library.humio.com/data-analysis/functions-groupby.html) function is used to get a list of status codes for logged events. For instance, the status code `200` is returned when the request is successful, and `404` when the page is not found. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(field=status, function=count())

Groups events by the status field, and counts the number of events in each group. 

It is possible to enhance the query for more detailed analysis. The following query example groups by both the fields status and source, limits to 1000 results, and sorts by count descending. `groupBy([field=status, field=source], function=count(), limit=1000) | sort(_count, order=desc)`

  3. Event Result set.




### Summary and Results

The query is used to extract a list of status codes, each with a count of how many events have that status. The query is useful for summarizing and analyzing log data. 

Sample output from the incoming example data: 

status| _count  
---|---  
101| 17  
200| 46183  
204| 3  
307| 1  
400| 2893  
401| 4  
Failure| 1  
Success| 8633
