# Concatenate Fields and Strings Together | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-format-not-concat.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Fields and Strings Together

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    format("%s/%s",field=[dirname,filename],as=pathname)

### Introduction

The [`concat()`](https://library.humio.com/data-analysis/functions-concat.html) is not able to concatenate fields and strings together. For example to create a pathname based on the directory and filename it is not possible to do: 

logscale
    
    
    concat([dirname,"/",filename],as=pathname)

This will raise an error. Instead, we can use [`format()`](https://library.humio.com/data-analysis/functions-format.html). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         format("%s/%s",field=[dirname,filename],as=pathname)

Formats a value separating the two by a forward slash, creating the field pathname

  3. Event Result set.




### Summary and Results

The [`format()`](https://library.humio.com/data-analysis/functions-format.html) function provides a flexible method of formatting data, including encapsulating or combining strings and fields together.
