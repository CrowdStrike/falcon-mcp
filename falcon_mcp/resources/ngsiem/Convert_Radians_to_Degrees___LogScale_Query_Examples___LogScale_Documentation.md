# Convert Radians to Degrees | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-mathrad2deg-convert-radians.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Convert Radians to Degrees

Convert angles from radians to degrees using the [`math:rad2deg()`](https://library.humio.com/data-analysis/functions-math-rad2deg.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    myvalue := 3.14159
    | math:rad2deg(myvalue, as=degrees)

### Introduction

The [`math:rad2deg()`](https://library.humio.com/data-analysis/functions-math-rad2deg.html) function converts angle measurements from radians to degrees. One radian equals approximately `57.2958` degrees (`180/π`). 

Common radian to degree conversions: 

  * π radians = 180 degrees 

  * π/2 radians = 90 degrees 

  * π/4 radians = 45 degrees 

  * π/6 radians = 30 degrees 




In this example, the [`math:rad2deg()`](https://library.humio.com/data-analysis/functions-math-rad2deg.html) function is used to convert the radian value `3.14159` to degrees. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         myvalue := 3.14159

Assigns approximately `π` radians to a field named myvalue. This value should convert to approximately `180` degrees. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | math:rad2deg(myvalue, as=degrees)

Converts the radian value in the myvalue field to degrees and returns the result in a field named degrees. 

  4. Event Result set.




### Summary and Results

The query converts an angle measurement from radians to degrees. This conversion is essential when working with trigonometric functions, as many mathematical operations use radians while human-readable angles are typically expressed in degrees. 

This query is useful for converting angular measurements, working with geometric calculations, or transforming mathematical results into more readable formats. The conversion factor used is `180/π` (approximately 57.2958 degrees per radian). 

Sample output from the incoming example data: 

degrees  
---  
180.000  
  
The result shows that `π` radians (approximately `3.14159`) converts to `180` degrees, demonstrating the standard conversion between radians and degrees.
