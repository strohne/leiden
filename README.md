# DIO inscription parser

Parsers for Leidener Klammersystem transcriptions.

One parser is tailored for the project Die Deutschen Inschriften.
Another parser is made for the EpiCentres project.

## Getting started

- Clone the repo
- Install dependencies:
  ```
  python -m pip install -r requirements.txt
  ```
- Install the local package and the Jupyter kernel:
  ```
  python -m pip install -e .
  python -m pip install ipykernel
  ```
- If you have access to an Epigraf database, use `data/input/getdata.R` to get inscription data.
- Run `parsers/dio/transform.py` in interactive mode
  

To generate parsers:
```
cd parsers/dio
dhparser dio.ebnf
```

To run tests:
```
cd parsers/dio
python tests.py tests/03_test_dio_sco_passau.ini
```

To patch successfully parsed data, see `patch/readme.md`.

## Authors

DIOParser is based on [DHParser](https://dhparser.readthedocs.io/).
The first [version of the grammar](https://github.com/badw-dh/Leidener_Klammersystem) was developed in a workshop
at the BBAW. Big shoutout to [Eckard Arnold](https://badw.de/die-akademie/mitarbeiter-verwaltung.html?tx_badwdb_badwperson%5Baction%5D=show&tx_badwdb_badwperson%5Bcontroller%5D=BADWPerson&tx_badwdb_badwperson%5BpartialType%5D=BADWPersonDetailsPartial&tx_badwdb_badwperson%5Bper_id%5D=3782). 