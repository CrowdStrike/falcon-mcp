# Modify Existing Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-eval-kib.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Modify Existing Fields

Modify existing fields by evaluating the provided expression using the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    eval(responsesize = responsesize / 1024)

### Introduction

The [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function can be used to modify existing fields. 

In this example, the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function is used to show the responseSize field in Kibibyte (KiB) instead of bytes. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         eval(responsesize = responsesize / 1024)

Modifies the existing responsesize field by, first, dividing the current value of responsesize by `1024`, then assigning the returned results back to the responsesize field. 

Notice that the original value is overwritten. Any subsequent use of the field responsesize in the query will be working with the new value in kilobytes, not the original value in bytes. 

If you want to preserve the original value, consider creating a new field instead: `eval(responsesizeKB = responsesize / 1024)`. This creates a new field responsesizeKB while leaving the values in the original field responsesize unchanged. 

  3. Event Result set.




### Summary and Results

The query is used to modify an existing field. In this example, it is used to convert values from one size to another; `bytes` to `KiB`. Converting values to `KiB` is useful when working with binary systems. The transformation is, for example, useful when dealing with network traffic, file sizes, or any other data where you want to represent sizes in a more readable format (KB instead of bytes). 

It is also possible to use the [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html) for converting units. For more information about supported units, see [`unit:convert()`](https://library.humio.com/data-analysis/functions-unit-convert.html).
