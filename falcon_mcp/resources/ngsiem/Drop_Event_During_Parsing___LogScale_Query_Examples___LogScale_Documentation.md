# Drop Event During Parsing | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-dropevent-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Drop Event During Parsing

Drop event during parsing using the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    parseJson()
    | case { someField = "some_value"
    | dropEvent(); * }
    | parseTimestamp(field=@timestamp)

### Introduction

The [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function can be used both during queries and within the parser pipeline. Depending on usage, the function has different behavior. 

If used during parsing, the event is dropped and removed entirely from the query output, meaning that the event data will not be stored in LogScale. If used within normal searching, the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function is simply an alias for false - it behaves the same as `false`. 

The [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function is often used within parsers to drop events during parsing that do not need to be ingested. The following example shows how to filter events as part of a parser by matching a particular field value from being ingested. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         parseJson()

Parses the incoming data to identify JSON values and converts them into a usable field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | case { someField = "some_value"
         | dropEvent(); * }

Starts a `case` statement, with the first matching expression identifying a field value in the extracted JSON field from the returned results. Then drops the event. This has the effect of terminating the parsing for this event, as there is no more data to be processed. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3[/Filter/] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseTimestamp(field=@timestamp)

Parses the timestamp from the @timestamp field for all other events that do not match the JSON value. 

  5. Event Result set.




### Summary and Results

This query is used to drop events at ingestion. When used within the parser pipeline, the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) is a simple and practical way of eliminating events during the parsing of incoming data.
