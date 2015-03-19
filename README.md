# ssfiless
#### Secure temporary file sharing service
(see [problem description](https://github.com/garryya/ssfiless/blob/master/PROBLEM%20DESCRIPTION) for the details)

* 2 components: server and command line tool front-end client
* The server implemented as non-blocking REST server (Python+Twisted engine), capable of handling multiple concurrent connections and supports the following REST commands:
   * POST - upload a file/folder
   * GET - get file content
   * DELETE - remove a file (voluntary added, not in requirements)
* configuration and files metadata stored in conf-file style DB (ssfiless.conf)
* files are stored encrypted on disk, encryption keys in DB next to the file (bad!) 
* cleanup runs periodically and removes old files from both DB and disk (the frequency and file age are configurable)

#### Testing
The server is running on AWS micro instance. Use examples below and server=ec2-54-87-90-127.compute-1.amazonaws.com
for testing

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
* Folders (**requirements**)
* HUGE files upload (**requirements**)
* security
  * no encryption keys on server or in-clear (*very-very bad!!!*)
    * option1: client-side encryption? key provided by a client
    * option2: authirization + HMAC-based encryption 
  * encrypt configuration and DB
* add folder recursion (?)
* add service stuff: start/stop/restart 
* file metadata storage: replace config-file with a DB (couchdb, postgres)
* add json schema for REST APIs
* GUI fron-end
