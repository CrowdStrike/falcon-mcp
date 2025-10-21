# Deduplicate Values in Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-arraydedup-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Deduplicate Values in Array

Remove duplicate values in an array using [`array:dedup()`](https://library.humio.com/data-analysis/functions-array-dedup.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    parseJson()
    | array:dedup("emails[]")

### Introduction

The [`array:dedup()`](https://library.humio.com/data-analysis/functions-array-dedup.html) function can be used to remove duplicate values in an array. 

In this example, the function removes duplicates in the array emails[]. 

Example incoming data might look like this: 

Raw Events

{"emails": ["john@mail.com", "admin@mail.com", "jane@mail.com", "admin@mail.com"]}  
---  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         parseJson()

Parses the incoming data to identify JSON values and converts them into a usable field. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[/Filter/] 2{{Aggregate}} result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | array:dedup("emails[]")

Removes duplicate values in the array emails[]. 

  4. Event Result set.




### Summary and Results

The query is used to remove duplicate values in an array. 

Sample output from the incoming example data: 

emails[0]| emails[1]| emails[2]  
---|---|---  
john@mail.com| admin@mail.com| jane@mail.com
