# Search Two Fields for Multiple Values in Either First Field or Second Field | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-in-multifields-or.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Search Two Fields for Multiple Values in Either First Field or Second Field

Search two fields for multiple values using the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function, using a case statement as an OR 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    case
            { in(srcIP, values=["10.1.168.2", "127.0.0.1"]);
            in(targetIP, values=["10.0.0.1", "192.168.1.12"]); }

### Introduction

The [`in()`](https://library.humio.com/data-analysis/functions-in.html) function can be used to select events in which the given field contains specific values. Sometimes it may be necessary to search for multiple values in two different fields in the same query string. Though the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function cannot directly be combined with an OR clause, it is possible to use the [`in()`](https://library.humio.com/data-analysis/functions-in.html) function in a case statement to produce the same output as an OR. 

In this example, the query will look for events in either the srcIP field or the targetIP. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         case
                 { in(srcIP, values=["10.1.168.2", "127.0.0.1"]);
                 in(targetIP, values=["10.0.0.1", "192.168.1.12"]); }

Filters for events in the srcIP field that contains the values `10.1.168.2` or `127.0.0.1` and filters for events in the targetIP field that contains the values `10.0.0.1` or `192.168.1.12`. The returned results would be events from both fields. Notice that because it is a case statement, it executes and returns whether either field contains the corresponding values in the array. 

  3. Event Result set.




### Summary and Results

The query is used to query two fields for multiple/specific values in either first field or second field.
