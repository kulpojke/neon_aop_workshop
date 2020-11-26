install.packages("devtools")
install.packages("neonUtilities")
devtools::install_github("NEONScience/NEON-geolocation/geoNEON")

library(neonUtilities)
library(geoNEON)
#library(glue)

options(stringsAsFactors=F) ##This is redundant for R versions 4.0.0+

sites <- c('BART',
           'HARV',
           'BLAN',
           'SCBI',
           'SERC',
           'DSNY',
           'JERC',
           'OSBS',
           'GUAN',
           'LAJA',
           'STEI',
           'TREE',
           'UNDE',
           'KONA',
           'KONZ',
           'UKFS',
           'GRSM',
           'MLBS',
           'ORNL',
           'DELA',
           'LENO',
           'TALL',
           'DCFS',
           'NOGP',
           'WOOD',
           'CPER',
           'RMNP',
           'STER',
           'CLBJ',
           'OAES',
           'YELL',
           'MOAB',
           'NIWO',
           'JORN',
           'SRER',
           'ONAQ',
           'ABBY',
           'WREF',
           'SJER',
           'SOAP',
           'TEAK',
           'BARR',
           'TOOL',
           'BONA',
           'DEJU',
           'HEAL',
           'PUUM')
notfirst <- FALSE

go <- function(notfirst, sites){
  veg_str <- loadByProduct(dpID="DP1.10098.001", site=site, package="expanded", check.size=F)
  list2env(veg_str, .GlobalEnv)
  ## Use geoNEON to retrieve precise easting and northing for each tree
  vegmap <- geoNEON::getLocTOS(vst_mappingandtagging, "vst_mappingandtagging")
  # Merge tables to join tree-specific data with the geospatial data
  veg <- merge(vst_apparentindividual, vegmap, by=c("individualID","namedLocation","domainID","siteID","plotID"))
  write.table(veg, "exact_locations_within_plots.csv", append=notfirst, sep=",", col.names=!notfirst, row.names=FALSE, quote=FALSE)
  print(notfirst)
  notfirst <- TRUE
  return(notfirst)
}

for (site in sites) {
  notfirst <- go(notfirst, sites)
}
