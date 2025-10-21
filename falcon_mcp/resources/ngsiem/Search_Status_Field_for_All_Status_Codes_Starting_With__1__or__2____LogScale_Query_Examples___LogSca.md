# Search Status Field for All Status Codes Starting With "1" or "2" | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-wildcard.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Status Field for All Status Codes Starting With "1" or "2"

Use a wildcard with [`in()`](https://library.humio.com/data-analysis/functions-in.html) to select all status codes starting with `"1"` or `"2"`

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    in(status, values=["1*", "2*"])

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. 

It is possible to use wildcards with the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function to select for example all status codes starting with "1" or "2". Notice that `""` must be used around the `*`. 

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
         
         in(status, values=["1*", "2*"])

Returns all events in which the status has a value starting with either `1` or `2`. Notice that since the wildcard is used, the double-quotes is required. 

  3. Event Result set.




### Summary and Results

The query is used to search status field for status codes starting with a given integer. 

Sample output from the incoming example data: 

srcIP| loglevel| status| user  
---|---|---|---  
10.0.0.1| INFO| 200| user1
