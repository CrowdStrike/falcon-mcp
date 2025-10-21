# Calculate Tangent Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathtan-calculate-single-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Tangent Values

Calculate tangent of angles in radians using the [`math:tan()`](https://library.humio.com/data-analysis/functions-math-tan.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    myvalue := 120
    | math:tan(myvalue, as=tangent_value)

### Introduction

The [`math:tan()`](https://library.humio.com/data-analysis/functions-math-tan.html) function calculates the tangent of an angle specified in radians. The tangent is the ratio of sine to cosine (opposite/adjacent) for an angle. 

In this example, the [`math:tan()`](https://library.humio.com/data-analysis/functions-math-tan.html) function is used to calculate the tangent of an assigned value of `120` (interpreted as radians). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         myvalue := 120

Assigns the value `120` to a field named myvalue. This creates a new field with a constant value that will be used for the tangent calculation. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:tan(myvalue, as=tangent_value)

Calculates the tangent of the value in the myvalue field and returns the result in a new field named tangent_value. Note that the input value is interpreted as radians, not degrees. 

  4. Event Result set.




### Summary and Results

The query calculates the tangent of a fixed value of `120 radians`. Since tangent is a periodic function with period π (approximately 3.14159), the result represents the equivalent angle within one period. 

This query is useful for performing consistent trigonometric calculations across events, testing specific angle values in radians, or adding reference trigonometric values to existing data. 

Sample output from the incoming example data: 

tangent_value  
---  
0.320
