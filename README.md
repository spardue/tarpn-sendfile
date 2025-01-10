# tarpn-sendfile

# Examples

The following example will send a file referenced by `--file` to the BBS of `-to` with a given `subject`

Example:

```shell
./tarpn-sendfile.py --to CALL-SIGN "test" --file tarpn-sendfile.py
```


The following will sync all the files it finds in the BBS inbox:
```shell
./tarpn-sendfile.py --sync
```
If there are any files in your inbox, they will be under `/home/pi/tarpn-sendfile-inbox`

# Install 

The following will download the current version of the script and extract it in your current directory:

```shell
curl -L https://github.com/spardue/tarpn-sendfile/archive/main.zip -o tarpn-sendfile.zip && unzip tarpn-sendfile.zip && rm tarpn-sendfile.zip
```
