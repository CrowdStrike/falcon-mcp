# Parse String as CSV | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsecsv-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse String as CSV

Parse a CSV-encoded field into known columns using [`parseCsv()`](https://library.humio.com/data-analysis/functions-parsecsv.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    kvParse()
    | parseCsv(result, columns=[count, status,
              completion, precision, sourcetask])

### Introduction

The [`parseCsv()`](https://library.humio.com/data-analysis/functions-parsecsv.html) function can be used to parse a CSV-encoded field into known columns. 

Example incoming data might look like this: 

Raw Events

2017-02-22T13:14:01.917+0000 [main thread] INFO statsModule got result="117 ,success ,27% ,3.14"  
---  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         kvParse()

Parses the string into key value pairs. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] 2[\Add Field/] result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | parseCsv(result, columns=[count, status,
                   completion, precision, sourcetask])

CSV parses the result field from a log line (extracted by the [`kvParse()`](https://library.humio.com/data-analysis/functions-kvparse.html) function) and adds the following fields to the event: count with the value `117`, status with the value `success`, completion with the value `27%`, and precision with the value `3.14`. 

  4. Event Result set.




### Summary and Results

The query is used to parse a string as CSV. 

Sample output from the incoming example data: 

completion| count| precision| result| status  
---|---|---|---|---  
27% | 117 | 3.14 | 117 ,success ,27% ,3.14 | success
