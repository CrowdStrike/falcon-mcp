# Format XML | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-xmlprettyprint-filter-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format XML

Format XML in @rawstring field using the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #type=SOAP
            | account=123
            | xml:prettyPrint()

### Introduction

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function can be used to format an XML field for improved readability. When used without parameters, [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) assumes, that the XML is in the @rawstring field. 

In this example, the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function is used to format the @rawstring field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=SOAP

Filters for events with the `XML` type. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | account=123

Filters for events related to account 123. 

It is recommended to filter the event set as much as possible before using the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function to prevent unnecessary formatting of discarded data. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | xml:prettyPrint()

Formats the `XML` content for improved readability. Without a specified field, it formats the @rawstring field. 

Note that if input is not valid XML, it returns unmodified values. To prevent this, you can set a [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter. For an example of usage, see [Format Only Valid XML](examples-xmlprettyprint-strict.html "Format Only Valid XML"). 

  5. Event Result set.




### Summary and Results

The query is used to make XML data more readable in the results. Formatting XML in the @rawstring field after filtering the data is very important as it is a resource-intensive operation.
