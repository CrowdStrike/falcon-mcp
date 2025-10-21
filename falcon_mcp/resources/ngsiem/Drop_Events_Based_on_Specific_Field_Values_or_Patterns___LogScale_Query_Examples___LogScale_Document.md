# Drop Events Based on Specific Field Values or Patterns | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-dropevent-filter-normal-searching.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Drop Events Based on Specific Field Values or Patterns

Drop events based on specific field values or patterns during normal searching using the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function with case statement 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Drop Event"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    case {
    fielda = badresult | dropEvent();
    fieldb = badresult | dropEvent();
    wildcard("badip", field[fieldc, fieldd] | dropEvent())
    }

### Introduction

The [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function can be used both during queries and within the parser pipeline. Depending on usage, the function has different behavior. 

If used during parsing, the event is dropped and removed entirely from the query output, meaning that the event data will not be stored in LogScale. If used within normal searching, the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function is simply an alias for false - it behaves the same as `false`. 

In this example, the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function is used within normal searching with a case statement to drop events based on specific values and patterns. When used within normal searching, the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function is simply an alias for `false` \- it behaves the same as false. It filters out specific events from the results. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Drop Event"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         case {
         fielda = badresult | dropEvent();
         fieldb = badresult | dropEvent();
         wildcard("badip", field[fieldc, fieldd] | dropEvent())
         }

Starts a `case` statement containing the following three conditions: 

If fielda equals `badresult`, drop the event. 

If fieldb equals `badresult`, drop the event. 

If either fieldc or fieldd contains the string `badip` (using wildcard matching), drop the event. 

Each condition uses the [`dropEvent()`](https://library.humio.com/data-analysis/functions-dropevent.html) function as the action to take when the condition is met. The [`wildcard()`](https://library.humio.com/data-analysis/functions-wildcard.html) function is used in the third condition to perform pattern matching with wildcards against multiple fields specified in the array notation `field[fieldc, fieldd]`. 

  3. Event Result set.




### Summary and Results

This query is used to drop events based on specific field values or patterns. In all three cases, the events that contain the filtered information will be removed from the results. This is useful, for example, for event processing or log filtering.
