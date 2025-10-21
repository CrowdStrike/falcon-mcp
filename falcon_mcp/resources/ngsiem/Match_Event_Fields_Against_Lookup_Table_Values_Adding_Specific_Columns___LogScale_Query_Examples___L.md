# Match Event Fields Against Lookup Table Values Adding Specific Columns | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-match-cidr-mode-columns.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Match Event Fields Against Lookup Table Values Adding Specific Columns

Compare event IP fields with CIDR ranges in lookup table using the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function with [_`mode`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-mode) parameter 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    match(file="cidr-file.csv", column="cidr-block", field=ip, mode=cidr, include=["info","type"])

### Introduction

The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is useful for comparing or combining data from multiple sources. The [`match()`](https://library.humio.com/data-analysis/functions-match.html) function allows searching and enriching data using CSV or JSON files, working as a filter or join operation in queries. 

In this example, the [`match()`](https://library.humio.com/data-analysis/functions-match.html) function is used to match event IP addresses against the column cidr-block of the `cidr-file.csv` file, adding specific columns details to the events. 

The query matches IP addresses against CIDR blocks (CIDR subnets) and adds specific network information from the columns info and type to the output rows. 

Example incoming event data might look like this: 

@timestamp| ip| action  
---|---|---  
2024-01-15T09:00:00.000Z| 10.0.1.25| login  
2024-01-15T09:01:00.000Z| 192.168.1.100| connect  
2024-01-15T09:02:00.000Z| 172.16.5.12| access  
  
Example `cidr-file.csv` file data might look like this: 

cidr-block| info| type| location| department  
---|---|---|---|---  
10.0.1.0/24| Internal Network| corporate| HQ| IT  
192.168.1.0/24| Development Network| test| Lab| Engineering  
172.16.0.0/16| Production Network| critical| DC| Operations  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1[\Add Field/] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         match(file="cidr-file.csv", column="cidr-block", field=ip, mode=cidr, include=["info","type"])

Uses CIDR ranges matching to match the cidr-block column of the `cidr-file.csv` lookup table file against the IP addresses (ip field) in the events, and adds specific network information to the output rows. 

It will only add the specified columns of the matching row. The column names become new field names. 

Note that when the [_`mode`_](https://library.humio.com/data-analysis/functions-match.html#query-functions-match-mode) parameter is set to `cidr`, then the event is matched if the field contains an IP address within the CIDR subnet. If multiple subnets match, the most specific one is selected, or an arbitrary one, if there are multiple equally specific subnets. 

  3. Event Result set.




### Summary and Results

The query is used to match IP addresses against CIDR blocks and add specific network information from the columns info and type to the output rows. 

The query helps analyze network traffic and security events by mapping IP addresses to network segments. 

Sample output from the incoming example data: 

@timestamp| ip| action| info| type  
---|---|---|---|---  
2024-01-15T09:00:00.000Z| 10.0.1.25| login| Internal Network| corporate  
2024-01-15T09:01:00.000Z| 192.168.1.100| connect| Development Network| test  
2024-01-15T09:02:00.000Z| 172.16.5.12| access| Production Network| critical  
  
Note how only the specified fields from the ` cidr-file.csv` file appear in output.
