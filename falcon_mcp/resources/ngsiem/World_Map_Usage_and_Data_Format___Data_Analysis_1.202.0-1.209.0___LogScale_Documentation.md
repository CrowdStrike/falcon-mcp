# World Map Usage and Data Format | Data Analysis 1.202.0-1.209.0 | LogScale Documentation

**URL:** https://library.humio.com/data-analysis/widgets-worldmap-usage-data.html
**Subdomain:** library
**Description:** 

---

[Falcon LogScale Documentation](https://library.humio.com)

/ [Data Analysis 1.202.0-1.209.0](data-analysis-docs.html)

/ [Data Visualization](data-visualization.html)

/ [Widgets](widgets.html)

/ [World Map](widgets-worldmap.html)

### World Map Usage and Data Format

The following table lists the primary fields used in the [`World Map`](widgets-worldmap.html "World Map") widget. 

Field |  Type |  Description   
---|---|---  
lat |  number |  A field containing the latitude to use for geohash bucketing.   
lon |  number |  A field containing the longitude to use for geohash bucketing.   
geohash |  string |  OPTIONAL. A base32 [geohash](https://en.wikipedia.org/wiki/Geohash) string to calculate latitude and longitude.   
precision |  number |  The precision to use in the calculation of the embedded geohash. Usually 4 is fine for a full globe, 12 is for a small area of zoom.   
magnitude |  aggregate |  A function used to calculate the magnitude (weight) of each bucket. This value is used to determine the size or opacity of the world map markers.   
  
If both geohash and lat and lon are specified, geohash is ignored. 

The [`World Map`](widgets-worldmap.html "World Map") widget: 

  * Requires specific input format for geographical data as shown in the table 

  * Utilizes the [`worldMap()`](functions-worldmap.html "worldMap\(\)") function to properly format and bucket locations using geohashing 

  * Can accept any input that matches the required format shown in the table, though geohashing is recommended for optimal visualization.
