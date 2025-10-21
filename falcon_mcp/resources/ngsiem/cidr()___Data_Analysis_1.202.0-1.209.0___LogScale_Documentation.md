# cidr() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-cidr.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`cidr()`](functions-cidr.html "cidr\(\)")

The [`cidr()`](functions-cidr.html "cidr\(\)") function filters events based on IPv4 or IPv6 subnet ranges. Subnet lists can be uploaded from a CSV or JSON file. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`column`_](functions-cidr.html#query-functions-cidr-column)|  string| optional[a] |  |  When [_`file`_](functions-cidr.html#query-functions-cidr-file) and [_`column`_](functions-cidr.html#query-functions-cidr-column) parameters are used together, it loads the subnet list from the given lookup file.   
[_`field`_](functions-cidr.html#query-functions-cidr-field)[b]| string| required |  |  Specifies the field that the CIDR expression runs against.   
[_`file`_](functions-cidr.html#query-functions-cidr-file)|  string| optional[[a]](functions-cidr.html#ftn.table-functions-cidr-optparamfn) |  |  When [_`file`_](functions-cidr.html#query-functions-cidr-file) and [_`column`_](functions-cidr.html#query-functions-cidr-column) parameters are used together, it loads the subnet list from the given lookup file.   
[_`negate`_](functions-cidr.html#query-functions-cidr-negate) (deprecated)| boolean| optional[[a]](functions-cidr.html#ftn.table-functions-cidr-optparamfn) | `false`|  This parameter is deprecated. Use the `!cidr(...)` negation instead to allow only addresses that are not in the given subnet to pass through (see [`cidr()` Examples](functions-cidr.html#functions-cidr-examples "cidr\(\) Examples")) or to allow events without the assigned field to pass through. (**deprecated in 1.100**)  
[_`subnet`_](functions-cidr.html#query-functions-cidr-subnet)|  array of strings| optional[[a]](functions-cidr.html#ftn.table-functions-cidr-optparamfn) |  |  Specifies the list of IP ranges the CIDR expression matches with.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-cidr.html#query-functions-cidr-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-cidr.html#query-functions-cidr-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     cidr("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     cidr(field="value")
> 
> These examples show basic structure only.

Hide negatable operation for this function

Show negatable operation for this function

> Negatable Function Operation
> 
> This function is negatable, implying the inverse of the result. For example:
> 
> logscale Syntax
>     
>     
>     !cidr()
> 
> Or:
> 
> logscale Syntax
>     
>     
>     not cidr()
> 
> For more information, see [Negating the Result of Filter Functions](syntax-operators.html#syntax-operators-negate "Negating the Result of Filter Functions").

### Parser Behavior with Missing or Invalid Files

When using [`cidr()`](functions-cidr.html "cidr\(\)") in parser queries that reference an uploaded lookup file, the function may encounter missing or invalid files, if for example they're temporary unavailable. In such cases, the parser continues processing data normally but generates a warning message. See [Parser Warning](parsers-create.html#parser-warning) for more information. 

### [`cidr()`](functions-cidr.html "cidr\(\)") Examples

Click + next to an example below to get the full details.

#### Check if Field Contains Valid IP Address

**Check if field contains valid IP address using the[`cidr()`](functions-cidr.html "cidr\(\)") function **

##### Query

logscale
    
    
    case {
            cidr("address", subnet=["0.0.0.0/0", "::/0"]) | ip := address;
            *
    }

##### Introduction

In this example, the [`cidr()`](functions-cidr.html "cidr\(\)") function is used to check if a field contains valid IP addresses, both IPv4 and IPv6. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         case {
                 cidr("address", subnet=["0.0.0.0/0", "::/0"]) | ip := address;
                 *
         }

Checks if a field contains valid IP addresses, both IPv4 and IPv6, and then assigns that address to the field ip. 

If you only want to check for valid IPv4 addresses, use: `cidr("address", subnet="0.0.0.0/0")`

If you only want to check for valid IPv6 addresses, use: `cidr("address", subnet="::/0")`

  3. Event Result set.




##### Summary and Results

The query is used to check for valid IP addresses. 

#### Filter Events Using CIDR Subnets - Example 1

**Filter events using CIDR subnets to limit search to an IP within an IP range**

##### Query

logscale
    
    
    cidr(ipAddress, subnet="192.0.2.0/24")

##### Introduction

In this example, the [`cidr()`](functions-cidr.html "cidr\(\)") function is used to match events where an IP is within a given IP range. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         cidr(ipAddress, subnet="192.0.2.0/24")

Matches events for which the ipAddress field is in the IP range 192.0.2.0/24. 

  3. Event Result set.




##### Summary and Results

The query is used to search on specific subnets within the network, optimizing query performance. The search will only be performed on the IP addresses that fall in the range of the specified subnet filter. 

#### Filter Events Using CIDR Subnets - Example 2

**Filter events using CIDR subnets to limit search to two specific IP ranges**

##### Query

logscale
    
    
    cidr(ipAddress, subnet=["192.0.2.0/24", "203.0.113.0/24"])

##### Introduction

In this example, the [`cidr()`](functions-cidr.html "cidr\(\)") function is used to match events within two IP ranges. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         cidr(ipAddress, subnet=["192.0.2.0/24", "203.0.113.0/24"])

Matches events for which the ipAddress field is in the IP range 192.0.2.0/24 or 203.0.113.0/24. 

  3. Event Result set.




##### Summary and Results

The query is used to search on specific subnets within the network, uptimizing query performance. The search will only be performed on the IP addresses that fall in the range of the specified subnet filters. 

#### Filter Events Using CIDR Subnets - Example 3

**Filter events using CIDR subnets to match attributes listed in an uploaded cidrfile.csv**

##### Query

logscale
    
    
    cidr(field=SRC, file="cidrfile.csv", column="cidr-block")

##### Introduction

In this example, the [`cidr()`](functions-cidr.html "cidr\(\)") function is used to match events for which the SRC attributes is one of those listed in the uploaded file `cidrfile.csv` with the subnets in the column cidr-block. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         cidr(field=SRC, file="cidrfile.csv", column="cidr-block")

Matches events for which the `SRC` field is one of those listed in the uploaded file `cidrfile.csv` with the subnets in the column cidr-block. 

  3. Event Result set.




##### Summary and Results

The query is used to search on specific subnets within the network, uptimizing query performance. The search will only be performed on the IP addresses that fall in the range of the specified subnet filter. 

#### Filter Events Using CIDR Subnets - Example 4

**Filter events using CIDR subnets with negation to match events not in a given IP range**

##### Query

logscale
    
    
    !cidr(ipAddress, subnet="192.0.2.0/24")

##### Introduction

In this example, the [`cidr()`](functions-cidr.html "cidr\(\)") function is used with a negation to match events for which the `ipAddress` attributes is not in a given IP range. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         !cidr(ipAddress, subnet="192.0.2.0/24")

Matches events for which the ipAddress field is not in the IP range 192.0.2.0/24. 

  3. Event Result set.




##### Summary and Results

The query is used to search on specific subnets within the network, uptimizing query performance. The search will only be performed on the IP addresses that does not fall in the range of the specified subnet filter.
