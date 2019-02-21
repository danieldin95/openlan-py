# OpenLAN Python

There is OpenLAN python implement, and now just accomplishs simple demo. 

                                         ope(vps on wlan)
                                                 |
                          ----------------------------------------------
                          |                      |                     |
                        cpe(vmware vm)         cpe(vmware vm)        cpe(vmware vm)
                          |                      |                     |
                        br-olan                br-olan               br-olan
                          | ethx                 | ethx                | ethx
                        office wifi            home wifi             hotel wifi

# Start CPE

The machine CPE running on need install 'bridge-utils', 'iputils' and 'tun' module in kernel. 

    cd openlan-py && python -m cpe.daemon -g 114.32.5.90 -a start

# Start OPE

Before you start OPE, you need startup one VPS to bridge your LAN over Internet.

    cd openlan-py &&  python -m ope.daemon -a start

# TODO list

1. Haven't support syslog; -- ok
2. The ope doesn't support unicast forwarding; -- ok
3. Need support configure options; -- ok 
4. OpenLAN messages support UDP, and now using TCP to transport it;
5. Fully OpenLAN supports include controller, multiope, ope register and discover mechanism;
6. Support openlan command tools to diagnose OpenLAN CPE/OPE status and configure it on running time.


