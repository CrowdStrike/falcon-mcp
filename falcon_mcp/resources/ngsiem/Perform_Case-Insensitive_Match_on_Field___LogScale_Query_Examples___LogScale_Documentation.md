# Perform Case-Insensitive Match on Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-caseinsensitive.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Perform Case-Insensitive Match on Field

Perform a case-insensitive match on field using [`in()`](https://library.humio.com/data-analysis/functions-in.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    in(loglevel, ignoreCase=true, values=["error", "warn"])

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. 

It is possible to perform case-insensitive searches on a field using the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function. In this example, the loglevel field is searched for occurrences of either `error` or `warning`. 

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
         
         in(loglevel, ignoreCase=true, values=["error", "warn"])

Returns all events in which the loglevel field has the value `error` or `warning`. As it is case-insensitive, it returns all occurrences of the specified values in all their variants, regardless of the case. 

  3. Event Result set.




### Summary and Results

The query is used to perform case-insensitive searches on a specific value in a given field. This is useful when searching for strings where values may appear in both both upper and lower case to ensure that all events are extracted. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
192.168.1.5| ERROR| 404| admin  
172.16.0.5| WARN| 422| user2  
192.168.1.15| ERROR| 500| admin
