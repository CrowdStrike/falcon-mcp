# Preview Content in a Lookup File With readFile() and Filter With !join()

     | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-readfile-join-1.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Preview Content in a Lookup File With [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) and Filter With ![`join()`](https://library.humio.com/data-analysis/functions-join.html)

Preview content in a lookup file in the search portion of a repo and filter for specific data with the ![`join()`](https://library.humio.com/data-analysis/functions-join.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2@{ shape: processes, label: "Join" } result{{Result Set}} repo --> 1 1 --> 2 2 --> result

logscale
    
    
    readFile("host_names.csv")
    | !join(query={groupBy(host_name)}, field=host_name, key=host_name, include=[host_name, id])

### Introduction

The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function can be used to preview content in a CSV [Lookup File](https://library.humio.com/data-analysis/repositories-files-ui.html). 

In this example, the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function is used to look up a host_names.csv file, and then filter for host names that do not send any logs. 

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

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2@{ shape: processes, label: "Join" } result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         readFile("host_names.csv")

Displays the content of the .csv file. 

  3. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } 2@{ shape: processes, label: "Join" } result{{Result Set}} repo --> 1 1 --> 2 2 --> result style 2 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         | !join(query={groupBy(host_name)}, field=host_name, key=host_name, include=[host_name, id])

Filters for host names that do not send any logs. 

  4. Event Result set.




### Summary and Results

The query is used to preview content in CSV Lookup Files, and then filter for host names that do not send any logs. 

Sample output from the incoming example data: 

host_id| host_name  
---|---  
5| DESKTOP-1  
6| DESKTOP-2  
7| DESKTOP-3
