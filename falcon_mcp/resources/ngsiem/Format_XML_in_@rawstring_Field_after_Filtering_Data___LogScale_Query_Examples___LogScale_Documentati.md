# Format XML in @rawstring Field after Filtering Data | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-xmlprettyprint-soap.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format XML in @rawstring Field after Filtering Data

Format XML in @rawstring field after filtering the data using the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result

logscale
    
    
    #type=SOAP
    | account=123
    | xml:prettyPrint()

### Introduction

The data type `SOAP` (Simple Object Access Protocol) stores a text string along with an identifier of the character set used in the string. If the character set used in the string is `UTF-8`, the string may be passed to Transformation Server unmodified. 

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function can be used to format the XML in the output string (the filtered data) for improved readability. 

It is recommended to apply [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) after filtering your data at the end of the query. This prevents unnecessary formatting of data that will be discarded. 

In this example, the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function is used to format the filtered `SOAP` messages in the output string. 

Note that if no field is specified, the [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field will be formatted. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         #type=SOAP

Filters for all events of the data type `SOAP`. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | account=123

Filters for strings where the field account matches the value `123`. It narrows the scope to a specific account's `SOAP` messages. 

  4. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2[/Filter/] 3>Augment Data] result{{Result Set}} repo --> 1 1 --> 2 2 --> 3 3 --> result style 3 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | xml:prettyPrint()

Takes the filtered SOAP messages (which are in XML format), and formats the XML content in the [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field for better readability. 

In this example, all the default values for the parameters [_`field`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-field), [_`step`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-step), [_`width`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-width) and [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) are used. 

  5. Event Result set.




### Summary and Results

The query is used to format rawstrings into valid XML, in this case retrieved `SOAP` messages from `account 123`. This is useful, for example, when analyzing specific `SOAP` messages in detail. 

Note that the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function can be used on any XML content - not just limited to SOAP messages, but also REST XML responses, XML configuration files, XML logs and any other XML formatted data. 

"Pretty printing" XML can be an expensive operation and it is recommended only to perform this after filtering the data (at the end of the query), so that only filtered data is formatted.
