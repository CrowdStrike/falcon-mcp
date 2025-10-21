# Preview And Output Several Lookup Files as Events With readFile()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-readfile-multiple-file-support.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Preview And Output Several Lookup Files as Events With [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html)

Preview and output each .csv file as several events using the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    readFile(["file1.csv", "file2.csv"])

### Introduction

The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function can be used to preview content in more CSV [Lookup Files](https://library.humio.com/data-analysis/repositories-files-ui.html). The advantage of using the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function instead of the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function, is that the lookup will not be matched against data. 

In this example, the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function is used to preview and output several lookup files as events. The files will be outputted in the order specified in the file parameter. For each file, the rows will be outputted as events in the order they are in the file. 

Example incoming data from `file1.csv` might look like this: 

host_name| host_id  
---|---  
DESKTOP-VSKPBK8| 1  
FINANCE| 2  
homer-xubuntu| 3  
logger| 4  
  
Example incoming data from `file2.csv` might look like this: 

host_name| host_id  
---|---  
DESKTOP-1| 5  
DESKTOP-2| 6  
DESKTOP-3| 7  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         readFile(["file1.csv", "file2.csv"])

First outputs all the rows from `file1.csv` as events, then outputs all the rows from `file2.csv` as events. The rows maintain their original order. 

If you aim to preview the content of large files, __ls_shortname recommends always including the [_`limit`_](https://library.humio.com/data-analysis/functions-readfile.html#query-functions-readfile-limit) parameter to ensure optimal UI performance. For example: `readFile([file1.csv, file2.csv], limit=6)`. Note that the files will be outputted in the specified order, until the limit has been reached. If `file1.csv` has 4 rows and `file2.csv` has 3 rows, then the query will output all rows of `file1.csv` and 2 rows of `file2.csv`. 

If the files are utilized as data input for further manipulation, the [_`limit`_](https://library.humio.com/data-analysis/functions-readfile.html#query-functions-readfile-limit) parameter can be omitted. 

  3. Event Result set.




### Summary and Results

The query is used to preview and output content in several CSV Lookup Files as events. The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function can also be used to read tables defined with the [`defineTable()`](https://library.humio.com/data-analysis/functions-definetable.html) function. 

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
6| DESKTOP-2
