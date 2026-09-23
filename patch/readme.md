# Patching parsed data to Epigraf

Patching parsed data to Epigraf is project/parser agnostic.

Run `patch/patch.py` after transformation/parsing in interactive mode. 
The script exports a CSV-file to `data/patch/` ready for importing via Epigraf's WebUI.
Git ignores patch files. DO NOT commit patch files.

## API patching
API patching is prepared but commented out, to use it, first, copy the `settings.default.py` 
to `settings.py` and add your credentials. The settings.py will be ignored by git

