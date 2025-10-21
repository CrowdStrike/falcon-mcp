# Format Only Valid JSON | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-jsonprettyprint-strict.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Format Only Valid JSON

Format only JSON data that is considered valid using the [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    formattedJson := json:prettyPrint(field=message, strict=true)

### Introduction

The [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function can be used to format a JSON field for improved readability. When used without parameters, [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) assumes, that the JSON is in the @rawstring field. 

In this example, the [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function is used to format the message field as JSON with the [_`strict`_](https://library.humio.com/data-analysis/functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true` to only process valid JSON. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         formattedJson := json:prettyPrint(field=message, strict=true)

Uses the [_`field`_](https://library.humio.com/data-analysis/functions-json-prettyprint.html#query-functions-json-prettyprint-field) parameter to specify the message field as the source of JSON data and the [_`strict`_](https://library.humio.com/data-analysis/functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true` to only process valid JSON. 

Formats the valid JSON data for improved readability and assigns the results to a new field named formattedJson. 

Note that if the JSON in the message field is invalid, the formattedJson field will not be created for that event. This is because the [_`strict`_](https://library.humio.com/data-analysis/functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter is set to `true`. 

  3. Event Result set.




### Summary and Results

The query is used to make valid JSON data more readable in the results. 

Without [_`strict`_](https://library.humio.com/data-analysis/functions-json-prettyprint.html#query-functions-json-prettyprint-strict) parameter set to `true`, the [`json:prettyPrint()`](https://library.humio.com/data-analysis/functions-json-prettyprint.html) function attempts to format even invalid JSON, which might lead to unexpected results.
