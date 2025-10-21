# Combine Values of Multiple Fields | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-format-combine-multipe-fields.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Combine Values of Multiple Fields

Create a new field by combining values from multiple fields using the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    format(format="%s,%s", field=[a, b], as="combined")
    table(combined)

### Introduction

The [`format()`](https://library.humio.com/data-analysis/functions-format.html) function can be used to combine values from multiple fields into a single field using a specified format pattern. 

In this example, the [`format()`](https://library.humio.com/data-analysis/functions-format.html) function is used to combine values from two fields a and b into a single field combined using a comma as a separator. 

Example incoming data might look like this: 

@timestamp| a| b  
---|---|---  
1686048000000000000| John| Smith  
1686048001000000000| Jane| Doe  
1686048002000000000| Bob| Johnson  
1686048003000000000| Alice| Brown  
1686048004000000000| Mike| Davis  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         format(format="%s,%s", field=[a, b], as="combined")

Creates a new field named combined by combining the values from fields a and b using a comma as separator. The [_`format`_](https://library.humio.com/data-analysis/functions-format.html#query-functions-format-format) parameter specifies the format string where each `%s` is replaced with the corresponding field value in the order specified in the [_`field`_](https://library.humio.com/data-analysis/functions-format.html#query-functions-format-field) parameter. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] 2["Expression"] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         table(combined)

Displays the results in a table showing only the newly created combined field. 

  4. Event Result set.




### Summary and Results

The query is used to merge values from multiple fields into a single field using a specified format pattern. 

This query is useful, for example, to create concatenated values for reporting, to prepare data for export, or to simplify complex multi-field data structures into a single field. 

Sample output from the incoming example data: 

combined  
---  
John,Smith  
Jane,Doe  
Bob,Johnson  
Alice,Brown  
Mike,Davis
