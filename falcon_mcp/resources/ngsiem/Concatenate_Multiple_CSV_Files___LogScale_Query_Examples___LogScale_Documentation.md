# Concatenate Multiple CSV Files | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-readfile-concatenate-multiple-csv-files.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Concatenate Multiple CSV Files

Combine data from multiple CSV files into a single result set using the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    readFile("users_2024.csv", "users_2025.csv", "temp_users.csv")

### Introduction

The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function can be used to read data from CSV files, lookup files and tables. When provided with multiple file or table names, it concatenates the data from all specified sources, combining them into a single result set. 

In this example, the [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function is used to concatenate data from multiple CSV files named `users_2024.csv`, `users_2025.csv`, and `temp_users.csv`, combining all events into a single result set. 

Example data in the CSV files might look like this: 

File `users_2024.csv`: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
  
File `users_2025.csv`: 

user_id| name| department| join_date  
---|---|---|---  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
  
File `temp_users.csv`: 

user_id| name| department| join_date  
---|---|---|---  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1@{ shape: doc, label: "Source or File" } result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         readFile("users_2024.csv", "users_2025.csv", "temp_users.csv")

Reads and concatenates data from three CSV files: `users_2024.csv`, `users_2025.csv`, and `temp_users.csv`. The [`readFile()`](https://library.humio.com/data-analysis/functions-readfile.html) function processes each CSV file in the order specified and combines all events into a single result set, with events from the first file appearing first, followed by events from subsequent files. 

  3. Event Result set.




### Summary and Results

The query is used to combine data from multiple CSV files into a single unified event set by concatenating their contents. 

This query is useful, for example, to merge data exports from different time periods, combine CSV files from multiple departments or regions, or consolidate data from various external sources for comprehensive analysis. 

Sample output from the incoming example data: 

user_id| name| department| join_date  
---|---|---|---  
001| Alice Johnson| Engineering| 2024-01-15  
002| Bob Smith| Marketing| 2024-03-22  
003| Carol Davis| Sales| 2024-06-10  
004| David Wilson| Engineering| 2025-01-08  
005| Emma Brown| HR| 2025-02-14  
006| Frank Miller| Sales| 2025-03-01  
007| Grace Lee| Marketing| 2025-07-20  
008| Henry Taylor| Engineering| 2025-08-15  
  
Note that the CSV files could be different formats (field names and content), but typically the schemas would match which will make it easier to query and display in a widget. 

The events appear in the output in the same order as the files are specified in the function call, with all events from the first file appearing before any events from the second file, and so on.
