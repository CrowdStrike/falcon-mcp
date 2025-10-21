# Make Copy of Events | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-copyevent-extracopy-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Make Copy of Events

Make an extra copy of the event to be parsed along with the original event using the [`copyEvent()`](https://library.humio.com/data-analysis/functions-copyevent.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{{Aggregate}} 4[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result

logscale
    
    
    copyEvent("arrivaltime")
    | case { #type=arrivaltime
    | @timestamp:=now() ; *
    | parseTimestamp(field=ts) }

### Introduction

The [`copyEvent()`](https://library.humio.com/data-analysis/functions-copyevent.html) function is used to make an extra copy of an event, when parsed, both copies will be visible in the pipeline. A common use of case statements is to return a specific value depending on a column's value in the result set. 

In this example, an event is stored with both the timestamp from the event and a separate stream based on arrival time (assuming the event has a type that is not `arrivaltime`). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{{Aggregate}} 4[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         copyEvent("arrivaltime")

Creates a copy of the current event, and assigns the type arrivaltime to the copied event. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{{Aggregate}} 4[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | case { #type=arrivaltime

Returns a specific value that meets the defined condition. In this case, it checks if the event type is arrivaltime, then categorizes all events by their arrivaltimes. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{{Aggregate}} 4[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | @timestamp:=now() ; *

Sets the @timestamp field to the current time `now()` for all events of the type arrivaltime, and adds the `;` separator and `*` to ensure, that all other fields are kept unchanged. As the [`now()`](https://library.humio.com/data-analysis/functions-now.html) is placed after the first aggregate function, it is evaluated continuously, and returns the live value of the current system time, which can divert between LogScale nodes. 

  5. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[/Filter/] 3{{Aggregate}} 4[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> 4 4 --> result style 4 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseTimestamp(field=ts) }

As the original events keep the original timestamp, it parses the timestamp from a field named ts for events that are not of type arrivaltime. 

  6. Event Result set.




### Summary and Results

The query is used to make an extra copy of an event, when parsed, both copies will be visible in the pipeline. The query creates a copy with type arrivaltime, and sets its timestamp to the current time, while the original event retains its original timestamp. This allows tracking both when an event occurred (original timestamp) and when it was received/processed (arrival time). The query is useful in log processing and data management.
