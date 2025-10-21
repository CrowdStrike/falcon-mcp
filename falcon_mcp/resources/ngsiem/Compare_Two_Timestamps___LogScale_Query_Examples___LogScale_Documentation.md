# Compare Two Timestamps | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-duration-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Compare Two Timestamps

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2[[Expression]] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    diff := endTime - startTime
    | test(diff > duration("5m"))

### Introduction

The [`duration()`](https://library.humio.com/data-analysis/functions-duration.html) function returns the number of milliseconds for a given duration specification. This value can be used as the basis for comparison for different values. 

In this example, the [`duration()`](https://library.humio.com/data-analysis/functions-duration.html) function is used to compute a simple value to use in a comparison. The input data contains the startTime and endTime for an operation, to determine whether the difference between the two exceeds a duration of 5 minutes. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2[[Expression]] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         diff := endTime - startTime

Determines the difference between the endTime and startTime; the fields should be in milliseconds (as they would be for an epoch or timestamp). 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1>Augment Data] 2[[Expression]] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | test(diff > duration("5m"))

Use the [`test()`](https://library.humio.com/data-analysis/functions-test.html) function to determine if the computed difference is greater than a duration of 5 minutes. In this case, [`duration()`](https://library.humio.com/data-analysis/functions-duration.html) returns 300,000. 

  4. Event Result set.




### Summary and Results

The [`duration()`](https://library.humio.com/data-analysis/functions-duration.html) functions supports a more convenient, and human-readable, method of defining a duration without needing to explicitly calculate the comparison. This is particularly useful when using parameters on a dashboard.
