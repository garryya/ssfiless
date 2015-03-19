# ssfiless
### Secure temporary file sharing service
(see [problem description](https://github.com/garryya/ssfiless/blob/master/PROBLEM%20DESCRIPTION) for the details)

* The server implemented as non-blocking REST server using Python Twisted engine, and supports the following REST commands
   * POST - upload a file/folder
   * GET - get file content
   * DELETE - remove a file
* configuration and files metadata stored in conf-file style DB
* 

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
* HUGE files upload
* test
  * POST, GET error handling
* file metadata storage: replace config-file with a DB (couchdb, postgres)
* security
  * authorization
  * encrypt configuration and DB
  * no encryption keys on server (client-side?)
* add folder recursion (?)
* add json schema for REST APIs
* GUI fron-end
