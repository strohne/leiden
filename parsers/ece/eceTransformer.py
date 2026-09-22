"""eceTransformer.py

A class to transform data frames with the ECE parser.
"""

from __future__ import annotations

import os
from typing import Any, Iterable, List, Tuple, Union

import re
import numpy as np
import pandas as pd
from DHParser import Error
from pandas.core.interchange.dataframe_protocol import DataFrame

import parsers.ece.eceParser as eceParser
from tqdm import tqdm

class EceTransformer:
    """
    eceTransformer
    """

    def __init__(self, basefolder) -> None:
        """
        Create a new ``exeTransformer`` instance.

        Parameters
        ----------
        basefolder : str
            The base folder where the grammar file and the parser class are located.
        """

        self.parser = eceParser

        self.basefolder = basefolder

        self.folder_test = basefolder + "tests/"
        self.file_grammar = basefolder + "ece.ebnf"
        self.file_preprocess = basefolder + "preprocess.csv"


        self.root_tag = "lines"

        self.string_tags = [
            "letters",
            "terminator",
            "inspace",
            "binder"
        ]

        self.inline_tags = [
            "part","lines",
            "pc", "lb", "gap", "unc",
            "sup", "sub", "nl", "com",
            "am",
            "dec", "ex", "gap", "res",  "cpl", "era", "add", "lig", "bar", "subbar", "space"
        ]

    def recompile(self) -> bool:
        """
        Recompile the ECE grammar and regenerate the parser class.

        :return: True if recompilation succeeded, False otherwise.
        """
        return self.parser.recompile_grammar(self.file_grammar, force=True)

    def testchunks(self, df, colname, casecol = 'case', chunksize = 150):
        """
        Generate test files for the grammar development.

        Parameters
        ----------
        df : pd.DataFrame
            The DataFrame containing the data to be chunked.
        colname : str
            The name of the column in *df* that contains the text snippets to be included in
            the test files.
        casecol : str, default 'case'
            The name of the column in *df* that contains the case identifiers to be included in
            the test files.
        chunksize : int, default 150
            The number of rows to include in each test file.

        """

        os.makedirs(self.folder_test, exist_ok=True)
        for chunkidx, chunkstart in enumerate(range(0, len(df), chunksize)):
            chunk = df.iloc[chunkstart:chunkstart + chunksize]
            tests = ""
            for idx, row in chunk.iterrows():
                snippet = str(row[colname]).strip()
                case = str(row[casecol])
                tests += f"\n{case}: "
                tests += '"""' + snippet + '"""'

            with open(self.folder_test + f"chunk_{colname}_{chunkidx + 1:03d}.ini", "w", encoding="utf-8") as file:
                file.write("[match:" + self.root_tag + "]\n" + tests)

    def preprocess(self, df: pd.DataFrame, colname: str = "content") -> DataFrame:
        """
        Preprocess the *colname* column of *df* by applying regex replacements from the *preprocess.csv* file.

        :param df:
        :param colname:
        :return: The preprocessed DataFrame with the same columns as *df* but with the *colname* column modified.
        """
        regs = pd.read_csv(self.file_preprocess, delimiter=';', keep_default_na=False)
        for idx, row in regs.iterrows():
            df[colname] = df[colname].str.replace(row['search'], row['replace'], regex=True)

        return df

    def parseSnippet(
            self,
            source: str,
            string_tags: List[str],
            inline_tags: List[str],
            indent: int = 2,
    ) -> Tuple[str | None, List[Error | str]]:

        """
        Parse a single snippet.

        Returns
        -------
        xml : str | None
            The XML representation if parsing succeeded, otherwise None.
        err : str | None
            The error message if something went wrong, otherwise None.
        """
        try:
            result, errors = self.parser.compile_snippet(source)

            xml = result.as_xml(
                string_tags=string_tags,
                inline_tags=inline_tags,
                indentation=indent,
            )
            # Collapse whitespace
            xml = re.sub(r"[\r\n ]+", " ", xml)

            return xml, errors
        except Exception as exc:
            return None, [str(exc)]

    def parseDataframe(
            self,
            df: pd.DataFrame,
            content_col: str = "content",
            parsed_col: str = None,
            error_col: str = None,
            status_col: str = None
    ) -> pd.DataFrame:
        """
        Parse the ``content`` column of *df* with *parser* while skipping NaN /
        empty strings.

        Parameters
        ----------
        df : pd.DataFrame
            Input data.
        content_col : str, default ``"content"``
            Name of the column that holds the raw snippet.
        parsed_col : str, defaults to the content column suffixed with `_parsed`.
            Column that will receive the XML output.
        error_col : str,.defaults to the content column suffixed with `_error`.
            Column that will receive any exception message.
        status_col : str, defaults to the content column suffixed with `_status`.
            Column that will receive the status of the parsing (e.g., "ok", "error", "empty").

        Returns
        -------
        pd.DataFrame
            The same DataFrame with new columns for parsing results, errors and status.
        """

        parsed_vals: List[Any] = [None] * len(df)   # pre‑size for speed
        error_vals: List[Any] = [None] * len(df)

        for i, row in enumerate(tqdm(df.itertuples(index=False), total=len(df), desc="Parsing")):

            raw = getattr(row, content_col)
            if pd.isna(raw):
                continue
            raw_str = str(raw).strip()
            if not raw_str:
                continue

            xml, err = self.parseSnippet(
                source=raw_str,
                string_tags=self.string_tags,
                inline_tags=self.inline_tags,
                indent=2
            )
            parsed_vals[i] = xml
            error_vals[i] = err

        df = df.copy()

        if parsed_col is None:
            parsed_col = content_col + "_parsed"
        if error_col is None:
            error_col = content_col + "_errors"
        if status_col is None:
            status_col = content_col + "_status"


        df[parsed_col] = parsed_vals
        df[error_col] = error_vals

        ok = df[parsed_col].str.startswith(f"<{self.root_tag}>").fillna(False)

        df[status_col] = np.select(
            [
                df[content_col].isna(),
                ~df[content_col].isna() & ok
            ],
            [
                "empty",
                "ok"
            ],
            default="error"
        )

        # Strip root tag
        taglen = len(self.root_tag)
        df.loc[ok, parsed_col] = (
            df.loc[ok, parsed_col]
            .str.slice(taglen + 2, - (taglen + 3))
            .str.strip()
        )

        return df
