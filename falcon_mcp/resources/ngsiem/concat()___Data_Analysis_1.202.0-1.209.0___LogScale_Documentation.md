# concat() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-concat.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`concat()`](functions-concat.html "concat\(\)")

Concatenates the values of a list of fields into a single value in a new field. 

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-concat.html#query-functions-concat-as)|  string| optional[a] | `_concat`|  The output name of the field to set.   
[_`field`_](functions-concat.html#query-functions-concat-field)[b]| array of strings| required |  |  Fields to concatenate.   
[a] Optional parameters use their default value unless explicitly set.[b] The parameter name [_`field`_](functions-concat.html#query-functions-concat-field) can be omitted.  
  
Hide omitted argument names for this function

Show omitted argument names for this function

> Omitted Argument Names
> 
> The argument name for [_`field`_](functions-concat.html#query-functions-concat-field) can be omitted; the following forms of this function are equivalent:
> 
> logscale Syntax
>     
>     
>     concat(["value"])
> 
> and:
> 
> logscale Syntax
>     
>     
>     concat(field=["value"])
> 
> These examples show basic structure only.

For example: 

logscale
    
    
    concat([aidValue, cidValue], as=checkMe2)

The function is not capable of combining arbitrary strings, or concatenating strings and fields together. The following will _not_ work: 

logscale
    
    
    concat([field1,"/",field2], as=combined)

Instead, you can use the [`format()`](functions-format.html "format\(\)") function: 

logscale
    
    
    format("%s/%s",field=[field1,field2],as=combined)

### [`concat()`](functions-concat.html "concat\(\)") Examples

Click + next to an example below to get the full details.

#### Concatenate Fields and Strings Together

****

##### Query

logscale
    
    
    format("%s/%s",field=[dirname,filename],as=pathname)

##### Introduction

The [`concat()`](functions-concat.html "concat\(\)") is not able to concatenate fields and strings together. For example to create a pathname based on the directory and filename it is not possible to do: 

logscale
    
    
    concat([dirname,"/",filename],as=pathname)

This will raise an error. Instead, we can use [`format()`](functions-format.html "format\(\)"). 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         format("%s/%s",field=[dirname,filename],as=pathname)

Formats a value separating the two by a forward slash, creating the field pathname

  3. Event Result set.




##### Summary and Results

The [`format()`](functions-format.html "format\(\)") function provides a flexible method of formatting data, including encapsulating or combining strings and fields together. 

#### Concatenate Multiple Values From Nested Array Elements

**Concatenate multiple values from nested array elements using[`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    objectArray:eval("foo[]", var=x, function={_mapped := concat([x.key.value, "x.key.others[0]", "x.key.others[1]"])}, asArray="_mapped[]")

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used with the [`concat()`](functions-concat.html "concat\(\)") function to concatenate multiple deeply nested arrays of objects values in the array `foo[] ` and return the concatenated values in the output field _mapped[]

Example incoming data might look like this: 

JSON
    
    
    "foo[0].key.value": y
    "foo[0].key.others[0]": 1
    "foo[0].key.others[1]": 2
    "foo[1].nothing": 355

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("foo[]", var=x, function={_mapped := concat([x.key.value, "x.key.others[0]", "x.key.others[1]"])}, asArray="_mapped[]")

Notice that a [_`var`_](functions-objectarray-eval.html#query-functions-objectarray-eval-var) parameter can be used to give a different name to the input array variable inside the function argument. This is particularly useful whenever the input array name is very long. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate multiple deeply nested arrays of objects values. 

Sample output from the incoming example data: 
    
    
    _mapped[0]: y12
    "foo[0].key.value": y
    "foo[0].key.others[0]": 1
    "foo[0].key.others[1]": 2

#### Concatenate Values From Nested Array Elements

**Concatenate deeply nested objects and arrays using[`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function with [`concat()`](functions-concat.html "concat\(\)") **

##### Query

logscale
    
    
    objectArray:eval("in[]", asArray="out[]", function={out := concat(["in.a", "in.b.c", "in.others[1].d"])})

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used with the [`concat()`](functions-concat.html "concat\(\)") function to concatenate deeply nested arrays of objects values in the array `in[] ` and return the concatenated values in the output field out[]. 

Example incoming data might look like this: 

JSON
    
    
    in[0].a: 1
    in[0].b.c: 2
    in[0].others[0].d: 3
    in[0].others[1].d: 4

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("in[]", asArray="out[]", function={out := concat(["in.a", "in.b.c", "in.others[1].d"])})

Iterates over the array from start to end (or to the first empty index in the array), applies the given function, and returns the concatenated results in a new output array name field out[]. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate deeply nested arrays of objects. 

Sample output from the incoming example data: 
    
    
    out[0]: 124

#### Concatenate Values From Two Nested Array Elements

**Concatenate values from two nested array elements returning output in flat array**

##### Query

logscale
    
    
    objectArray:eval("arr[]", var=x, function={_mapped := concat([x.a, x.b])}, asArray="_mapped[]")

##### Introduction

In this example, the [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") function is used with the variable x to concatenate the values `a` and `b` from each array element. The [`concat()`](functions-concat.html "concat\(\)") function is used to return the concatenated output into a new array. 

Example incoming data might look like this: 

JSON
    
    
    arr[0]: machine
    arr[0].a: a0
    arr[0].b: b0
    arr[1].a: a1
    arr[1].b: b1
    arr[1].c: c1
    arr[2].a: a2
    arr[4].b: b2
    other: abc

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         objectArray:eval("arr[]", var=x, function={_mapped := concat([x.a, x.b])}, asArray="_mapped[]")

Concatenates the values `a` and `b` from each array element and returns the results in a new array named _mapped. In this example, [`objectArray:eval()`](functions-objectarray-eval.html "objectArray:eval\(\)") iterates over each element of the array and assigns each element to the variable `x` which is then used as an alias. The new field _mapped is created by concatenating the value using the alias `x` to extract each object value from each element of the array. Notice that the output in this example is a flat array. 

For example, this array element: 

arr[0].a: a0  
---  
arr[0].b: b0  
  
is translated to: 
         
         _mapped[0]: a0b0

  3. Event Result set.




##### Summary and Results

The query is used to concatenate values of two array elements. 

Sample output from the incoming example data, the original values have not been removed: 
    
    
    _mapped[0]: a0b0
    _mapped[1]: a1b1
    _mapped[2]: a2
    _mapped[3]: b2
    
    arr[0]: machine
    
    arr[0].a: a0
    arr[0].b: b0
    
    arr[1].a: a1
    arr[1].b: b1
    
    arr[1].c: c1
    
    arr[2].a: a2
    
    arr[4].b: b2
    
    other: abc

#### Concatenate Values in Two Fields - Example 1

**Concatenate values in two fields into a single value in a new array using the[`concat()`](functions-concat.html "concat\(\)") function **

##### Query

logscale
    
    
    concat([aidValue, cidValue], as=checkMe2)

##### Introduction

In this example, the [`concat()`](functions-concat.html "concat\(\)") function concatenates the AID (Agent ID) and CID (Customer ID) values into a single value in a new array. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         concat([aidValue, cidValue], as=checkMe2)

Concatenates the values of the fields aidValue and cidValue into a single value in a new field named checkMe2. 

The single value contains both the Agent ID and Customer ID information. It is recommended to have a consistent format and potentially include a separator between the AID and CID to ensure, that they can be easily parsed apart, if needed later. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate the values of a list of fields into a single value in a new field. Combining CID and AID values is, for example, useful for unique identification, troubleshooting, data analysis etc. This query is also useful in case you want to combine for example first names and last names from two different fields into the full name in a new field, or if you have a list of users and a list of the URLs visited, that you want to combine to see which user navigated which URLs. 

#### Concatenate Values in Two Fields - Example 2

**Concatenate values in two fields into a single value in a new array using the[`concat()`](functions-concat.html "concat\(\)") function **

##### Query

logscale
    
    
    concat([f1, f2], as="combined")

##### Introduction

In this example, the [`concat()`](functions-concat.html "concat\(\)") function concatenates the values of two fields with different names (f1 and f2) into a single value in a new field. 

##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         concat([f1, f2], as="combined")

Concatenates the values of the arrays f1 and f2 into a single value in a new array named combined. 

  3. Event Result set.




##### Summary and Results

The query is used to concatenate the values of a list of fields into a single value in a new field. This query is useful in case you want to combine for example first names and last names from two different fields into the full name in a new field, or if you have a list of users and a list of the URLs visited, that you want to combine to see which user navigated which URLs. 

#### Correlate Inbound Email URLs with Subsequent Access Attempts

**Correlate Inbound Email URLs with Subsequent Access Attempts to detect when a malicious URL in an email is subsequently accessed using the[`correlate()`](functions-correlate.html "correlate\(\)") function **

##### Query

logscale
    
    
    ((#repo="abnormal_security" AND #event.module="email-security") OR (#repo="corelight" AND #event.module="ids"))
    | case{
        #Vendor="corelight" 
        | url.prefix := "http://" 
        | url.original := concat([url.prefix,"/",client.address,"/",url.path]); *
    }
    | correlate(
        emailInbound:{#event.module="email-security"},
        emailAccess:{#event.module="ids" 
        | url.original <=> emailInbound.url.original},
        sequence=true,within=1h)

##### Introduction

In this example, the [`correlate()`](functions-correlate.html "correlate\(\)") is used to match URLs from inbound emails with subsequent HTTP requests to those URLs within a one-hour window, indicating when recipients click on email link. 

The [`correlate()`](functions-correlate.html "correlate\(\)") matches URLs received in emails with subsequent access attempts detected in network traffic, helping identify potential phishing or malicious link interactions. 

Example incoming data might look like this: 

@timestamp| #repo| #event.module| #Vendor| client.address| url.path| url.original| email.from.address| email.to.address  
---|---|---|---|---|---|---|---|---  
2023-06-15T10:00:00Z| abnormal_security| email-security| abnormal| <no value>| <no value>| http://malicious.com/path1| sender@external.com| user1@company.com  
2023-06-15T10:15:30Z| corelight| ids| corelight| 10.0.1.100| path1| <no value>| <no value>| <no value>  
2023-06-15T11:00:00Z| abnormal_security| email-security| abnormal| <no value>| <no value>| http://suspicious.net/offer| phish@bad.com| user2@company.com  
2023-06-15T11:05:45Z| corelight| ids| corelight| 10.0.2.200| offer| <no value>| <no value>| <no value>  
2023-06-15T12:30:00Z| abnormal_security| email-security| abnormal| <no value>| <no value>| http://legitimate.org/docs| partner@vendor.com| user3@company.com  
2023-06-15T12:45:15Z| corelight| ids| corelight| 10.0.3.150| docs| <no value>| <no value>| <no value>  
  
##### Step-by-Step

  1. Starting with the source repository events.

  2. logscale
         
         ((#repo="abnormal_security" AND #event.module="email-security") OR (#repo="corelight" AND #event.module="ids"))

Filters for events that are either `email-security` events from the abnormal_security repository OR `ids` (Intrusion Detection System) events from the corelight repository. 

This filter ensures that only relevant events from these two specific security tools are processed for the subsequent correlation analysis. 
  3. logscale
         
         | case{
             #Vendor="corelight" 
             | url.prefix := "http://" 
             | url.original := concat([url.prefix,"/",client.address,"/",url.path]); *
         }

The case statement processes events from the `corelight` vendor (`#Vendor="corelight"`) only to standardize their URL format. 

For these events, it first creates a new field named url.prefix containing the value `http://`. Then, using the [`concat()`](functions-concat.html "concat\(\)") function, it constructs a complete URL string in a new field named url.original. 

This URL is built by combining the HTTP prefix, followed by a forward slash, then the client's IP address from the client.address field, another forward slash, and finally the URL path from the url.path field. 

The wildcard (*) at the end ensures all other original fields in the events are preserved. 

For example, if an event has client.address=`10.0.1.100` and url.path=`download/file.exe`, the resulting url.original field would contain `http://10.0.1.100/download/file.exe`. This standardization allows for proper correlation with URLs found in email security events. 

  4. logscale
         
         | correlate(
             emailInbound:{#event.module="email-security"},

Defines the first query named emailInbound to match email security events. Filters for events with #event.module=`email-security` which captures all inbound emails containing URLs. All fields from matching events are preserved since no field restrictions are specified. 

This query forms the base pattern for correlation, and its fields (particularly url.original) will be referenced by the second query using the prefix notation (emailInbound.url.original). 

These events represent the initial detection of URLs in incoming emails, which is crucial for tracking potential phishing attempts or malicious links. 

  5. logscale
         
         emailAccess:{#event.module="ids" 
             | url.original <=> emailInbound.url.original},

Defines the second query named emailAccess to match URL access attempts. Filters for events with #event.module=`ids` which captures network traffic events. 

The correlation relationship (condition) is specified using the ``<=>`` operator which requires exact matches between fields (field correlation matches). 

The url.original field from this emailAccess event must match the url.original field from the emailInbound event. This ensures that events will only be correlated when they show access to exactly the same URL that was received in an email, helping identify when recipients click on email links. 

  6. logscale
         
         sequence=true,within=1h)

Sets the correlation parameters: 

     * [_`sequence`_](functions-correlate.html#query-functions-correlate-sequence)=`true` ensures that emailInbound events must occur before emailAccess events, preventing matching of access events that occurred before the email was received.Email receipt must occur before URL access 

     * [_`within`_](functions-correlate.html#query-functions-correlate-within)=`1h` specifies a one-hour maximum time window between email receipt and URL access, focusing on immediate user interactions with email links. Access attempts more than an hour after email receipt are excluded. 

  7. Event Result set.




##### Summary and Results

The query is used to identify when users click on URLs received in emails by correlating email security events with network traffic events. The [`correlate()`](functions-correlate.html "correlate\(\)") matches URLs received in emails with subsequent access attempts detected in network traffic, helping identify potential phishing or malicious link interactions. 

This query is useful, for example, to detect potential security incidents where users interact with phishing emails, track the effectiveness of security awareness training, or monitor for suspicious URL access patterns. 

Sample output from the incoming example data: 

@timestamp| emailInbound.email.from.address| emailInbound.email.to.address| emailInbound.url.original| emailAccess.@timestamp| emailAccess.client.address| TimeBetweenEvents  
---|---|---|---|---|---|---  
2023-06-15T10:00:00Z| sender@external.com| user1@company.com| http://malicious.com/path1| 2023-06-15T10:15:30Z| 10.0.1.100| 930  
2023-06-15T11:00:00Z| phish@bad.com| user2@company.com| http://suspicious.net/offer| 2023-06-15T11:05:45Z| 10.0.2.200| 345  
2023-06-15T12:30:00Z| partner@vendor.com| user3@company.com| http://legitimate.org/docs| 2023-06-15T12:45:15Z| 10.0.3.150| 915
