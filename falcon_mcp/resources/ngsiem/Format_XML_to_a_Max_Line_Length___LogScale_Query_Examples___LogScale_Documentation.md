# Format XML to a Max Line Length | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-xmlprettyprint-max-line-length.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format XML to a Max Line Length

Format XML in @rawstring field using the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function with custom formatting parameters set 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    formattedXml := xml:prettyPrint(field=payload, step=4, width=100)

### Introduction

The [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function can be used to format an XML field for improved readability. When used without parameters, [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) assumes, that the XML is in the @rawstring field. 

In this example, the [`xml:prettyPrint()`](https://library.humio.com/data-analysis/functions-xml-prettyprint.html) function is used with parameters to format the XML data in the payload field to a max line length of 100 and indent by 4 spaces. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         formattedXml := xml:prettyPrint(field=payload, step=4, width=100)

Uses the [_`field`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-field) parameter to specify the payload field as the source of XML data, the [_`step`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-step) parameter set to `4`, and the [_`width`_](https://library.humio.com/data-analysis/functions-xml-prettyprint.html#query-functions-xml-prettyprint-width) parameter set to `100` to format the XML data in the payload field to a max line length of 100 and indent by 4 spaces. 

The results are assigned to a new field named formattedXml. 

  3. Event Result set.




### Summary and Results

The query is used to make XML data more readable in the results by defining a max line length of 100 and indent by 4 spaces.
