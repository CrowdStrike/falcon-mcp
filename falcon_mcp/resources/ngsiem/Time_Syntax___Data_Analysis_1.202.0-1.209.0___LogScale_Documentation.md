# Time Syntax | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/syntax-time.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Language Syntax](syntax.html)

## Time Syntax

The time syntax defines how you can convert or translate timestamps and other time related values to alternative formats. A relative time syntax is available for specifying and calculating times in relation to other times. See [Relative Time Syntax](syntax-time-relative.html "Relative Time Syntax"). 

### Rate Unit Conversion

When displaying a rate (value per unit of time) in a [`Time Chart`](widgets-timechart.html "Time Chart"), the display is sensitive to the size of the chart's `span` or `bucket` parameter, if the thing being graphed is a [`sum()`](functions-sum.html "sum\(\)") or [`count()`](functions-count.html "count\(\)") of log data. 

You can use `timeChart(function=sum(bytes),span=1h)` to show an hourly rate. But sometimes you want a rate (for example `Kibytes/sec`) for which it does not make sense to create a bucket for each. Previously, we have suggested to use a successive [`eval()`](functions-eval.html "eval\(\)") to reduce the chart inputs, but that is rather cumbersome and also sensitive to the size of the buckets (the span of each bar in the chart). Unit conversions can resolve this. 

#### Source-Unit is a Sum or Count

You can convert using a syntax like `timeChart(function=sum(bytes), unit="bytes/span to Mi bytes/day")`. This will make it so that the conversion takes the timespan into account. If you use the above with `span=1d` there will be no conversion, but if you do it with `span=1h`, then the plotted values will be multiplied by 24 (because there are 24 hours in a day). You can use `/span` or `/bucket` interchangeably. 

#### Source-Unit is Already a Rate

You can convert using a syntax like `timeChart(..., unit="bytes/sec to Mibytes/day")`. In this case, the source is already a rate (measured in units per time). With this, the conversion is applied independently of the length of the span (bucket size) for the graph. 

#### Expressing Rates and Units

Units in this system is either a base unit (like events or bytes) or a rate, like a base unit per time unit. The syntax for a base unit is this 

logscale Syntax
    
    
    base_unit    ::= Number_opt SIunit_opt unitname_opt
    Number_opt   ::= ([0-9]+)?
    SIunit_opt   ::= ([KMGP]i?
    | )
    unitname_opt ::= (' '? <string>)?

Tip

Units can be expressed as SI units or binary units. An example of a base unit is `2Gi bytes`. We use the standard SI-units K, M, G, and P to denote 1000-based kilo, mega, giga and peta; whereas Ki, Mi, Gi, and Pi designate the binary multiple 1024n style. See the National Institute of Standards and Technology's [Reference on Prefixes for Binary Multiples](http://physics.nist.gov/cuu/Units/binary.html) for a detailed explanation. 

The `unitname_opt` can, optionally, be separated from the SI unit with a single space to be able to differentiate names unit names starting with an `i`. 

Time units follow the same pattern, as you see here: 

logscale Syntax
    
    
    time_unit    ::= Number_opt Time
    Number_opt   ::= ([0-9]+)?
    Time         ::= prefix-of( "seconds, "milliseconds", "minutes", "hours" "days" )
    | "ms"
    | "bucket"
    | "span"

The non-unique prefixes `m` and `mi` are interpreted as minutes. Whereas, `ms` designates milliseconds. A rate is like so: 

logscale Syntax
    
    
    Rate :=   base_unit "/" time_unit

Since the entirety of base-unit is optional — a missing base unit is implied to be one — you can convert from events/second to events/hour with a minimal expression such as this: 

logscale Syntax
    
    
    unit="/s to /h"

The `to` side of such a conversion must be a rate, whereas the left side can be a basic unit, which is interpreted as `unit/bucket`.
