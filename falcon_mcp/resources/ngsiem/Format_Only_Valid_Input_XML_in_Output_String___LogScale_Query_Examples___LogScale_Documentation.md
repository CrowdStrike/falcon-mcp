# Format Only Valid Input XML in Output String | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-xmlprettyprint-message-field.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format Only Valid Input XML in Output String

Format only valid input XML to valid XML in output string using the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    formattedXml := xml:prettyPrint(field=message, strict=true)

### Introduction

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function can be used to format the XML in the output string (the filtered data) for improved readability. 

It is recommended to apply [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) after filtering your data at the end of the query. This prevents unnecessary formatting of data that will be discarded. 

In this example, the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function is used to format only the valid XML in the field [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) in the output string. 

Setting the [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter to `true`, means that only valid XML input produce a value in the output field. By default - if the [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) parameter is not set - invalid input XML is copied to the output field unmodified. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         formattedXml := xml:prettyPrint(field=message, strict=true)

Formats and copies valid XML to the output field formattedXml by setting the parameter `strict=true`. 

When [_`strict`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-strict) is set to `true`, only valid XML input produce a value in the output field, therefore, the field formattedXml will not be created for events with invalid XML in message. 

  3. Event Result set.




### Summary and Results

The query is used to "pretty print" an XML field, in this example the [message](https://library.humio.com/logscale-repo-schema/logscale-repo-schema-humio-activity-terms-action.html) field, and to validate the integrity of the XML message as it only outputs if the XML is completely valid. Only the valid input XML is formatted to valid output XML. Invalid input XML is not copied to the output field unmodified. 

The query is useful in cases where XML validity is critical and to ensure XML compliance. 

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function formats an XML field for improved readability.
