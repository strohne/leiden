# DIO inscription parser

A parser for Leidener Klammersystem transcriptions from the project Die Deutschen Inschriften.

## Getting started

- Clone the repo
- Install packages:
  ```
  pip install DHParser
  pip install pandas
  ```
  
- If you have access to an Epigraf database, use `transform/getdata.R` to get inscription data.
- Run `transform/parse.py` in interactive mode to parse inscriptions


To generate the parser:
```
dhparser dio.ebnf
```

To run tests:
```
python tst_dio_grammar.py tests_grammar/03_test_dio_passau.ini
```

## Resources

https://epidoc.stoa.org/gl/latest/

https://patrimonium.huma-num.fr/atlas/editor/

https://patrimonium.huma-num.fr/atlas/epidoc-converter/


## Authors

DIOParser is based on [DHParser](https://dhparser.readthedocs.io/).
The first [version of the grammar](https://github.com/badw-dh/Leidener_Klammersystem) was developed in a workshop
at the BBAW. Big shoutout to [Eckard Arnold](https://badw.de/die-akademie/mitarbeiter-verwaltung.html?tx_badwdb_badwperson%5Baction%5D=show&tx_badwdb_badwperson%5Bcontroller%5D=BADWPerson&tx_badwdb_badwperson%5BpartialType%5D=BADWPersonDetailsPartial&tx_badwdb_badwperson%5Bper_id%5D=3782). 