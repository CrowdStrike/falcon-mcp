# Match Multiple Pairs of Event Fields Against Multiple Columns in .CSV Lookup File | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-match-multiple-pairs.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

##  Match Multiple Pairs of Event Fields Against Multiple Columns in .CSV Lookup File

Compare multiple pairs of event fields against multiple columns in a .CSV lookup file using the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    match(test.csv, field=[field1, field2], column=[column1, column2])

### Introduction

The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is useful for comparing or combining data from multiple sources. The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function allows searching and enriching data using CSV or JSON files, working as a filter or join operation in queries. 

In this example, the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is used to match multiple pairs of fields against multiple columns in a CSV file named `test.csv` simultaneously. 

Example incoming event data might look like this: 

json
    
    
    [
       {
          "field1" : "c",
          "field2" : "f"
       },
       {
          "field2" : "e",
          "field1" : "c"
       }
    ]

Example `test.csv` file data might look like this: 

column1| column2| column3  
---|---|---  
a| b| d  
c| d| a  
c| e| f  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         match(test.csv, field=[field1, field2], column=[column1, column2])

For each event, checks if field1 matches column1 and field2 matches column2

  3. Event Result set.




### Summary and Results

The query is used to match multiple pairs of event fields against multiple columns in the .CSV file named `test.csv`. Multiple field matching helps validate and enrich complex event data. 

Sample output from the incoming example data: 

column3| field1| field2  
---|---|---  
f| c| e
