Module for `protect network ports` of servers, with the ability to `access only by allowed lists` of ip addresses, as well as `blocking all connections` to any of the servers using `prohibited lists` of ip addresses

The module is a centralized system for managing access lists to instances managed by CLD. The main recommended module is to provide controlled and secure user access to instances. In addition, the module implements the functionality of managing secure access between instances to allow the required services and services. This module has a fairly wide range of applications:
1. Allows you to completely restrict access to your instances, in parallel forming and updating the list of allowed IP addresses for connection.
2. Implements functionality that allows you to delimit access to a list or even a range of ports.
3. Has the ability to customize the rules for accessing instances under CLD control and allows you to define a list of protected ports for connection to each of the instances.

The Access-module also includes the following functionality:
- A utility that allows you to selectively add users' IP addresses to the list of allowed connections using a special one-time token. This allows not only to increase the level of security, but also ensures that links and tokens cannot be made publicly available.
- If the user who is granted access by IP address does not have a static IP address and is faced with the need to constantly update the IP address - the functionality of the Access module includes the ability to generate a unique access key via VPN. Key generation occurs in a fully automatic mode and is transmitted to the user who requested the VPN key. Further, within the framework of a secure VPN connection - the user does not need to update his IP address, everything happens automatically.
- As part of security work, the Access module has a convenient, simple and straightforward functionality to block unwanted IP addresses. In the event of an attack on any of the CLD instances, you can completely block the connection from a specific IP address and completely exclude the unwanted IP address in a short time. Also, at any time you can display a list of blocked IP addresses that are in the banlist and make a further decision depending on your goals. You can also remove an IP address from a banlist centrally using the built-in utility.

Below is a list of the Access-module initial variables.

| Variable | Description |
| ------ | ----------- |
| CLD_IP | The IP address of the instance where CLD is installed. |
| MIKROTIK | if the architecture of the system implies the use of microtic - the variable that determines its use. |
| MIKROTIK_USER | username mikrotik. |
| MIKROTIK_PASSWORD | password of user mikrotik. |
| MIKROTIK_HOST | The IP address at which mikrotik is located. |
