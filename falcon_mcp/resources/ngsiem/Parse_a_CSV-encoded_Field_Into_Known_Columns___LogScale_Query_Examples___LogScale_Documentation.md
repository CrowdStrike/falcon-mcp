# Parse a CSV-encoded Field Into Known Columns | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-parsecsv-logline-known-columns.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Parse a CSV-encoded Field Into Known Columns

Parse a CSV-encoded Field into known columns and add it to the event using the parseCsv() function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    parseCsv(result, columns=[count, status, completion, precision, sourcetask])

### Introduction

The parseCsv() function can be used to parse a CSV-encoded field into known columns. 

In this example, the parseCsv() function is used to parse a log line. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         parseCsv(result, columns=[count, status, completion, precision, sourcetask])

Parses a CSV-encoded field into known columns. 

In this example, where the parsed field is from a log line, using `parseCsv(result, columns=[count, status, completion, precision, sourcetask])` will add these fields to the event: 

     * `count: 117`

     * `status: success`

     * `completion: 27%`

     * `precision: 3.14`

  3. Event Result set.




### Summary and Results

The query is used to parse a CSV-encoded field into known columns. CSV files are often used to exchange data between systems.
