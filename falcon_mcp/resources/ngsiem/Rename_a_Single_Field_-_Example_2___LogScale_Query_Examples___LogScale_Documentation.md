# Rename a Single Field - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-rename-single-field-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Rename a Single Field - Example 2

Rename a single field using the [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function with assignment syntax to define the new name of the field 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    goodName := rename(badName)

### Introduction

The [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function is used to rename one or more fields. In this example, only one field is renamed using the assignment operator (`:=`). 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1{Conditional} result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         goodName := rename(badName)

Renames the badName field to goodName by assigning the new value (variable name) to the field. The value on the right side of the assignment operator is set equal to the value on the left side of it. 

  3. Event Result set.




### Summary and Results

The query is used to quickly rename single fields.
