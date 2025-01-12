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
Clone this repo and run the following:

```shell
pip install -r requirements.txt
```

# Run

Run the web service locally in dev mode:

```shell
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Send a file to other stations:
```shell
curl -X 'POST' 'http://127.0.0.1:8000/send_file/'      -F 'callsigns=K5ABC'      -F 'to=N1XYZ'      -F 'to=W4RT'      -F 'file=@app.py' -F 'note=Hello there friends'
```
