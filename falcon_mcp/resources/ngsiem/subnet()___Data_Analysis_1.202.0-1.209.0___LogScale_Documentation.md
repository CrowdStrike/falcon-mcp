# subnet() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-subnet.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`subnet()`](functions-subnet.html "subnet\(\)")

Compute a subnet from a ipv4 field; by default emits a into a _subnet field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-subnet.html#query-functions-subnet-as)|  string| optional[a] | `_subnet`|  Specifies the name of the output field.   
[_`bits`_](functions-subnet.html#query-functions-subnet-bits)|  number| required |  |  Specifies the prefix bits to include in the subnet, for example, 23.   
[_`field`_](functions-subnet.html#query-functions-subnet-field)[b]| string| required |  |  Specifies the input field.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-subnet.html#query-functions-subnet-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-subnet.html#query-functions-subnet-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     subnet("value",bits="value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     subnet(field="value",bits="value")
> 
> These examples show basic structure only.

### [`subnet()`](functions-subnet.html "subnet\(\)") Syntax Examples

Compute subnet for ipAddress using 23bit prefix; emit into subnet field 

logscale
    
    
    subnet(ipAddress, bits=23, as=subnet)

### [`subnet()`](functions-subnet.html "subnet\(\)") Examples

Click + next to an example below to get the full details.

#### Calculate Subnet with Custom Prefix Length

**Determine network address with specified bits using the[`subnet()`](functions-subnet.html "subnet\(\)") function **

##### Query

logscale
    
    
    subnet(ipAddress, bits=23, as=subnet)

##### Introduction

In this example, the [`subnet()`](functions-subnet.html "subnet\(\)") function is used to calculate the `/23` subnet address for IP addresses and store the result in a custom field named subnet. 

Example incoming data might look like this: 

@timestamp| ipAddress  
---|---  
2025-08-06T10:15:30.000Z| 192.168.10.45  
2025-08-06T10:15:31.000Z| 10.0.15.200  
2025-08-06T10:15:32.000Z| 172.16.100.75  
2025-08-06T10:15:33.000Z| 192.168.20.150  
2025-08-06T10:15:34.000Z| 10.0.30.25  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         subnet(ipAddress, bits=23, as=subnet)

Calculates the subnet network address for each IP address in the ipAddress field. The [_`bits`_](functions-subnet.html#query-functions-subnet-bits) parameter is set to `23` to specify a `/23` network prefix length. The [_`as`_](functions-subnet.html#query-functions-subnet-as) parameter defines subnet as the output field name. The function returns the network address of the `/23` subnet that contains each IP address. 

  3. Event Result set.




##### Summary and Results

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
