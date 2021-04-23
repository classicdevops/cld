Cloud manage module provides such functionality as creation, configuration and management of KVM servers on hypervisors running "Proxmox VE (Virtualization Management Platform)". The existing toolkit allows in the console mode to carry out all basic operations with KVM servers located on hypervisors under the control of CLD.
Main functions and features:
- KVM creation supports interactive mode, servers are created based on operating system (OS) templates such as Centos, Debian, Ubuntu, Fedora, FreeBSD
- OS templates are loaded onto the hypervisor automatically
- basic configuration of OS, network, access credentials is done directly during KVM deployment from a template, each KVM server parameter is configured by arguments, or interactively
- support for creating several types of file systems is available (zfs, lvm, qcow2), it is recommended to use zfs - it has high quality and stability when working in production
- control over the assignment and operation of ip addresses for each KVM is set during deployment
- QEMU guest agent is installed in each OS, all control options from the hypervisor are available
- for each KVM during deployment, a serial port is connected, the serial console is configured in all OS templates
- auto login option for serial console
- changing the root password for KVM in soft (without rebooting) and hard modes (by mounting the FS on a switched off KVM)
- migration of KVM between hypervisors in interactive and direct modes (zfs), (other filesystems through shared network storage)
- centralized KVM server management functionality (start, stop reset, destroy)
- support for api OVH, Hetzner, Online.net (ordering ip addresses, migrating ip addresses between services, creating MAC)
- daily check of KVM backups on hypervisors, clear report in telegram or by email.
- scripts for deploying hypervisors (debian 9, debian 10), full OS configuration, network configuration, network storages