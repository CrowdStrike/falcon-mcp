# Evaluate Field Values Within Repository | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-test-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Evaluate Field Values Within Repository

Compare field values within the Falcon LogScale repository 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00;

logscale
    
    
    test(cputime < 7500)

### Introduction

The [`test()`](https://library.humio.com/data-analysis/functions-test.html) function is used to evaluate arbitrary expressions as boolean values in a query. Arbitrary expressions are used for various purposes, like performing calculations, making decisions, and defining conditions. 

In this example, the [`test()`](https://library.humio.com/data-analysis/functions-test.html) function evaluates the arbitrary expression `<` as a boolean value (true/false) and filters events when the expression returns true. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[(Filter Function)] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ffbf00; style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         test(cputime < 7500)

Evaluates if the value of the field cputime is less than `7500`. 

  3. Event Result set.




### Summary and Results

The query is used to compare a field value within the Falcon LogScale repository.
