#
# Get data from the database and save it as a csv file
#

# See https://github.com/datavana/rpigraf
library(rpigraf)
library(tidyverse)

db_setup(host = "127.0.0.3", 3306, "root", "root")
items <- db_fetch("items", list("itemtype"="dio-inscriptions-raw"), "epi_public")

items %>%
  select(id, content, type, norm_iri, ) %>%
  write_csv("data/input/dio_public_raw.csv")