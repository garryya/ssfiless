# ssfiless
## Secure temporary file sharing service

(see https://github.com/garryya/ssfiless/blob/master/PROBLEM%20DESCRIPTION for details)


```
> ssfilesss-client.py --server=SERVER-ADDRESS --action=upload --path=FILENAME
Uploading file FILENAME ...
http://10.0.2.15:8080/FILENAME
Uploaded

> ssfilesss-client.py --server=SERVER-ADDRESS --action=get --path=FILENAME
```

**Questions/assumptions**
* get file content returns what? (maybe HTML: "<html>Hello, world!</html>")

**TODO**
* test
  * POST, GET error handling
* file metadata storage: replace config-file with a DB (couchdb, postgres)
* authorization
* add folder recursion (?)
* add json schema for REST APIs
