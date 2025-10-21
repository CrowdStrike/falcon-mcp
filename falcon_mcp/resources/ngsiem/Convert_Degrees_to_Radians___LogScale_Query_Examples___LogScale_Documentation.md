# Convert Degrees to Radians | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathdeg2rad-convert-degrees.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Degrees to Radians

Convert angles from degrees to radians using the [`math:deg2rad()`](https://library.humio.com/data-analysis/functions-math-deg2rad.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    myvalue := 180.0
            | math:deg2rad(myvalue, as=radians)

### Introduction

The [`math:deg2rad()`](https://library.humio.com/data-analysis/functions-math-deg2rad.html) function converts angle measurements from degrees to radians. One degree equals approximately `0.0174533` radians (`π/180`). 

Common degree to radian conversions: 

  * 180 degrees = π radians 

  * 90 degrees = π/2 radians 

  * 45 degrees = π/4 radians 

  * 30 degrees = π/6 radians 




In this example, the [`math:deg2rad()`](https://library.humio.com/data-analysis/functions-math-deg2rad.html) function is used to convert the degree value `180` to radians. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         myvalue := 180.0

Assigns `180` degrees to a field named myvalue. This value should convert to approximately `π` radians. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:deg2rad(myvalue, as=radians)

Converts the degree value in the myvalue field to radians and returns the result in a field named radians. 

  4. Event Result set.




### Summary and Results

The query converts an angle measurement from degrees to radians. This conversion is essential when working with trigonometric functions, as many mathematical operations require radians rather than degrees. 

This query is useful for preparing angular measurements for mathematical calculations, working with geometric computations, or transforming human-readable angles into formats suitable for mathematical operations. The conversion factor used is `π/180` (approximately 0.0174533 radians per degree). 

Sample output from the incoming example data: 

radians  
---  
3.14159  
  
The result shows that `180` degrees converts to `π` radians (approximately `3.14159`), demonstrating the standard conversion between degrees and radians.
