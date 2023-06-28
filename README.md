# FHookC2
![fhook](https://github.com/fish-not-phish/FHook/assets/69283986/01ab29fa-9a71-41ac-8668-53732b541e30)

FHookC2 was developed on top of PythonRAT by Safesploit. You can find their GitHub [here](https://github.com/safesploit/PythonRAT/tree/main).

FHook is a Command and Control server which allows an individual to accept connections from multiple remote clients via a remote access tool. This is only for educational purposes, please do not use this to perform any form of illegal activity and always get permission prior to remoting into an individuals device.

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
### OpenSSL
Download OpenSSL to create a certificate.
##### Windows
Download the correct version [here](https://slproweb.com/products/Win32OpenSSL.html).
#### Linux
sudo apt install openssl
#### Creating the certifcate
```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```
## Command Help
### Selection Menu
![target_manual](https://github.com/fish-not-phish/FHook/assets/69283986/f01d253b-2c97-4f64-aa9b-ead36bc177f7)
### Target Commands
![manual](https://github.com/fish-not-phish/FHook/assets/69283986/e6f42c74-1c3c-4a96-a643-c8db747bf3ec)


