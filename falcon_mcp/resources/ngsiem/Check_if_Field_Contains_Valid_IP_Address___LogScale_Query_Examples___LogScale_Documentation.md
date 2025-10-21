# Check if Field Contains Valid IP Address | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-cidr-5.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Check if Field Contains Valid IP Address

Check if field contains valid IP address using the [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    case {
            cidr("address", subnet=["0.0.0.0/0", "::/0"]) | ip := address;
            *
    }

### Introduction

The [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function can be used to filter events using CIDR subnets and is used for both IPv4 and IPv6 addresses. 

In this example, the [`cidr()`](https://library.humio.com/data-analysis/functions-cidr.html) function is used to check if a field contains valid IP addresses, both IPv4 and IPv6. 

### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         case {
                 cidr("address", subnet=["0.0.0.0/0", "::/0"]) | ip := address;
                 *
         }

Checks if a field contains valid IP addresses, both IPv4 and IPv6, and then assigns that address to the field ip. 

If you only want to check for valid IPv4 addresses, use: `cidr("address", subnet="0.0.0.0/0")`

If you only want to check for valid IPv6 addresses, use: `cidr("address", subnet="::/0")`

  3. Event Result set.




### Summary and Results

The query is used to check for valid IP addresses.
