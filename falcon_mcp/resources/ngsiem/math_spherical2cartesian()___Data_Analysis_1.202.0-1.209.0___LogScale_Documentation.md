# math:spherical2cartesian() | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/functions-math-spherical2cartesian.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Query Functions](functions.html)

## [`math:spherical2cartesian()`](functions-math-spherical2cartesian.html "math:spherical2cartesian\(\)")

This query function converts given spherical coordinates to cartesian coordinates. The coordinate system uses z as the up-axis and measures the azimuthal angle from the x-axis. 

### Note

This query function is not yet available, but expected to be released in a future version of LogScale. 

### Note

Math functions on ARM architecture may return different results in very high-precision calculationsc compared to Intel/AMD architectures.

Parameter| Type| Required| Default Value| Description  
---|---|---|---|---  
[ _`as`_](functions-math-spherical2cartesian.html#query-functions-math-spherical2cartesian-as)|  string| optional[a] | `_spherical2cartesian`|  Output prefix of fields to set with suffixes `.x`, `.y` and `.z` (for example, `as.x`, `as.y`, `as.z`).   
[_`azimuth`_](functions-math-spherical2cartesian.html#query-functions-math-spherical2cartesian-azimuth)|  string| required |  |  Azimuthal angle measured from the x-axis.   
[_`polar`_](functions-math-spherical2cartesian.html#query-functions-math-spherical2cartesian-polar)|  number| required |  |  Polar angle measured from the xy-plane.   
[_`radius`_](functions-math-spherical2cartesian.html#query-functions-math-spherical2cartesian-radius)|  string| required | `1.0`|  Radius of the sphere.   
[a] Optional parameters use their default value unless explicitly set.  
  
The [`math:spherical2cartesian()`](functions-math-spherical2cartesian.html "math:spherical2cartesian\(\)") query function requires three parameters: the azimuth, the polar, and the radius. If no radius is specified, a radius of 1.0 is used. 

If the polar angle is set to 90 degrees, the returned coordinates will be (0.0, 0.0, 1.0). If both polar and azimuthal angles are set to 0, the returned coordinates will be (1.0, 0.0, 0.0). 

### [`math:spherical2cartesian()`](functions-math-spherical2cartesian.html "math:spherical2cartesian\(\)") Syntax Examples

For geographical coordinates, the azimuth corresponds to longitude and the polar angle to latitude. To convert from geographical coordinates to the cartesian coordinates of the point on the unit-sphere, you would enter a query into LogScale like the one below: 

logscale
    
    
    lat := 90.0
    | lon := 0.0
    | math:spherical2cartesian(azimuth=lon, polar=lat, radius = 1.0, as=p)

The results will be in the fields p.x, p.y and p.z.
