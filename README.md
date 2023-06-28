# FHookC2
![fhook](https://github.com/fish-not-phish/FHook/assets/69283986/01ab29fa-9a71-41ac-8668-53732b541e30)

FHookC2 was developed on top of PythonRAT by Safesploit. You can find their GitHub [here](https://github.com/safesploit/PythonRAT/tree/main).

FHook is a Command and Control server which allows an individual to accept connections from multiple remote clients via a remote access tool. 

## C2 Features
+ Tracks current working directory
  + Enables server to change directories on the client
+ TLS encryption
+ Gives basic host machine information
+ Check user privileges
+ Download file from client
+ Upload file to client
+ Single file encrpytion
  + Encrpytion key is stored in client memory
  + Encryption key is sent to the server
    + Key name is based off the file that was encrypted
+ User directory encryption
  + Encrpytion key is stored in client memory
  + Encryption key is sent to the server
    + Key name is based off the username the directory that was encrypted
+ Screenshot of the users main display
  + Image is stored in the clients memory
  + Image is sent to the server
+ Webcam Picture
  + Picture is taken via the webcam and stored in clients memory
  + Picture is sent to the server
+ Persistence
  + Registry
    + Server can give a registry name and the target file to create persistence
  + Startup
    + Server can give the target file to add to the startup folder

## Dependencies
#### Server
```
pip install -r server_requirements.txt
```
#### Client
```
pip install -r client_requirements.txt
```
