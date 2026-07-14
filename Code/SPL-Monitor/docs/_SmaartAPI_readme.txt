
===== PAGE 1 =====
 
For more information about the API, see the Smaart API Specification. 
 
Copyright © 2021 Rational Acoustics LLC. 
WebSocket API Client Readme 
The WebSocket API Client is a standalone application that was created to provide a simple GUI for 
interfacing with the API server in Smaart v8.3+, Smaart Di 2.1+, and Smaart SPL. The application is 
distributed within the Smaart API SDK, along with other supporting code examples and documentation. 
Before using the Client application, make sure that you enable the API server from the API Options 
dialog within Smaart. The Websocket API Client can run on the same computer where Smaart is running. 
 
Upon opening the WebSocket API Client, choose the desired 
Smaart product from the Product drop list. The application 
begins scanning the local network for instances of that product 
with the API server enabled. The Server drop list should 
populate with all available servers within a few seconds. 
 
After you choose a server, the application will immediately 
connect and populate the Endpoint drop list with any available 
endpoints. Endpoints include the root of the server, as well as 
a streaming endpoint for each running measurement, and 
streaming endpoints for calibrated logging inputs. Connecting 
to the root of the server allows you to send commands that 
are not related to the content of streaming measurements 
(such as the command to start a measurement). Connecting 
directly to a running measurement’s endpoint begins 
processing a stream of live measurement data, and changes 
the Command drop list to include commands related to the 
content of streaming measurements. 
 
Request 
The Request text box is an editable text field that shows a 
formatted preview of the chosen command, which can be sent 
to the server using the Send Request button. Note: some 
commands require manual editing of the request message, to 
include specific details such as the target measurement name, 
tab name, etc. These fields are designated with <angle 
brackets>. 
 
Response 
The Response text box is a read-only display of the response 
received from the server after a request is sent. If you’re connected directly to a measurement 
endpoint, the response field updates with live measurement data in real time, and a “Show Plot” 
checkbox appears allowing you to show a simple plot of the measurement. 
