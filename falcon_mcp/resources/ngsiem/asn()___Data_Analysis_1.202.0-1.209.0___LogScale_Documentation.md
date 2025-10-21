# asn() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-asn.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`asn()`](functions-asn.html "asn\(\)")

Sets the autonomous system (AS) number and organization associated with a given IP address. 

By default, uses the ip field as the input. If an AS organization associated with the IP address, then two new fields matching the input field name are created with the AS number and organization. For example, using the default, the new fields would be ip.asn and ip.org. 

LogScale includes GeoLite2 data created by MaxMind, available from [MaxMind's website](https://www.maxmind.com/en/home). By default, the database is updated automatically if the cluster is running with a valid LogScale license. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-asn.html#query-functions-asn-as)|  string| optional[a] | `(input field)`|  The name prefix of fields added by this function. Defaults to input field.   
[_`field`_](functions-asn.html#query-functions-asn-field)[b]| string| optional[[a]](functions-asn.html#ftn.table-functions-asn-optparamfn) | `ip`|  The field with an IP address for which to get the AS number.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-asn.html#query-functions-asn-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-asn.html#query-functions-asn-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     asn("value")
> 
> and:
> 
> logscale Syntax
>     
>     
>     asn(field="value")
> 
> These examples show basic structure only.

The autonomous system number will be written as ip.asn, and organization name as ip.org. 

### [`asn()`](functions-asn.html "asn\(\)") Examples

Click + next to an example below to get the full details.

#### Determine Autonomous System (AS) Number and IP address/Organization Associated - Example 1

**Determine the autonomous system (AS) number and organization associated with a given IP address**

##### Query

logscale
    
    
    asn(field=address)

##### Introduction

The [`asn()`](functions-asn.html "asn\(\)") function provides the Autonomous System Number (ASN) of a given IP address, providing information on the owner. By default, [`asn()`](functions-asn.html "asn\(\)") uses the ip field as the input parameter. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         asn(field=address)

Adds the ASN to a given event (based on the field address) in the fields address.asn and address.org are added to the event. 

  3. Event Result set.




##### Summary and Results

The query is used to automatically add an AS number to its associated IP address (and organization with that IP address associated). Knowing the Autonomos System Number of the associated IP addresses is useful to identify registered owners/organizations of an IP range. When using the ASN search to query a list of IP addresses, it is possible to mix IPv4 and IPv6 addresses within the one query. 

#### Determine Autonomous System (AS) Number and IP address/Organization Associated - Example 2

**Determine the autonomous system (AS) number and organization associated with a given IP address**

##### Query

logscale
    
    
    asn(field=ipaddr,as=address)

##### Introduction

The [`asn()`](functions-asn.html "asn\(\)") function assumes the default values ip for input parameter and outputs to new fields based on this field name. This can be modified by using the [_`as`_](functions-asn.html#query-functions-asn-as) parameter. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         asn(field=ipaddr,as=address)

Adds the fields address.asn and address.org (based on the field ipaddr) to the event. 

  3. Event Result set.




##### Summary and Results

The query is used to automatically add an AS number to its associated IP address (and organization with that IP address associated). Knowing the Autonomos System Number of the associated IP addresses is useful to identify registered owner/organizations of an IP range. When using the ASN search to query a list of IP addresses, it is possible to mix IPv4 and IPv6 addresses within the one query.
