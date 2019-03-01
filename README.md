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

1. OpenLAN messages support UDP, and now using TCP to transport it;
2. Fully OpenLAN supports include controller, multiope, ope register and discover mechanism;


