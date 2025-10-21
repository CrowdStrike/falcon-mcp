# Analyze User Sessions Based on Click Activity | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-session-visitors-sort.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Analyze User Sessions Based on Click Activity

Analyzes user sessions based on users click activity using the [`session()`](https://library.humio.com/data-analysis/functions-session.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))
    | sort(clicks)

### Introduction

The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function can be used to group related events into sessions. 

A session contains events that occur within a specified time interval. By default, this interval is 15 minutes. You can modify this interval by setting the [_`maxpause`_](https://library.humio.com/data-analysis/functions-session.html#query-functions-session-maxpause) parameter. 

The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function then calculates aggregate values across all events in each session. 

In this example, the [`session()`](https://library.humio.com/data-analysis/functions-session.html) function is used to analyze user sessions based on users click activity. The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function groups events by a given timespan. 

Example incoming data might look like this: 

timestamp| cookie_id| action_type| page_url| user_agent  
---|---|---|---|---  
2025-05-15 05:30:00| user123| pageview| /home| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:15| user123| click| /products| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:30| user123| click| /product/item1| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:00| user123| click| /cart| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:30| user123| click| /checkout| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:35:00| user456| pageview| /home| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:35:30| user456| click| /about| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:36:00| user456| click| /contact| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:38:00| user789| pageview| /home| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
2025-05-15 05:38:30| user789| click| /products| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))

Groups events by the field cookie_id (unique user identifier) and creates sessions with 15-minute inactivity timeout (the default value of the [_`maxpause`_](https://library.humio.com/data-analysis/functions-session.html#query-functions-session-maxpause) parameter), then makes a count of each event in a session returning the result in a new field named clicks. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | sort(clicks)

Sorts the results by number of clicks (default is descending order). 

  4. Event Result set.




### Summary and Results

The query is used to analyze user sessions based on the users click activity. The query is useful, for example, to identify most/least active user sessions, detect potential automated behavior or just to understand user engagement levels. 

Sample output from the incoming example data: 

cookie_id| clicks  
---|---  
user123| 5  
user456| 3  
user789| 2  
  
Note that each row represents an event (either pageview or click).
