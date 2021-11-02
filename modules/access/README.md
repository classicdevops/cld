Module for `protect network ports` of servers, with the ability to `access only by allowed lists` of ip addresses, as well as `blocking all connections` to any of the servers using `prohibited lists` of ip addresses

Модуль представляет из себя централизованную систему управления списками доступов к инстанцам находящимся под управлением CLD. Основной задачей данного модуля является обеспечение контролируемого и безопасного доступа пользователей к инстанцам. Кроме того, модуль реализует функционал управления безопасным доступом между инстанцами для разрешения подключенния требуемых служб и сервисов. Данный модуль имеет довольно широкую область применения:
1. Позволяет полностью ограничить доступ к вашим инстанцам, паралельно формируя и обновляя список разрешенных для подключения ip адресов.
2. Реализует функционал, который позволяет разграничивать доступ к списку или даже диапазону портов.
3. Имеет возможности гибкой кастомизации правил доступа к инстанцам под управлением CLD и позволяет определять список защищенных для подключения портов к каждому из инстанцов.

The module is a centralized system for managing access lists to instances managed by CLD. The main recommended module is to provide controlled and secure user access to instances. In addition, the module implements the functionality of managing secure access between instances to allow the required services and services. This module has a fairly wide range of applications:
1. Allows you to completely restrict access to your instances, in parallel forming and updating the list of allowed IP addresses for connection.
2. Implements functionality that allows you to delimit access to a list or even a range of ports.
3. Has the ability to customize the rules for accessing instances under CLD control and allows you to define a list of protected ports for connection to each of the instances.
