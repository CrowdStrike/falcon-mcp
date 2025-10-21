# Calculate Base 2 Logarithm of Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathlog2-calculate-logarithm.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Base 2 Logarithm of Values

Calculate the base 2 logarithm using the [`math:log2()`](https://library.humio.com/data-analysis/functions-math-log2.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 8
    | math:log2(x, as=log2_result)

### Introduction

The [`math:log2()`](https://library.humio.com/data-analysis/functions-math-log2.html) function can be used to calculate the base 2 logarithm of a double field value. This function determines the exponent needed to raise 2 to obtain the given number. 

In this example, the [`math:log2()`](https://library.humio.com/data-analysis/functions-math-log2.html) function is used to calculate the base 2 logarithm of a value (`x = 8`), showing how many times you need to multiply 2 by itself to get that value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 8

Assigns the value `8` to a field named x. This value will be used to calculate its base 2 logarithm. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:log2(x, as=log2_result)

Calculates the base 2 logarithm of the value in field x and returns the result in a new field named log2_result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-log2.html#query-functions-math-log2-as) parameter is not specified, the result is returned in a field named _log2 as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the base 2 logarithm of a value, which is useful in analyzing exponential growth or decay in base 2 systems. 

This query is useful, for example, to analyze binary data sizes, calculate the number of bits needed to represent a number, or measure exponential relationships in computer science applications. 

Sample output from the incoming example data: 

log2_result  
---  
3.000  
  
The result shows that the base 2 logarithm of `8 = 3`, meaning that `2³ = 8`. This indicates that you need to multiply `2` by itself `3` times to get `8`. Some other examples: 

  * base 2 logarithm of 2 = 1 (`2¹ = 2`) 

  * base 2 logarithm of 4 = 2 (`2² = 4`) 

  * base 2 logarithm of 16 = 4 (`2⁴ = 16`) 

  * base 2 logarithm of 1 = 0 (`2⁰ = 1`)
