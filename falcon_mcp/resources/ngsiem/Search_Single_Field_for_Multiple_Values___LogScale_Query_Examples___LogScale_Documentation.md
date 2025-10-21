# Search Single Field for Multiple Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-ordinary.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Single Field for Multiple Values

Search single field for multiple values using the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    in(status, values=["404","422"])

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. 

In this example, the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function is used to search for events in which the user received the HTTP codes `404` and `422`. 

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
         
         in(status, values=["404","422"])

Searches for events with the values `404` and `422` in the status field. If you want to search for all values starting with 4, it is possible to just use the query `in(status, values=["4*"])` \- here it is important to remember the double-quotes because of the wildcard usage. 

  3. Event Result set.




### Summary and Results

The query is used to search a single field for specific values. This is useful when monitoring events in which log messages contain error, warning, or other similar words in log entries, or perhaps specific numeric values in other fields. In this example, it selects logs with specific HTTP statuses. If you just want to search a single field for one specific value, use this query: `status = 404` instead of the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
192.168.1.5| ERROR| 404| admin  
172.16.0.5| WARN| 422| user2
