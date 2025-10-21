# Calculate Sine of a Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathsin-positive-value.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Sine of a Value

Compute trigonometric sine using the [`math:sin()`](https://library.humio.com/data-analysis/functions-math-sin.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    myvalue := 345
    | math:sin(myvalue, as=mathvalue)

### Introduction

The [`math:sin()`](https://library.humio.com/data-analysis/functions-math-sin.html) function can be used to calculate the sine of an angle specified in radians. It accepts both positive and negative values and returns a value between -1 and 1. 

In this example, the [`math:sin()`](https://library.humio.com/data-analysis/functions-math-sin.html) function is used to calculate the sine of a positive value, demonstrating how the function handles standard input. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         myvalue := 345

Assigns the positive value `345` to a variable named myvalue for use in subsequent calculations. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[[Expression]] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:sin(myvalue, as=mathvalue)

Calculates the sine of the value in the myvalue field and returns the result in a new field named mathvalue. The [`math:sin()`](https://library.humio.com/data-analysis/functions-math-sin.html) function automatically handles the conversion of the input value to radians and returns a value between -1 and 1. 

  4. Event Result set.




### Summary and Results

The query is used to calculate the sine of a positive angle value, demonstrating basic trigonometric calculations. 

This query is useful, for example, to analyze periodic data, process angular measurements, or calculate wave functions in scientific applications. 

Sample output from the incoming example data: 

mathvalue  
---  
-0.9589243  
  
Note that the sine value for 345 radians is the exact opposite of the sine of -345 radians, demonstrating the odd symmetry property of the sine function where `sin(-x) = -sin(x)`.
