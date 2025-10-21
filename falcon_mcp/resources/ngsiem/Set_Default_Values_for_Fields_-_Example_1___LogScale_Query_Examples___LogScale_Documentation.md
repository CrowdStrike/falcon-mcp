# Set Default Values for Fields - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-default-setvalue-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set Default Values for Fields - Example 1

Set default values for field using the [`default()`](https://library.humio.com/data-analysis/functions-default.html) function so it can be used in a calculation with [`eval()`](https://library.humio.com/data-analysis/functions-eval.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    default(field=[minutes, seconds, hours], 0)

### Introduction

Setting default values of fields is necessary, if the fields are to be used in calculations with the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function. If not set to a value so the field is considered to be present, the event would be discarded during eval step. In this example, an array is set as the _`field`_ parameter. This allows setting the same default value for multiple fields with a single command. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         default(field=[minutes, seconds, hours], 0)

Sets the default value of the fields minutes, seconds and hours to `0` so it can be used in a calculation. It ensures, that all time-related fields have a numeric value. 

If the fields did not have a value, the event would be discarded during the eval step because [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) requires all used fields to be present. 

  3. Event Result set.




### Summary and Results

The query is used to enable calculation of the fields with the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function. The query ensures that all events have consistent minutes, seconds, and hours fields for further processing or analysis. Otherwise, if the field is not set to a value, the event is not parsed. The use of the [`default()`](https://library.humio.com/data-analysis/functions-default.html) function is important for data normalization and preparation in log analysis, ensuring consistent and complete data sets for further processing and analysis. For example, in a security event log, ensuring that all events have a message can be crucial for quick triage.
