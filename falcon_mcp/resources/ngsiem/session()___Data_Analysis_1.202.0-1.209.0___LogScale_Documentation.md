# session() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-session.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`session()`](functions-session.html "session\(\)")

Collects events into sessions, which are series of events that are no further than [_`maxpause`_](functions-session.html#query-functions-session-maxpause) apart (defaults to 15m), and then performs an aggregate operation across the events that make up the session. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`function`_](functions-session.html#query-functions-session-function)[a]| array of aggregate functions| optional[b] | `count(as=_count)`|  Specifies which aggregate functions to perform on each session. If several aggregators are listed for the [_`function`_](functions-session.html#query-functions-session-function) parameter, then their outputs are combined using the rules described for [`stats()`](functions-stats.html "stats\(\)").   
[_`maxpause`_](functions-session.html#query-functions-session-maxpause)|  string| optional[[b]](functions-session.html#ftn.table-functions-session-optparamfn) | `15m`|  Defines the maximum pause between sessions, for example, events more than this far apart will become separate sessions.   
[a] The parameter name [_`function`_](functions-session.html#query-functions-session-function) can be omitted.[b] Optional parameters use their default value unless explicitly set.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`function`_](functions-session.html#query-functions-session-function) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     session("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     session(function="value")
> 
> These examples show basic structure only.

### [`session()`](functions-session.html "session\(\)") Examples

Click + next to an example below to get the full details.

#### Analyze User Sessions Based on Click Activity

**Analyzes user sessions based on users click activity using the[`session()`](functions-session.html "session\(\)") function **

##### Query

logscale
    
    
    groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))
    | sort(clicks)

##### Introduction

In this example, the [`session()`](functions-session.html "session\(\)") function is used to analyze user sessions based on users click activity. The [`session()`](functions-session.html "session\(\)") function groups events by a given timespan. 

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
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(cookie_id, function=session(maxpause=15m, count(as=clicks)))

Groups events by the field cookie_id (unique user identifier) and creates sessions with 15-minute inactivity timeout (the default value of the [_`maxpause`_](functions-session.html#query-functions-session-maxpause) parameter), then makes a count of each event in a session returning the result in a new field named clicks. 

  3. logscale
         
         | sort(clicks)

Sorts the results by number of clicks (default is descending order). 

  4. Event Result set.




##### Summary and Results

The query is used to analyze user sessions based on the users click activity. The query is useful, for example, to identify most/least active user sessions, detect potential automated behavior or just to understand user engagement levels. 

Sample output from the incoming example data: 

cookie_id| clicks  
---|---  
user123| 5  
user456| 3  
user789| 2  
  
Note that each row represents an event (either pageview or click). 

#### Count Unique Visitors Based on Client IP Addresses

**Count unique visitors based on client IP addresses using the[`session()`](functions-session.html "session\(\)") function **

##### Query

logscale
    
    
    groupBy(client_ip, function=session(maxpause=15m))
    | count()

##### Introduction

In this example, the [`session()`](functions-session.html "session\(\)") function is used to count the unique visitors (each visitor defined as non-active for 15 minutes) of a site based on client IP addresses. The [`session()`](functions-session.html "session\(\)") function groups events by a given timespan. 

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
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(client_ip, function=session(maxpause=15m))

Groups events by the field client_ip into sessions of 15 minutes. then makes a count of the total number of unique sessions 

The [_`maxpause`_](functions-session.html#query-functions-session-maxpause) parameter defines the maximum pause between the sessions (`15m` in this example). Events more far apart than the defined value will become separate sessions. For example, if the same user returns to a site within 15 minutes, it will be the same session. 

  3. logscale
         
         | count()

Makes a count of the total number of unique sessions. 

  4. Event Result set.




##### Summary and Results

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
  
#### Find Minimum And Maximum Values of any Numerical Field in Session

**Find minimum and maximum values of any numerical field in a session using the[`session()`](functions-session.html "session\(\)") function **

##### Query

logscale
    
    
    groupBy(cookie_id, function=session([max(bet),min(bet)]))

##### Introduction

In this example, the [`session()`](functions-session.html "session\(\)") function is used to find minimum and maximum values of the field bet in a session. The [`session()`](functions-session.html "session\(\)") function groups events by a given timespan. 

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
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         groupBy(cookie_id, function=session([max(bet),min(bet)]))

Groups events by the field cookie_id (unique user identifier) and creates sessions of 15-minutes timeout (the default value of the [_`maxpause`_](functions-session.html#query-functions-session-maxpause) parameter), then calculates the maximum and minimum values of the field bet for each session, returning the results in new fields named _max and _min. 

  3. Event Result set.




##### Summary and Results

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
