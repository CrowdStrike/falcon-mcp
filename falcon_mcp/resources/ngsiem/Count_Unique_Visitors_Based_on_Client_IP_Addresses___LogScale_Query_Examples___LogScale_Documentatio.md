# Count Unique Visitors Based on Client IP Addresses | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-session-count-visitor.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Count Unique Visitors Based on Client IP Addresses

Count unique visitors based on client IP addresses using the [`session()`](https://library.humio.com/data-analysis/functions-session.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    groupBy(client_ip, function=session(maxpause=15m))
    | count()

### Introduction

The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function can be used to group related events into sessions. 

A session contains events that occur within a specified time interval. By default, this interval is 15 minutes. You can modify this interval by setting the [_`maxpause`_](https://library.humio.com/data-analysis/functions-session.html#query-functions-session-maxpause) parameter. 

The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function then calculates aggregate values across all events in each session. 

In this example, the [`session()`](https://library.humio.com/data-analysis/functions-session.html) function is used to count the unique visitors (each visitor defined as non-active for 15 minutes) of a site based on client IP addresses. The [`session()`](https://library.humio.com/data-analysis/functions-session.html) function groups events by a given timespan. 

Example incoming data might look like this: 

timestamp| client_ip| url| status_code| user_agent  
---|---|---|---|---  
2025-05-15 05:30:00| 192.168.1.100| /login| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:31:15| 192.168.1.100| /dashboard| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:32:30| 192.168.1.100| /reports| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:48:00| 192.168.1.100| /login| 200| Mozilla/5.0 (Windows NT 10.0; Win64; x64)  
2025-05-15 05:30:05| 192.168.1.101| /login| 200| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:35:10| 192.168.1.101| /profile| 200| Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)  
2025-05-15 05:40:00| 192.168.1.102| /login| 200| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
2025-05-15 05:41:30| 192.168.1.102| /settings| 200| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
2025-05-15 05:42:45| 192.168.1.102| /logout| 200| Mozilla/5.0 (iPhone; CPU iPhone OS 14_0)  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         groupBy(client_ip, function=session(maxpause=15m))

Groups events by the field client_ip into sessions of 15 minutes. then makes a count of the total number of unique sessions 

The [_`maxpause`_](https://library.humio.com/data-analysis/functions-session.html#query-functions-session-maxpause) parameter defines the maximum pause between the sessions (`15m` in this example). Events more far apart than the defined value will become separate sessions. For example, if the same user returns to a site within 15 minutes, it will be the same session. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | count()

Makes a count of the total number of unique sessions. 

  4. Event Result set.




### Summary and Results

The query is used to group events by client IP addresses into sessions of 15m, and then make a count of the total number of unique sessions (returns the total count of sessions across all IP addresses). The query is, for example, useful for measuring unique website/application visitors and understanding real user engagement patterns. Also useful for security monitoring and detection of unusual spikes in unique visitors. 

Sample output from the incoming example data: 

_count  
---  
4  
  
The query counts 4 unique sessions total as the first IP address has activity that spans beyond the 15-minute session timeout, creating two distinct sessions. 

If you make the count on the client_ip field: `| count(client_ip)`, the query will return a more detailed result showing the session count per IP address: 

client_ip| _count  
---|---  
192.168.1.100| 2  
192.168.1.101| 1  
192.168.1.102| 1
