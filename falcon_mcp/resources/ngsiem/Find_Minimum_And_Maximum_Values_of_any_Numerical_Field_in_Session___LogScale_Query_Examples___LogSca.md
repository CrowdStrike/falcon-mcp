# Find Minimum And Maximum Values of any Numerical Field in Session | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-session-count-bet.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Find Minimum And Maximum Values of any Numerical Field in Session

Find minimum and maximum values of any numerical field in a session using the [`session()`](https://library.humio.com/data-analysis/functions-session.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    groupBy(cookie_id, function=session([max(bet),min(bet)]))

### Introduction

The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function can be used to group related events into sessions. 

A session contains events that occur within a specified time interval. By default, this interval is 15 minutes. You can modify this interval by setting the [_`maxpause`_](https://library.humio.com/data-analysis/functions-session.html#query-functions-session-maxpause) parameter. 

The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function then calculates aggregate values across all events in each session. 

In this example, the [`session()`](https://library.humio.com/data-analysis/functions-session.html) function is used to find minimum and maximum values of the field bet in a session. The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function groups events by a given timespan. 

Example incoming data might look like this: 

timestamp| cookie_id| bet| action_type| category  
---|---|---|---|---  
2025-05-15 05:30:00| user123| 25.99| purchase| electronics  
2025-05-15 05:32:00| user123| 49.99| purchase| electronics  
2025-05-15 05:34:00| user123| 15.99| purchase| accessories  
2025-05-15 05:48:00| user123| 99.99| purchase| appliances  
2025-05-15 05:49:00| user123| 150.00| purchase| furniture  
2025-05-15 05:35:00| user456| 75.50| purchase| clothing  
2025-05-15 05:37:00| user456| 199.99| purchase| appliances  
2025-05-15 05:40:00| user456| 89.99| purchase| electronics  
2025-05-15 05:30:00| user789| 10.99| purchase| books  
2025-05-15 05:55:00| user789| 20.99| purchase| books  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(cookie_id, function=session([max(bet),min(bet)]))

Groups events by the field cookie_id (unique user identifier) and creates sessions of 15-minutes timeout (the default value of the [_`maxpause`_](https://library.humio.com/data-analysis/functions-session.html#query-functions-session-maxpause) parameter), then calculates the maximum and minimum values of the field bet for each session, returning the results in new fields named _max and _min. 

  3. Event Result set.




### Summary and Results

The query is used to analyze the likelihood (the bet) of the behavior within user sessions. This query is, for example, useful for identifying if the event was an attempt to hack the system. 

Sample output from the incoming example data: 

cookie_id| _max| _min  
---|---|---  
user123| 49.99| 15.99 // First session  
user123| 150.00| 99.99 // Second session  
user456| 199.99| 75.50 // Single session  
user789| 10.99| 10.99 // First session  
user789| 20.99| 20.99 // Second session  
  
Note that each session shows its own min/max values.
