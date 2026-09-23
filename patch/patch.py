#
# Patch items parsed with DHParser
#

from pathlib import Path

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
    if "__file__" in globals()
    else Path.cwd()
)

import pandas as pd
from datetime import datetime

import settings
# Run `pip install "git+https://github.com/datavana/epygraf.git#egg=epygraf"`
# epygraf is imported via settings

#%% Load parsed items

# Set filename to parsed CSV in `data/output/`
filename = "dio_public_raw.csv"
df = pd.read_csv( PROJECT_ROOT / "data" / "output" / filename, delimiter =';')

#%% Prepare data for patch

# Keep successful parsing
# TODO: Read parsing quality, decide what will be patched
df = df[df['ok'] == True]

# Update item type
df['type'] = 'dio-inscriptions'

# Add parsed-prefix to norm_iri and replace id with iri path
df['id'] = 'items/' + 'dio-inscriptions/' + df['norm_iri'] + '-parsed'

# Add prefixes to articles_id and sections_id
df['articles_id'] = 'articles-' + df['articles_id'].astype(str)
df['sections_id'] = df['sections_id'].astype('Int64')
df['sections_id'] = 'sections-' + df['sections_id'].astype(str)

# Update content with parsed data
df['content'] = df['parsed']

# Only keep columns required for patch
patch = df[['articles_id', 'sections_id', 'id', 'content']].dropna()

#%% Save patch

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
patch.to_csv(PROJECT_ROOT / "data" / "patch" / f"{timestamp}_patch.csv", index=False, sep=";")

#%% !Directly patch parsed items

# database = "epi_public"
# epi.api.patch(patch, database = f"{database}")