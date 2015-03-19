# ssfiless
Secure temporary file sharing service


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
* error handling
* replace config-file style filedata storage with DB (couchdb, postgres)
* add folder recursion
* add json schema for REST APIs
