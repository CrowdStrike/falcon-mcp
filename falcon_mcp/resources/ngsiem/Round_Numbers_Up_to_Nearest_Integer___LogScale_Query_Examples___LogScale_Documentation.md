# Round Numbers Up to Nearest Integer | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathceil-round-up.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Round Numbers Up to Nearest Integer

Round a number up to the nearest integer using the [`math:ceil()`](https://library.humio.com/data-analysis/functions-math-ceil.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    x := 3.1
    | math:ceil(x, as=result)

### Introduction

The [`math:ceil()`](https://library.humio.com/data-analysis/functions-math-ceil.html) function can be used to round a double-precision number up to the nearest integer. It returns the smallest integer value that is greater than or equal to the input value, effectively rounding up regardless of the decimal portion. 

In this example, the [`math:ceil()`](https://library.humio.com/data-analysis/functions-math-ceil.html) function is used to demonstrate ceiling rounding behavior with a decimal number, showing how it always rounds up to the next integer regardless of the decimal value. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         x := 3.1

Assigns the double-precision floating-point value `3.1` to a field named x. This value will demonstrate how ceiling rounding always rounds up to the next integer, even with a small decimal portion. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:ceil(x, as=result)

Rounds up the value in field x to the nearest integer and returns the result in a new field named result. If the [_`as`_](https://library.humio.com/data-analysis/functions-math-ceil.html#query-functions-math-ceil-as) parameter is not specified, the result is returned in a field named _ceil as default. 

  4. Event Result set.




### Summary and Results

The query is used to round numbers up to the nearest integer, which is useful when you need to ensure values are not underestimated or when working with whole units that cannot be fractional. 

This query is useful, for example, to calculate minimum container needs, determine upper bounds for resource allocation, or round up time durations to whole units. 

Sample output from the incoming example data: 

result  
---  
4.0  
  
The result shows that `math:ceil(3.1) = 4.0`, demonstrating how the function always rounds up to the next integer regardless of the decimal portion. 

Note that ceiling rounding has distinct behaviors for different types of numbers: positive numbers round up to the next integer, negative numbers round up toward zero, and integers remain unchanged. For example: `math:ceil(3.9) = 4.0`, `math:ceil(-3.1) = -3.0`, `math:ceil(5.0) = 5.0`.
