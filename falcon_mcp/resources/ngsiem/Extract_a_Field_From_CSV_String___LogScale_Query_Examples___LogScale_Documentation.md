# Extract a Field From CSV String | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-textsubstring-extract-csv-field.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Extract a Field From CSV String

Extract data between specific commas using the [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function with [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html)

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    motor := text:substring(myCSV, begin=text:positionOf(myCSV, character=",") + 1, end=text:positionOf(myCSV, character=",", occurrence=2))

### Introduction

The [`text:substring()`](https://library.humio.com/data-analysis/functions-text-substring.html) function can be used with [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html) to extract a specific field from a comma-separated string by finding the positions of the commas that bound the desired field. 

In this example, the functions are used together to extract the second field from a CSV string by finding the positions of the first and second commas. 

Example incoming data might look like this: 

@rawstring| @timestamp  
---|---  
myCSV="Bluesmobile,cop motor,440cu in,cop tires,cop suspension,cop shock"| 1757503124225  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         motor := text:substring(myCSV, begin=text:positionOf(myCSV, character=",") + 1, end=text:positionOf(myCSV, character=",", occurrence=2))

Extracts the second field from the CSV string using: 

     * The [_`begin`_](https://library.humio.com/data-analysis/functions-text-positionof.html#query-functions-text-positionof-begin) position is set to one character after the first comma (adding 1 to skip the comma itself) 

     * The _`end`_ position is set to the second comma's position 

     * The [_`occurrence`_](https://library.humio.com/data-analysis/functions-text-positionof.html#query-functions-text-positionof-occurrence) parameter is used to find the second comma in the string 

The result - the extracted text - is returned in a new field named motor. 

  3. Event Result set.




### Summary and Results

The query extracts text between the first and second commas in a CSV string. 

This query is useful when working with CSV data where you need to extract specific fields based on their position in the string. 

Sample output from the incoming example data: 

motor| myCSV  
---|---  
cop motor| Bluesmobile,cop motor,440cu in,cop tires,cop suspension,cop shock  
  
Note that [`text:positionOf()`](https://library.humio.com/data-analysis/functions-text-positionof.html) returns the position of the specified character, and adding 1 to the begin position skips over the comma itself.
