# Parse String as CSV - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsecsv-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse String as CSV - Example 2

Parse a CSV-encoded field into known columns using [`parseCsv()`](https://library.humio.com/data-analysis/functions-parsecsv.html) function and trim parameter defined 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    parseCsv(columns=[status, hosts, rest], trim=true)

### Introduction

The [`parseCsv()`](https://library.humio.com/data-analysis/functions-parsecsv.html) function can be used to parse a CSV-encoded field into known columns. In this example, the [`parseCsv()`](https://library.humio.com/data-analysis/functions-parsecsv.html) function is used to parse a log line with spaces and quotes and trim the output. Trimming the output is done by setting the [_`trim`_](https://library.humio.com/data-analysis/functions-parsecsv.html#query-functions-parsecsv-trim) parameter to `true`. When `true` and using quotes with trim, the spaces inside the quotes are not removed, but the quotes may come after spaces. 

Example incoming data might look like this: 

csv
    
    
    117, " crowdstrike.com, logscale.com ", 3.14

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         parseCsv(columns=[status, hosts, rest], trim=true)

CSV parses the columns field from a log line and adds the following fields to the event: status with the value `117, `, hosts with the value `" crowdstrike.com, logscale.com \"`, rest with the value ` 3.14"`. 

  3. Event Result set.




### Summary and Results

The query is used to parse a string as CSV. 

Note that if you use quotes with _`trim`_ the behavior is as follows: 

  * When [_`trim`_](https://library.humio.com/data-analysis/functions-parsecsv.html#query-functions-parsecsv-trim) set to `true`, spaces around the separation character (for example a comma) are ignored, but retained within quoted columns. For example: 

csv
        
        117 , " crowdstrike.com, humio.com " , 3.14

Would identify three columns: 

csv
        
        117," crowdstrike.com, humio.com ",3.14

Retaining the spaces at the beginning and end of a quoted column. 

  * Without trim ([_`trim=false`_](https://library.humio.com/data-analysis/functions-parsecsv.html#query-functions-parsecsv-trim)), the spaces around the character separated would be included in the values. For example: 
        
        117 , " crowdstrike.com, humio.com " , 3.14

Would identify the following three columns, as the quotation mark after the space does not start a quoted value, which means that the ',' between the two host names is interpreted as a separator: 

csv
        
        117 , " crowdstrike.com, humio.com  "

In the preceding example, there are spaces after and before columns due to the spaces around the comma separator.
