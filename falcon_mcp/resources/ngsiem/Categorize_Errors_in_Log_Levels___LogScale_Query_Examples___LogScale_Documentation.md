# Categorize Errors in Log Levels | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-if.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Categorize Errors in Log Levels

Categorize errors in log levels using the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function in combination with [`if()`](https://library.humio.com/data-analysis/functions-if.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    critical_status := if((in(status, values=["500", "404"])), then="Critical", else="Non-Critical")

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. It is possible to combine the [`in()`](https://library.humio.com/data-analysis/functions-in.html) with the [`if()`](https://library.humio.com/data-analysis/functions-if.html) function to categorize log level errors and their criticality. 

In this more advanced example, the [`if()`](https://library.humio.com/data-analysis/functions-if.html) function is used to categorize errors based on a time condition and it compares the status of a log level and decides on the log's criticality. The field critical_status is going to be evaluated based on the [`if()`](https://library.humio.com/data-analysis/functions-if.html) function. 

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
         
         critical_status := if((in(status, values=["500", "404"])), then="Critical", else="Non-Critical")

Searches for events where the field status contains the values `500` or `400` and assigns the value `Critical` to a field named critical_status for the returned results. If the values are not equal to `500` or `400`, then the returned events will have the value `Non-Critical` assigned to the field critical_status. 

  3. Event Result set.




### Summary and Results

The query is used to categorize errors in log levels according to their criticality. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user| critical_status  
---|---|---|---|---  
192.168.1.5| ERROR| 404| admin| Critical  
10.0.0.1| INFO| 200| user1| Non-Critical  
172.16.0.5| WARN| 422| user2| Non-Critical  
192.168.1.15| ERROR| 500| admin| Critical  
10.0.0.12| DEBUG| 302| user1| NonCritical
