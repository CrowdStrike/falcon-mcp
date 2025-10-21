# Compare More Fields and Their Respective Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-test-compare-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compare More Fields and Their Respective Values

Compare more fields and their respective values 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00;

logscale
    
    
    test(field1 < field2)

### Introduction

The [`test()`](https://library.humio.com/data-analysis/functions-test.html) function can be used to make comparisons between one field and one value, and it can also compare more fields and their respective values. 

In this example, the [`test()`](https://library.humio.com/data-analysis/functions-test.html) function is used to check if the value of field1 is less than the value in field2. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         test(field1 < field2)

Evaluates if the value of the field field1 is less than the value in field field2. 

  3. Event Result set.




### Summary and Results

The query is used to compare more fields and their respective values.
