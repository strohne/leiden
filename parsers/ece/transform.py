#%%
#
# Transform EpiCentres data
#

from pathlib import Path

PROJECT_ROOT = (
    Path(__file__).resolve().parents[2]
    if "__file__" in globals()
    else Path.cwd()
)
ECE_ROOT = PROJECT_ROOT / "parsers" / "ece"

import pandas as pd

import importlib
import parsers.ece.eceTransformer as eceModule
eceModule = importlib.reload(eceModule)

from parsers.ece.eceTransformer import EceTransformer

#%% Load data

filename = "ece_gardell-1937-latin.xlsx"
inputfile = PROJECT_ROOT / "data" / "input" / filename
df = pd.read_excel(inputfile)

#%% Prepare IDs

df["corpus"] = filename
df["id"] = (
    df["corpus"].astype(str).str.strip() + "_" +
    df["case"].astype(str).str.lower().str.strip()
)

df["id"] = (
    df["id"]
    .str.replace(" ", "_")
    .str.replace("-", "_")
    .str.strip()
)

cols = ["corpus", "case", "id"]
df = df[cols + [c for c in df.columns if c not in cols]]


#%% Instantiate transformer and preprocess text

ece = EceTransformer(str(ECE_ROOT) + "/")
df = ece.preprocess(df, 'transcription')
df = ece.preprocess(df, 'expanded')

#%% Build parser and prepare test files

ece.recompile()
ece.testchunks(df, 'transcription', 'id', chunksize=1000)
ece.testchunks(df, 'expanded', 'id', chunksize=1000)

#%% Parse and transform to XML

df = ece.parseDataframe(df, 'transcription')
df = ece.parseDataframe(df, 'expanded')

#%% Unmatched brackets

df["trancription_matched_brackets"] = (
    df["transcription"].str.count(r"\[") == df["transcription"].str.count(r"\]")
)

df["expanded_matched_brackets"] = (
    df["expanded"].str.count(r"\[") == df["expanded"].str.count(r"\]")
)

#%% How many are well-formed?

print(df[["transcription_status", "trancription_matched_brackets"]].value_counts())

print(df[["expanded_status", "expanded_matched_brackets"]].value_counts())

#%% Save results

outputname = Path(filename).stem
df.to_csv(PROJECT_ROOT / "data" / "output" / f"{outputname}.csv", index=False)
df.to_excel(PROJECT_ROOT / "data" / "output" / f"{outputname}.xlsx", index=False)
