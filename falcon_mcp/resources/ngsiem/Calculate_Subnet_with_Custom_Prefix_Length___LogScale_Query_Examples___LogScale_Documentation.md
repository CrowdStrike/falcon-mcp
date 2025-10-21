# Calculate Subnet with Custom Prefix Length | LogScale Query Examples | LogScale Documentation

**URL:** https://library.humio.com/examples/examples-subnet-ip-prefix.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [LogScale Query Examples](examples.html)

## Calculate Subnet with Custom Prefix Length

Determine network address with specified bits using the [`subnet()`](https://library.humio.com/data-analysis/functions-subnet.html) function 

### Query

flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result

logscale
    
    
    subnet(ipAddress, bits=23, as=subnet)

### Introduction

The [`subnet()`](https://library.humio.com/data-analysis/functions-subnet.html) function can be used to calculate the subnet network address for an IP address using a specified prefix length. The function takes an IP address and returns the corresponding subnet address based on the number of network bits specified. 

In this example, the [`subnet()`](https://library.humio.com/data-analysis/functions-subnet.html) function is used to calculate the `/23` subnet address for IP addresses and store the result in a custom field named subnet. 

Example incoming data might look like this: 

@timestamp| ipAddress  
---|---  
2025-08-06T10:15:30.000Z| 192.168.10.45  
2025-08-06T10:15:31.000Z| 10.0.15.200  
2025-08-06T10:15:32.000Z| 172.16.100.75  
2025-08-06T10:15:33.000Z| 192.168.20.150  
2025-08-06T10:15:34.000Z| 10.0.30.25  
  
### Step-by-Step

  1. Starting with the source repository events.

  2. flowchart LR; %%{init: {"flowchart": {"defaultRenderer": "elk"}} }%% repo{{Events}} 1["Expression"] result{{Result Set}} repo --> 1 1 --> result style 1 fill:#ff0000,stroke-width:4px,stroke:#000;

logscale
         
         subnet(ipAddress, bits=23, as=subnet)

Calculates the subnet network address for each IP address in the ipAddress field. The [_`bits`_](https://library.humio.com/data-analysis/functions-subnet.html#query-functions-subnet-bits) parameter is set to `23` to specify a `/23` network prefix length. The [_`as`_](https://library.humio.com/data-analysis/functions-subnet.html#query-functions-subnet-as) parameter defines subnet as the output field name. The function returns the network address of the `/23` subnet that contains each IP address. 

  3. Event Result set.




### Summary and Results

The query is used to determine the network addresses for IP addresses using a `/23` prefix length, which creates subnets with 512 addresses each. 

This query is useful, for example, to group IP addresses by their network segments, analyze traffic patterns at the subnet level, or apply network-based policies. 

Sample output from the incoming example data: 

@timestamp| @timestamp.nanos| @timezone| ipAddress| subnet  
---|---|---|---|---  
1754475330000| 0| Z| 192.168.10.45| 192.168.10.0/23  
1754475331000| 0| Z| 10.0.15.200| 10.0.14.0/23  
1754475332000| 0| Z| 172.16.100.75| 172.16.100.0/23  
1754475333000| 0| Z| 192.168.20.150| 192.168.20.0/23  
1754475334000| 0| Z| 10.0.30.25| 10.0.30.0/23  
  
Note that the subnet addresses are stored in CIDR notation in the subnet field. 

Each subnet can contain up to 512 host addresses (9 host bits).
