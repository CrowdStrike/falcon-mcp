# Create New Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-eval-addfieldtogether.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Create New Fields

Create new fields by evaluating the provided expression using the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    eval(c = a + b)

### Introduction

The [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function can be used to create new fields based on an expression. 

In this example, the [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function is used to add the fields a and b together, creating a new field c containing the results. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         eval(c = a + b)

Adds the values of field a and field b together and returns the sum of these in a new field named c. 

  3. Event Result set.




### Summary and Results

The query is used to create a new field containing the sum of two other fields. In case the field c already existed, it would just be modified with the new value. The [`eval()`](https://library.humio.com/data-analysis/functions-eval.html) function is useful when testing and debugging. You can for example use it to test a complex function or expression with different inputs and quickly check the output in the returned values.
