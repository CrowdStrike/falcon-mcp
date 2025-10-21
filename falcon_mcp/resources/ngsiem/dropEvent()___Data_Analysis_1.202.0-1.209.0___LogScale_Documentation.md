# dropEvent() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-dropevent.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`dropEvent()`](functions-dropevent.html "dropEvent\(\)")

The [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function can be used both during queries and within the parser pipeline. 

Depending on usage, the function has different behavior: 

  * If used during parsing, the event is dropped and removed entirely from the query output, meaning that the event data will not be stored in Falcon LogScale. 

  * If used within normal searching, the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function is simply an alias for false - it behaves the same as `false`. 




### Note

The [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") does not accept any arguments. The [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") has different behaviour depending on usage in parser or in normal searches. 

### [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") Examples

Click + next to an example below to get the full details.

#### Drop Event During Parsing

**Drop event during parsing using the[`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function **

##### Query

logscale
    
    
    parseJson()
    | case { someField = "some_value"
    | dropEvent(); * }
    | parseTimestamp(field=@timestamp)

##### Introduction

The [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function is often used within parsers to drop events during parsing that do not need to be ingested. The following example shows how to filter events as part of a parser by matching a particular field value from being ingested. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         parseJson()

Parses the incoming data to identify JSON values and converts them into a usable field. 

  3. logscale
         
         | case { someField = "some_value"
         | dropEvent(); * }

Starts a `case` statement, with the first matching expression identifying a field value in the extracted JSON field from the returned results. Then drops the event. This has the effect of terminating the parsing for this event, as there is no more data to be processed. 

  4. logscale
         
         | parseTimestamp(field=@timestamp)

Parses the timestamp from the @timestamp field for all other events that do not match the JSON value. 

  5. Event Result set.




##### Summary and Results

This query is used to drop events at ingestion. When used within the parser pipeline, the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") is a simple and practical way of eliminating events during the parsing of incoming data. 

#### Drop Events Based on Parsing JSON Value

****

##### Query

logscale
    
    
    case {
    @rawstring="#*"
    | dropEvent();
    * }

##### Introduction

When parsing incoming data, it is sometimes the case that the data includes 'commented' data, where,for example, the `#` character is used to identify comments in files rather than real data. This example removes those lines from the ingest process during parsing using the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function to drop the entire event from the ingest pipeline. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         case {
         @rawstring="#*"
         | dropEvent();

Starts a `case` statement, with the first matching expression looking for the hash symbol in a line to indicate that it could be removed, then dropping the entire event using [`dropEvent()`](functions-dropevent.html "dropEvent\(\)")

  3. logscale
         
         * }

For all other lines, the `case` expression matches all other events and lets them through. 

  4. Event Result set.




##### Summary and Results

This query is used to remove data at ingestion, in this example data that matches a typical source construct (the comment). When used within the parser pipeline, the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function ensures that the data is removed entirely from the query output, meaning that the event data will not be stored in LogScale. 

#### Drop Events Based on Specific Field Values or Patterns

**Drop events based on specific field values or patterns during normal searching using the[`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function with case statement **

##### Query

logscale
    
    
    case {
    fielda = badresult | dropEvent();
    fieldb = badresult | dropEvent();
    wildcard("badip", field[fieldc, fieldd] | dropEvent())
    }

##### Introduction

In this example, the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function is used within normal searching with a case statement to drop events based on specific values and patterns. When used within normal searching, the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function is simply an alias for `false` \- it behaves the same as false. It filters out specific events from the results. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         case {
         fielda = badresult | dropEvent();
         fieldb = badresult | dropEvent();
         wildcard("badip", field[fieldc, fieldd] | dropEvent())
         }

Starts a `case` statement containing the following three conditions: 

If fielda equals `badresult`, drop the event. 

If fieldb equals `badresult`, drop the event. 

If either fieldc or fieldd contains the string `badip` (using wildcard matching), drop the event. 

Each condition uses the [`dropEvent()`](functions-dropevent.html "dropEvent\(\)") function as the action to take when the condition is met. The [`wildcard()`](functions-wildcard.html "wildcard\(\)") function is used in the third condition to perform pattern matching with wildcards against multiple fields specified in the array notation `field[fieldc, fieldd]`. 

  3. Event Result set.




##### Summary and Results

This query is used to drop events based on specific field values or patterns. In all three cases, the events that contain the filtered information will be removed from the results. This is useful, for example, for event processing or log filtering.
