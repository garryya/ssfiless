# ssfiless
#### Secure temporary file sharing service
(see [problem description](https://github.com/garryya/ssfiless/blob/master/PROBLEM%20DESCRIPTION) for the details)

* The server implemented as non-blocking REST server using Python Twisted engine, and supports the following REST commands
   * POST - upload a file/folder
   * GET - get file content
   * DELETE - remove a file (voluntary added, not in requirements)
* configuration and files metadata stored in conf-file style DB
* 

#### Usage examples using client tool and the command line:
##### Upload
```
> ./ssfilesss-client.py --server=localhost --action=upload --path=requirements.txt
Uploading file requirements.txt ...
http://10.0.2.15:8080/2cbffc36-0c24-4f15-89ad-3735adeb1cef
Uploaded
```
##### Get content
```
> ./ssfilesss-client.py --server=localhost --action=get --path=2cbffc36-0c24-4f15-89ad-3735adeb1cef
Twisted-Core==13.2.0
Twisted-Web==13.2.0
argparse==1.2.1
httplib2==0.8
jsonschema==2.3.0
simplejson==3.3.1
zope.interface==4.0.5
configobj==4.7.2
```
##### Get content - cUrl 
```
> curl -s -X GET -H "Content-Type: application/octet-stream" http://localhost:8080/2cbffc36-0c24-4f15-89ad-3735adeb1cef
Twisted-Core==13.2.0
Twisted-Web==13.2.0
argparse==1.2.1
httplib2==0.8
jsonschema==2.3.0
simplejson==3.3.1
zope.interface==4.0.5
configobj==4.7.2
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
