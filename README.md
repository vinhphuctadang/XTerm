# Overview:
A simple ChatServer (yet a panel) for sending and recieving JSON messages between clients

# How to use ?

In order to take advantage of the server, 

First, start HNhu.exe (or start an x86 for 32 bit machine)
Next, from any programming language (requires socket library supported):

socket = new Socket ('localhost', 16472) // default HNhu port is 16472
// from now on we can send and recieve via the socket 
// but watch out
// A message is consisting of 2 parts: first 4 bytes are for message size (in byte, denote n) and next n bytes represent the message content in json format

socket.close ()

we can accomplish these tasks:
1. Have kernel to fullfil some information:
  You should sent a Message (format shown above) comprising of:
    ```python
    {
      "type" : "request"
      "function" : "kernel",
      "request" : "get"
      "variable" : "<any_variable>"
    }
    
    ```
    
  Response will have a form like:
  ```
    {
      "type": "response"
      "success" : "true" // or "success":"false"
      "result": "<result_content>"
    }
  ```
    
2. Create a channel, from now on the connection (socket) is used for publishing, see MQTT for more information:
```
    {
      "type" : "request"
      "function" : "kernel",
      "request" : "create"
      "channel" : "<channel_name>" 
    }
```
  
    After the sending attempt, socket should recieve a message contain 
    ```
    {
     "type":"response"
     "result":"<register_channel_name>", 
     "success":"true"
     }
     
     ```
     otherwise a message 
     ```
     {
     "type":"response"
     "success": "false"
     "result":"<error_description>"
     } 
     ```
     
     is returned
     
3. Subscribe a channel:
```
    {
      "type":"response"
      "type" : "request"
      "function" : "kernel",
      "request" : "subscribe"
      "channel" : "<channel_name>" 
    }
    
```
    
    if succeed, the kernel-HNhu- should return a json message: 
```
    {
      "type":"response"
      "success":"true",
      "channel":"<subscribed_channel_name>"
    }
```    
    else a message which formed
```   
    {
      "type":"response"
      "success":"false",
      "result":"error_description"
    }
```
    From the time of successful subscription, the socket will be recieving messages having structure like this:
```
    {
      "type":"noftify",
      "channel":"subscribed channel"
      
      ...      
    }
```
 4. Accepted function via socket:
  <to_be_continue>
