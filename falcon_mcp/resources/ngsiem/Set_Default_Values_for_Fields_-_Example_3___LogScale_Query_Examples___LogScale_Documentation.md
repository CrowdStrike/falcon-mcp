# Set Default Values for Fields - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-default-replaceempty.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set Default Values for Fields - Example 3

Set default values for a field and replace empty values with relevant default value 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    default(field=message, value="N/A", replaceEmpty=true)

### Introduction

Setting default values of fields is necessary, if the fields are to be used in calculations with the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function. If not set to a value so the field is considered to be present, the event would be discarded during eval step. 

In LogScale, empty values are by default kept as the field does indeed exist when it has the empty value. 

This examples shows how to set _`replaceEmpty`_ to `true` to replace empty values with the default as well. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         default(field=message, value="N/A", replaceEmpty=true)

Replaces an empty value in the field message with the default value `"N/A"` by setting _`replaceEmpty`_ to `true`. 

  3. Event Result set.




### Summary and Results

The query is used to replace empty values in a field to a defined default value. If not setting a default value for empty values, the event would be discharded during further eval steps because [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) requires all used fields to be present. The use of the [`default()`](https://library.humio.com/data-analysis/functions-default.html) function is important for data normalization and preparation in log analysis, ensuring consistent and complete data sets for further processing and analysis. For example, in a security event log, ensuring that all events have a message can be crucial for quick triage.
