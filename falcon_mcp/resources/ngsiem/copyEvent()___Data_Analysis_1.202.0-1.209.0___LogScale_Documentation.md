# copyEvent() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-copyevent.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`copyEvent()`](functions-copyevent.html "copyEvent\(\)")

Makes an extra copy of the event within the current pipeline. This can only be used within the parser to duplicate events for the purposes of copying the even to another repo. The function cannot be used during a query. 

For On-Prem deployments only: If you are using this function to copy an event to another repository, the [`ALLOW_CHANGE_REPO_ON_EVENTS`](https://library.humio.com/falcon-logscale-self-hosted/envar-allow_change_repo_on_events.html) environment variable must be set to `true`. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`type`_](functions-copyevent.html#query-functions-copyevent-type)[a]| string| required |  |  The value for [#type](searching-data-event-fields.html#searching-data-event-fields-tag-type) for the copy.   
[a] The parameter name [_`type`_](functions-copyevent.html#query-functions-copyevent-type) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`type`_](functions-copyevent.html#query-functions-copyevent-type) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     copyEvent("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     copyEvent(type="value")
> 
> These examples show basic structure only.

### [`copyEvent()`](functions-copyevent.html "copyEvent\(\)") Examples

Click + next to an example below to get the full details.

#### Make Copy of Events

**Make an extra copy of the event to be parsed along with the original event using the[`copyEvent()`](functions-copyevent.html "copyEvent\(\)") function **

##### Query

logscale
    
    
    copyEvent("arrivaltime")
    | case { #type=arrivaltime
    | @timestamp:=now() ; *
    | parseTimestamp(field=ts) }

##### Introduction

In this example, an event is stored with both the timestamp from the event and a separate stream based on arrival time (assuming the event has a type that is not `arrivaltime`). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         copyEvent("arrivaltime")

Creates a copy of the current event, and assigns the type arrivaltime to the copied event. 

  3. logscale
         
         | case { #type=arrivaltime

Returns a specific value that meets the defined condition. In this case, it checks if the event type is arrivaltime, then categorizes all events by their arrivaltimes. 

  4. logscale
         
         | @timestamp:=now() ; *

Sets the @timestamp field to the current time `now()` for all events of the type arrivaltime, and adds the `;` separator and `*` to ensure, that all other fields are kept unchanged. As the [`now()`](functions-now.html "now\(\)") is placed after the first aggregate function, it is evaluated continuously, and returns the live value of the current system time, which can divert between LogScale nodes. 

  5. logscale
         
         | parseTimestamp(field=ts) }

As the original events keep the original timestamp, it parses the timestamp from a field named ts for events that are not of type arrivaltime. 

  6. Event Result set.




##### Summary and Results

The query is used to make an extra copy of an event, when parsed, both copies will be visible in the pipeline. The query creates a copy with type arrivaltime, and sets its timestamp to the current time, while the original event retains its original timestamp. This allows tracking both when an event occurred (original timestamp) and when it was received/processed (arrival time). The query is useful in log processing and data management. 

#### Make Copy of Events from One Repo to Another Repo

**Use one parser to ingest data into multiple repositories**

##### Query

logscale
    
    
    copyEvent("cloned_event")
    | case { #type="cloned_event"
    | repo := "target-repo-name"; * }

##### Introduction

In this example, an event is copied from one repo to another and the copied event can only be used in a parser. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         copyEvent("cloned_event")

Creates a copy of the current event, and assigns the type cloned_event to the copied event. Now two events are flowing through the parser, one event containing the field cloned_event, and one event without that field. In other words, it creates a copy with the type cloned_event and assigns it to a different repository. 

  3. logscale
         
         | case { #type="cloned_event"

Returns a specific value that meets the defined condition. In this case, it checks if the event type is cloned_event. The case construct is used to direct the two events to a different target repo. 

  4. logscale
         
         | repo := "target-repo-name"; * }

Creates a new repo named target-repo-name with all events of the type cloned_event being directed. The use of `*` ensures, that all other fields are kept unchanged. 

  5. Event Result set.




##### Summary and Results

The query is used to ingest data into multiple repositories using the same parser. Shipping all data to one parser and having that parser ship data to many different repositories can be useful: for example, if logs are being sent from a single source, it is possible to setup one parser that can parse all events from this source and decide which repositories to send events to. 

### Note

For On-Prem deployments only: If you are using this function to copy an event to another repository, the [`ALLOW_CHANGE_REPO_ON_EVENTS`](https://library.humio.com/falcon-logscale-self-hosted/envar-allow_change_repo_on_events.html) environment variable must be set to `true`.
