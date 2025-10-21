# Exclude Events With Specific Values From Searches | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-exclude.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Exclude Events With Specific Values From Searches

Exclude events with specific values from searches using the negated function [`in()`](https://library.humio.com/data-analysis/functions-in.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    !in(loglevel, values=["ERROR", "WARN"])

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. 

It is possible to exclude events with specific values using the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function with a negation in front. In this example, events will be excluded from the search result if the loglevel field contains the values `ERROR` or `WARNING`. 

Example incoming data might look like this: 

Raw Events

srcIP=192.168.1.5 loglevel=ERROR status=404 user=admin  
---  
srcIP=10.0.0.1 loglevel=INFO status=200 user=user1  
srcIP=172.16.0.5 loglevel=WARN status=422 user=user2  
srcIP=192.168.1.15 loglevel=ERROR status=500 user=admin  
srcIP=10.0.0.12 loglevel=DEBUG status=302 user=user1  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         !in(loglevel, values=["ERROR", "WARN"])

Returns all events in which the loglevel field does not contain the value `ERROR` or `WARNING`. 

  3. Event Result set.




### Summary and Results

The query is used to exclude events with specific values from search results. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
10.0.0.1| INFO| 200| user1  
10.0.0.12| DEBUG| 302| user1
