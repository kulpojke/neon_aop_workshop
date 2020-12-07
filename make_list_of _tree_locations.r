install.packages("devtools")
install.packages("neonUtilities")
  
library(devtools)
devtools::install_github("NEONScience/NEON-geolocation/geoNEON")
  
library(neonUtilities)
library(geoNEON)
library(dplyr)
#library(glue)

options(stringsAsFactors=F) ##This is redundant for R versions 4.0.0+

sites <-  c('BART',
            'HARV',
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
            'CLBJ',
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
            'BONA',
            'DEJU',
            'HEAL',
            'PUUM')


go <- function(notfirst, sites){
  veg_str <- loadByProduct(dpID="DP1.10098.001", site=site, package="expanded", check.size=F)
  list2env(veg_str, .GlobalEnv)
  ## Use geoNEON to retrieve precise easting and northing for each tree
  vegmap <- geoNEON::getLocTOS(vst_mappingandtagging, "vst_mappingandtagging")
  # rename columns
  vst_apparentindividual <- vst_apparentindividual %>%
    rename(
      app_indiv_dataQF = dataQF,
      app_indiv_date = date,
      app_indiv_eventID = eventID,
      app_indiv_remarks = remarks,
      app_indiv_subplotID = subplotID,
      app_indiv_uid = uid
    )
  
  vst_mappingandtagging <- vst_mappingandtagging %>%
    rename(
      map_tag_dataQF = dataQF,
      map_tag_date = date,
      emap_tag_eventID = eventID,
      map_tag_remarks = remarks,
      map_tag_subplotID = subplotID,
      map_tag_uid = uid
    )
  
  # Merge tables to join tree-specific data with the geospatial data
  veg <- merge(vst_apparentindividual, vegmap, by=c("individualID","namedLocation","domainID","siteID","plotID"))
  write.table(veg, "exact_locations_within_plots.csv", append=notfirst, sep=",", col.names=!notfirst, row.names=FALSE, quote=FALSE)
  notfirst <- TRUE
  return(notfirst)
}

# exception handling in R is completely insane!   
notfirst <- FALSE
for (site in sites) {
  result = tryCatch({
    notfirst <- go(notfirst, sites) 
  }, 
  error = function(e){
  })
}
