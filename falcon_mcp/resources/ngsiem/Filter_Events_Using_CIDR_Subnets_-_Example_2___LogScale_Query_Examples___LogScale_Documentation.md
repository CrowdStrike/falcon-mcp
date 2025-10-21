# Filter Events Using CIDR Subnets - Example 2 | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-cidr-2.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Filter Events Using CIDR Subnets - Example 2

Filter events using CIDR subnets to limit search to two specific IP ranges 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    cidr(ipAddress, subnet=["192.0.2.0/24", "203.0.113.0/24"])

### Introduction

The [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function can be used to filter events using CIDR subnets and is used for both IPv4 and IPv6 addresses. 

In this example, the [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function is used to match events within two IP ranges. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         cidr(ipAddress, subnet=["192.0.2.0/24", "203.0.113.0/24"])

Matches events for which the ipAddress field is in the IP range 192.0.2.0/24 or 203.0.113.0/24. 

  3. Event Result set.




### Summary and Results

The query is used to search on specific subnets within the network, uptimizing query performance. The search will only be performed on the IP addresses that fall in the range of the specified subnet filters.
