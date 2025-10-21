# Math Query Functions | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## Math Query Functions

LogScale's math query functions provide a range of arithmetical and numerical functions. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

**Table: Math Query Functions**

Function| Default Argument| Availability| Description  
---|---|---|---  
[`math:abs([as], field)`](functions-math-abs.html "math:abs\(\)")| [_`field`_](functions-math-abs.html#query-functions-math-abs-field)|  |  Calculates the absolute value of a field; the result is always a positive number or 0.   
[`math:arccos([as], field)`](functions-math-arccos.html "math:arccos\(\)")| [_`field`_](functions-math-arccos.html#query-functions-math-arccos-field)|  |  Calculates the arc cosine of a field.   
[`math:arcsin([as], field)`](functions-math-arcsin.html "math:arcsin\(\)")| [_`field`_](functions-math-arcsin.html#query-functions-math-arcsin-field)|  |  Calculates the arc sine of a field.   
[`math:arctan([as], field)`](functions-math-arctan.html "math:arctan\(\)")| [_`field`_](functions-math-arctan.html#query-functions-math-arctan-field)|  |  Calculates the arc tangent of a value.   
[`math:arctan2([as], x, y)`](functions-math-arctan2.html "math:arctan2\(\)")|  |  |  Calculates the arc tangent of a value.   
[`math:ceil([as], field)`](functions-math-ceil.html "math:ceil\(\)")| [_`field`_](functions-math-ceil.html#query-functions-math-ceil-field)|  |  Rounds field value to smallest integer that's larger than or equal to it.   
[`math:cos([as], field)`](functions-math-cos.html "math:cos\(\)")| [_`field`_](functions-math-cos.html#query-functions-math-cos-field)|  |  Calculates the cosine of a field.   
[`math:cosh([as], field)`](functions-math-cosh.html "math:cosh\(\)")|  |  |  Computes the hyperbolic cosine of a double field.   
[`math:deg2rad([as], field)`](functions-math-deg2rad.html "math:deg2rad\(\)")| [_`field`_](functions-math-deg2rad.html#query-functions-math-deg2rad-field)|  |  Converts angles from degrees to radians.   
[`math:exp([as], field)`](functions-math-exp.html "math:exp\(\)")| [_`field`_](functions-math-exp.html#query-functions-math-exp-field)|  |  Calculates Euler's number e raised to the power of a double value in a field.   
[`math:expm1([as], field)`](functions-math-expm1.html "math:expm1\(\)")| [_`field`_](functions-math-expm1.html#query-functions-math-expm1-field)|  |  Calculates the exponential value of a number minus 1.   
[`math:floor([as], field)`](functions-math-floor.html "math:floor\(\)")| [_`field`_](functions-math-floor.html#query-functions-math-floor-field)|  |  Computes the largest integer value not greater than the field value given.   
[`math:log([as], field)`](functions-math-log.html "math:log\(\)")| [_`field`_](functions-math-log.html#query-functions-math-log-field)|  |  Calculates the natural logarithm (base e) of the value in a double field.   
[`math:log10([as], field)`](functions-math-log10.html "math:log10\(\)")| [_`field`_](functions-math-log10.html#query-functions-math-log10-field)|  |  Calculates the base 10 logarithm of a double field.   
[`math:log1p([as], field)`](functions-math-log1p.html "math:log1p\(\)")| [_`field`_](functions-math-log1p.html#query-functions-math-log1p-field)|  |  Calculates the natural logarithm of the sum of field's value and 1\.   
[`math:log2([as], field)`](functions-math-log2.html "math:log2\(\)")| [_`field`_](functions-math-log2.html#query-functions-math-log2-field)|  |  Calculates the base 2 logarithm of a double field.   
[`math:mod([as], divisor, field)`](functions-math-mod.html "math:mod\(\)")| [_`field`_](functions-math-mod.html#query-functions-math-mod-field)|  |  Calculates the floor modulus of field value and the divisor.   
[`math:pow([as], exponent, field)`](functions-math-pow.html "math:pow\(\)")| [_`field`_](functions-math-pow.html#query-functions-math-pow-field)|  |  Calculates the field value to the exponent power.   
[`math:rad2deg([as], field)`](functions-math-rad2deg.html "math:rad2deg\(\)")| [_`field`_](functions-math-rad2deg.html#query-functions-math-rad2deg-field)|  |  Converts angles from radians to degrees.   
[`math:sin([as], field)`](functions-math-sin.html "math:sin\(\)")| [_`field`_](functions-math-sin.html#query-functions-math-sin-field)|  |  Calculates the sine of a field.   
[`math:sinh([as], field)`](functions-math-sinh.html "math:sinh\(\)")| [_`field`_](functions-math-sinh.html#query-functions-math-sinh-field)|  |  Calculates the hyperbolic sine of a double field.   
[`math:spherical2cartesian([as], azimuth, polar, radius)`](functions-math-spherical2cartesian.html "math:spherical2cartesian\(\)")|  |  |  Calculates the average for a field of a set of events.   
[`math:sqrt([as], field)`](functions-math-sqrt.html "math:sqrt\(\)")| [_`field`_](functions-math-sqrt.html#query-functions-math-sqrt-field)|  |  Calculates the rounded positive square root of a double field.   
[`math:tan([as], field)`](functions-math-tan.html "math:tan\(\)")| [_`field`_](functions-math-tan.html#query-functions-math-tan-field)|  |  Calculates the trigonometric tangent of an angle in a field.   
[`math:tanh([as], field)`](functions-math-tanh.html "math:tanh\(\)")| [_`field`_](functions-math-tanh.html#query-functions-math-tanh-field)|  |  Calculates the hyperbolic tangent of a field.   
[`parseHexString([as], [charset], field)`](functions-parsehexstring.html "parseHexString\(\)")| [_`field`_](functions-parsehexstring.html#query-functions-parsehexstring-field)|  |  Parses input from hex encoded bytes, decoding resulting bytes as a string.   
[`parseInt([as], [endian], field, [radix])`](functions-parseint.html "parseInt\(\)")| [_`field`_](functions-parseint.html#query-functions-parseint-field)|  |  Converts an integer from any radix or base to base-ten, decimal radix.   
[`round([as], field, [how])`](functions-round.html "round\(\)")| [_`field`_](functions-round.html#query-functions-round-field)|  |  Rounds an input field up or down, depending on which is nearest.   
[`unit:convert([as], [binary], field, [from], [keepUnit], [to], [unit])`](functions-unit-convert.html "unit:convert\(\)")| [_`field`_](functions-unit-convert.html#query-functions-unit-convert-field)|  |  Converts values between different units.
