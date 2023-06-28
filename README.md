# Docserve
Docserve is a simple project that provides documentation from offline files. It allows user to search through
previously cached documentation for the most relevant pages. Docserve uses TF-IDF algorithm to display most
relevant docs.

## Usage
Docserve comes with simple and convinient CLI.
# serve
To start docserve you simply write
```console
py docserve serve
```
This will start Flask application at predefined host and port. You can specify additional informations
using parameters.
# index
Docserve works by preindexing doc files and caching them for later usage. If you want to add documentation
to the registry file use
```console
py docserve index <directory>
```
This will index all files in given directory and automatically save results into binary file.
`index` command can also reindex files that are already present in the registry. This is useful
if some files have been changed.
# info
You can display informations (such as number of indexed documents or size) about compiled registry files by using
```console
py docserve info <datafile>
```
For more usage info refer to `py docserve -h`
\
**NOTE:** This project is not fully finished yet and still lacks a lot of functionality.

