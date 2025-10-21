# Calculate Floor Modulus of Values | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathmod-calculate-modulus.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Floor Modulus of Values

Calculate the remainder using floor modulus with the [`math:mod()`](https://library.humio.com/data-analysis/functions-math-mod.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 7
    | math:mod(x, 3, as=remainder)

### Introduction

The [`math:mod()`](https://library.humio.com/data-analysis/functions-math-mod.html) function can be used to calculate the floor modulus (remainder) of a division operation, for example, `x mod y` where `y` is the divisor and x is a field. Both the [_`field`_](https://library.humio.com/data-analysis/functions-math-mod.html#query-functions-math-mod-field) and [_`divisor`_](https://library.humio.com/data-analysis/functions-math-mod.html#query-functions-math-mod-divisor) are floor rounded before the calculation. 

In this example, the [`math:mod()`](https://library.humio.com/data-analysis/functions-math-mod.html) function is used to calculate the remainder when a field value is divided by a specified [_`divisor`_](https://library.humio.com/data-analysis/functions-math-mod.html#query-functions-math-mod-divisor) (`y = 3` in this case). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 7

Assigns the value `7` to a field named x. This field value will be divided by the divisor in the modulus calculation. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:mod(x, 3, as=remainder)

Calculates the floor modulus of the field value x with divisor (`y`) `3`, and returns the result in a new field named remainder. Both values are floor rounded before the calculation. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-mod.html#query-functions-math-mod-as) parameter is not specified, the result is returned in a field named _mod as default. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the remainder after division using floor modulus, which handles both positive and negative numbers consistently. 

This query is useful, for example, to determine if numbers are divisible evenly by a specific value, to implement circular buffers, or to distribute items evenly across groups. 

Sample output from the incoming example data: 

remainder  
---  
1  
  
The result shows that when `7` is divided by `3`, the remainder is `1` (as `7 = 2 × 3 + 1`). 

The function can also handle: 

  * Negative numbers (for example, `-7 mod 3 = 2`) 

  * Decimal values (for example, `7.8 mod 3 = 1`, as the value is floor rounded first) 

  * Decimal divisors (which are also floor rounded before calculation)
