# Rename Existing Fields in Array | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-array-rename-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Rename Existing Fields in Array

Rename existing fields in an array using the [`array:rename()`](https://library.humio.com/data-analysis/functions-array-rename.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    array:rename(array="mail[]", asArray="user.email[]")

### Introduction

The [`array:rename()`](https://library.humio.com/data-analysis/functions-array-rename.html) function is used to rename existing fields in an array provided that the array has continuous, sequential indexes with no empty indexes and that it starts at [0]. 

In this example, the [`array:rename()`](https://library.humio.com/data-analysis/functions-array-rename.html) function is used to rename the array mail[] as user.email[]. 

Example incoming data might look like this: 
    
    
    'mail[0]'='user0@example.com'
    'mail[1]'='user1@example.com'
    'mail[2]'='user2@example.com'

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{{Aggregate}} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         array:rename(array="mail[]", asArray="user.email[]")

Renames the array mail[] as user.email[]. If there are empty entries in the array, only the fields from index 0 up to the first empty index will be renamed. If an array with the new name already exists, it will be overwritten. 

  3. Event Result set.




### Summary and Results

The query is used to rename fields in an array. Renaming the mail[] array is useful when, for example, modifying vendor logs email addresses into ECS data model is needed. 

Sample output from the incoming example data: 
    
    
    user.email[0]->user0@example.com
    user.email[1]->user1@example.com
    user.email[2]->user2@example.com
