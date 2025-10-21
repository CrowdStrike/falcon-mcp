# Rename a Single Field - Example 1 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-rename-single-field-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Rename a Single Field - Example 1

Rename a single field using the [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function with the [_`as`_](https://library.humio.com/data-analysis/syntax-fields.html#syntax-fields-from-functions) parameter to define the new name of the field 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    rename(field=badName, as=goodName)

### Introduction

The [`rename()`](https://library.humio.com/data-analysis/functions-rename.html) function is used to rename one or more fields. In this example, only one field is renamed using the [_`as`_](https://library.humio.com/data-analysis/functions-rename.html#query-functions-rename-as) parameter to define the new name of the field. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         rename(field=badName, as=goodName)

Renames the field badName to goodName. 

  3. Event Result set.




### Summary and Results

The query is used to quickly rename single fields.
