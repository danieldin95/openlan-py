# OpenLAN Python
There is OpenLAN python implement, and now just accomplishs simple demo. 

                                               cpe (linux)
                                                 |
                          -------------------ope(vps on wlan)-----------
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

# Start CPE for Windows

Please refer to [openlan-go olv1](https://github.com/danieldin95/openlan-go/tree/master/olv1)


