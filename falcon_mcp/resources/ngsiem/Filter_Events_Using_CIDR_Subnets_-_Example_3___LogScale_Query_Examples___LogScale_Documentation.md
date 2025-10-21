# Filter Events Using CIDR Subnets - Example 3 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-cidr-3.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Events Using CIDR Subnets - Example 3

Filter events using CIDR subnets to match attributes listed in an uploaded cidrfile.csv 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    cidr(field=SRC, file="cidrfile.csv", column="cidr-block")

### Introduction

The [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function can be used to filter events using CIDR subnets and is used for both IPv4 and IPv6 addresses. 

In this example, the [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function is used to match events for which the SRC attributes is one of those listed in the uploaded file `cidrfile.csv` with the subnets in the column cidr-block. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         cidr(field=SRC, file="cidrfile.csv", column="cidr-block")

Matches events for which the `SRC` field is one of those listed in the uploaded file `cidrfile.csv` with the subnets in the column cidr-block. 

  3. Event Result set.




### Summary and Results

The query is used to search on specific subnets within the network, uptimizing query performance. The search will only be performed on the IP addresses that fall in the range of the specified subnet filter.
