# Openlan-py
there is openlan python implement, and now just accomplishs simple demo. 

                                    ope(vps on wlan)
                                           |
                           --------------------------------
                          |                                |
                        cpe(vmware vm)             cpe(vmware vm)
                          |                                |
                        br-olan                          br-olan
                          | ethx                           | ethx
                      office wifi                      home wifi

# Start cpe
the machine the cpe running on need install 'bridge-utils', 'iputils' and 'tun' module in kernel. 

    cd openlan-py && python -m cpe.daemon -g 114.32.5.90 -a start

# Start ope
Before you start the ope, you need startup one VPS to bridge your LAN over Internet.

    cd openlan-py &&  python -m ope.daemon -a start

# Todo list
1. haven't support syslog;
2. the ope doesn't support unicast forwarding;
3. need support configure options;
4. openlan messages support udp, and now using tcp to transport it;
5. fully openlan supports include controller, multiope, ope register and discover mechanism.


