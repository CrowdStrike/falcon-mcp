# Calculate Rounded Square Root Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathsqrt-calculate-assigned-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Rounded Square Root Values

Find and round square roots using the [`math:sqrt()`](https://library.humio.com/data-analysis/functions-math-sqrt.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    myvalue := 100
    | math:sqrt(myvalue, as=square_root)

### Introduction

The [`math:sqrt()`](https://library.humio.com/data-analysis/functions-math-sqrt.html) function can be used to calculate the square root of positive numeric values. The function returns the positive square root rounded to the nearest integer. 

In this example, the [`math:sqrt()`](https://library.humio.com/data-analysis/functions-math-sqrt.html) function is used to calculate the square root of an assigned value. The input must be a numeric field that can contain decimal values (floating-point numbers). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         myvalue := 100

Assigns the value `100` to a field named myvalue. This creates a new field with a constant value that will be used for the square root calculation. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:sqrt(myvalue, as=square_root)

Takes the square root of the value in the myvalue field and returns the result in a new field named square_root. The function automatically rounds the result to the nearest integer. In this case, it calculates the square root of `100`, which is `10`. 

Note that - if not returning an exact integer, the function rounds the result to the nearest integer in case of non-perfect squares. For example: 

Square root of `90 = 9.487` rounds to `9`. 

Square root of `91 = 9.539` rounds to `10`. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the square root of an assigned constant value, demonstrating how to combine value assignment with mathematical functions. 

This query is useful, for example, to perform calculations on fixed values or to add reference calculations to existing event data. 

Sample output from the incoming example data: 

square_root  
---  
10
