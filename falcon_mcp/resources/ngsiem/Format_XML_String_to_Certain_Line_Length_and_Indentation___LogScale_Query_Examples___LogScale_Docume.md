# Format XML String to Certain Line Length and Indentation | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-xmlprettyprint-payload-field.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format XML String to Certain Line Length and Indentation

Format XML strings to a certain line length and indentation using the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    formattedXml := xml:prettyPrint(field=payload, step=4, width=100)

### Introduction

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function can be used to format the XML in the output string (the filtered data) for improved readability. 

It is recommended to apply [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) after filtering your data at the end of the query. This prevents unnecessary formatting of data that will be discarded. 

In this example, the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function is used with specified _`step`_ and _`width`_ parameters to format the XML content in the payload field (instead of default [@rawstring](https://library.humio.com/data-analysis/searching-data-event-fields.html#searching-data-event-fields-metadata-rawstring) field). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         formattedXml := xml:prettyPrint(field=payload, step=4, width=100)

Formats XML in the field payload to a max line length of `100` and indent by `4` spaces, and returns the formatted XML result in a new field named formattedXml. 

Defining a max line length of 100 characters using the [_`width`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-width) parameter makes it easier to read (allows longer lines before wrapping). 

Larger indentation (4 spaces) provides more visual separation between XML levels. 

  3. Event Result set.




### Summary and Results

The query is used to format values of a specific field into valid XML of a certain line length and indentation. Defining a max line length makes it easier to read. 

"Pretty printing" XML can be an expensive operation and it is recommended only to perform this after filtering the data (at the end of the query), so that only filtered data is formatted. 

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function formats an XML field for improved readability.
