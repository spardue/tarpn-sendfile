# tarpn-sendfile

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
