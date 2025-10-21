# Format JSON | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-jsonprettyprint-filter-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format JSON

Format JSON in @rawstring field using the [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #type=json
    | account=123
    | json:prettyPrint()

### Introduction

The [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function can be used to format a JSON field for improved readability. When used without parameters, [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) assumes, that the JSON is in the @rawstring field. 

In this example, the [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function is used to format the @rawstring field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=json

Filters for events with the `JSON` type. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | account=123

Filters for events related to account 123. 

It is recommended to filter the event set as much as possible before using the [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function to prevent unnecessary formatting of discarded data. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | json:prettyPrint()

Formats the `JSON` content for improved readability. Without a specified field, it formats the @rawstring field. 

Note that if input is not valid JSON, it returns unmodified values. To prevent this, you can set a [_`strict`_](https://library.humio.com/data-analysis/functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter. For an example of usage, see [Format Only Valid JSON](examples-jsonprettyprint-strict.html "Format Only Valid JSON"). 

  5. Event Result set.




### Summary and Results

The query is used to make JSON data more readable in the results. Formatting JSON in the @rawstring field after filtering the data is very important as it is a resource-intensive operation. 

Note that without the [_`strict`_](https://library.humio.com/data-analysis/functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true`, the [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function attempts to format even invalid JSON, which might lead to unexpected results.
