# Preview Content in a Lookup File With readFile()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-readfile-preview-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Preview Content in a Lookup File With [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html)

Preview content in a lookup file in the search portion of a repo without having to match the lookup against data 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    readFile("host_names.csv")

### Introduction

The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function can be used to preview content in a CSV [Lookup File](https://library.humio.com/data-analysis/repositories-files-ui.html). The advantage of using the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function instead of the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function, is that the lookup will not be matched against data. 

In this example, the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function is used to look up a host_names.csv file just to preview the content in it. 

Example incoming data might look like this: 
    
    
    |--------------------|
    | host_name, host_id |
    | DESKTOP-VSKPBK8, 1 |
    | FINANCE, 2         |
    | homer-xubuntu, 3   |
    | logger, 4          |
    | DESKTOP-1, 5       |
    | DESKTOP-2, 6       |
    | DESKTOP-3, 7       |
    |--------------------|

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         readFile("host_names.csv")

Displays the content of the .csv file. 

If you aim to preview the content of large files, we recommend always including the [_`limit`_](https://library.humio.com/data-analysis/functions-readfile.html#query-functions-readfile-limit) parameter to ensure optimal UI performance. For example: `readFile("host_names.csv", limit=5)`. However, if the file is utilized as data input for further manipulation, the [_`limit`_](https://library.humio.com/data-analysis/functions-readfile.html#query-functions-readfile-limit) parameter can be omitted. 

Notice that if reading a file from a package, then the package name should be specified in addition to the filename. For example: `readFile("falcon/investigate/logoninfo.csv")`. 

  3. Event Result set.




### Summary and Results

The query is used to preview content in CSV Lookup Files. After previewing the content with the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function, it is possible to use the data for further manipulation, for example combine it with [`count()`](https://library.humio.com/data-analysis/functions-count.html) to count the rows, [`select()`](https://library.humio.com/data-analysis/functions-select.html) to filter data, [`join()`](https://library.humio.com/data-analysis/functions-join.html) to match data, etc. 

The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function can also be used to read tables defined with the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function. See [Perform a Right Join Query to Combine Two Datasets](examples-define-table-right.html "Perform a Right Join Query to Combine Two Datasets")

Sample output from the incoming example data: 

host_id| host_name  
---|---  
1| DESKTOP-VSKPBK8  
2| FINANCE  
3| homer-xubuntu  
4| logger  
5| DESKTOP-1  
6| DESKTOP-2  
7| DESKTOP-3  
  
Sample output from the incoming example data with [_`limit`_](https://library.humio.com/data-analysis/functions-readfile.html#query-functions-readfile-limit) parameter: 

host_id| host_name  
---|---  
1| DESKTOP-VSKPBK8  
2| FINANCE  
3| homer-xubuntu  
4| logger  
5| DESKTOP-1
