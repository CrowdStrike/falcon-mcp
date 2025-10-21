# Assign End of Search Time Interval to Field - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-end-comparison.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Assign End of Search Time Interval to Field - Example 2

Assign the end of the search time interval to a field using the [`end()`](https://library.humio.com/data-analysis/functions-end.html) function in a comparison 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    isOld := (end()-@timestamp) > 1000

### Introduction

The [`end()`](https://library.humio.com/data-analysis/functions-end.html) function is used to assign the end of the search time interval to a field provided by the parameter [_`as`_](https://library.humio.com/data-analysis/functions-end.html#query-functions-end-as). The [`end()`](https://library.humio.com/data-analysis/functions-end.html) function is equivalent to the [`now()`](https://library.humio.com/data-analysis/functions-now.html) function — that is: the current time. 

In this example, the [`end()`](https://library.humio.com/data-analysis/functions-end.html) is used to compare the difference between the end time and the @timestamp field to determine if an event is "old" (more than 1000 milliseconds old). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         isOld := (end()-@timestamp) > 1000

Returns results where the current time minus the ingestion timestamp are greater than `1000`, and assigns the returned results to a new field named isOld. 

In more details: [`end()`](https://library.humio.com/data-analysis/functions-end.html) returns the end time of the search interval. @timestamp is the timestamp of the individual event.`(end()-@timestamp)` calculates the difference between these two times, giving the age of the event relative to the end of the search interval. This difference is compared to `1000` milliseconds (1 second). If the difference is greater than `1000` milliseconds, isOld will be set to `true`; otherwise, it will be `false`. 

  3. Event Result set.




### Summary and Results

The query is used to quickly identifying events that are more than 1 second older than the end of the search interval. Assigning end of search time interval to a field is useful when, for example, searching for security events. When doing a query, the events you are searching do not know the span of the search (the system just returns a list of the events in the given time interval), but you might want to show the relative time of the event timestamp compared to the search window. For example, if you search of a bunch of events that happened yesterday and you are searching from `yesterday 00:00 to 23:59`, you then want to calculate '3 hours before' or even '2s before' because when searching for security events that time difference may be important.
