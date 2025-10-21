# Format Only Valid XML | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-xmlprettyprint-strict.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format Only Valid XML

Format only XML data that is considered valid using the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    formattedXml := xml:prettyPrint(field=message, strict=true)

### Introduction

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function can be used to format an XML field for improved readability. When used without parameters, [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) assumes, that the XML is in the @rawstring field. 

In this example, the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function is used to format the message field as XML with the [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter set to `true` to only process valid XML. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         formattedXml := xml:prettyPrint(field=message, strict=true)

Uses the [_`field`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-field) parameter to specify the message field as the source of XML data and the [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter set to `true` to only process valid XML. 

Formats the valid XML data for improved readability and assigns the results to a new field named formattedXml. 

Note that if the XML in the message field is invalid, the formattedXml field will not be created for that event. 

  3. Event Result set.




### Summary and Results

The query is used to make valid XML data more readable in the results. 

Note that without [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter set to `true`, the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function attempts to format even invalid XML, which might lead to unexpected results.
