# Add a Field Based on Values of Another Field - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-if-5.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Add a Field Based on Values of Another Field - Example 1

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    | statusClass :=
    if(regex("^1", field=statuscode), then="informational", else=
    if(regex("^2", field=statuscode), then="successful", else=
    if(regex("^3", field=statuscode), then="redirection", else=
    if(regex("^4", field=statuscode), then="client error", else=
    if(regex("^5", field=statuscode), then="server error", else=
    "unknown")))))

### Introduction

Nested [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions can be used within a larger expression for adding a field whose value is calculated based on another field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | statusClass :=
         if(regex("^1", field=statuscode), then="informational", else=
         if(regex("^2", field=statuscode), then="successful", else=
         if(regex("^3", field=statuscode), then="redirection", else=
         if(regex("^4", field=statuscode), then="client error", else=
         if(regex("^5", field=statuscode), then="server error", else=
         "unknown")))))

Add a statusClass field where the following conditions are set: 

     * If the value of field statuscode begins with `1`, then statusClass is labeled as `informational`, otherwise: 

     * If the value of field statuscode begins with `2`, then statusClass is labeled as `successful`, otherwise: 

     * If the value of field statuscode begins with `3`, then statusClass is labeled as `redirection`, otherwise: 

     * If the value of field statuscode begins with `4`, then statusClass is labeled as `client error`, otherwise: 

     * If the value of field statuscode begins with `5`, then statusClass is labeled as `server error`, otherwise it is labeled as `unknown`. 

  3. Event Result set.




### Summary and Results

Nested [`if()`](https://library.humio.com/data-analysis/functions-if.html) functions for tagging a field according to different statuscode values.
