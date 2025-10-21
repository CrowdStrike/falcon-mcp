# Set a Field Value Based on Tag Value | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-if-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Set a Field Value Based on Tag Value

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    keyprocess := if(#eventType == "Spawn", then=ChildID, else=ProcessID)

### Introduction

When processing event data, there are occasions when a value needs to be determined from another field in the event. In this example, the field keyprocess is populated based on the #eventType tag. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         keyprocess := if(#eventType == "Spawn", then=ChildID, else=ProcessID)

Using the [`if()`](https://library.humio.com/data-analysis/functions-if.html), set the value of keyprocess to the value of the ChildID if #eventType is `Spawn`; otherwise, set keyprocess to ProcessID. 

  3. Event Result set.




### Summary and Results

Using [`if()`](https://library.humio.com/data-analysis/functions-if.html) provides a simplified way of processing and parsing data when the test value can be easily identified. 

In this example, the process ID has been identified based on whether it is the original or a spawn (child) process.
