install.packages("devtools")
install.packages("neonUtilities")
devtools::install_github("NEONScience/NEON-geolocation/geoNEON")

library(neonUtilities)
library(geoNEON)
#library(glue)

options(stringsAsFactors=F) ##This is redundant for R versions 4.0.0+

sites <- c("WREF", "TEAK")
notfirst <- FALSE
for (site in sites) {

  veg_str <- loadByProduct(dpID="DP1.10098.001", site=site, 
                         package="expanded", check.size=F)

  list2env(veg_str, .GlobalEnv)

  ## Use geoNEON to retrieve precise easting and northing for each tree
  names(vst_mappingandtagging) #this object was created using list2env() above
  vegmap <- geoNEON::getLocTOS(vst_mappingandtagging, "vst_mappingandtagging")
  names(vegmap)


  # Merge tables to join tree-specific data with the geospatial data
  veg <- merge(vst_apparentindividual, vegmap, by=c("individualID","namedLocation",
                                                  "domainID","siteID","plotID"))

  write.table(veg, "exact_locations_within_plots.csv", append=notfirst, sep=",", col.names=!notfirst, row.names=FALSE, quote=FALSE)

  notfirst <- TRUE
  # plot
  #symbols(veg$adjEasting[which(veg$plotID=="WREF_085")], 
  #        veg$adjNorthing[which(veg$plotID=="WREF_085")], 
  #        circles=veg$stemDiameter[which(veg$plotID=="WREF_085")]/100/2, #Divide by 100 to reduce cm displayed in m, and divide by 2 to reduce diameter to radius
  #        xlab="Easting", ylab="Northing", inches=F)

}
