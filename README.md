# Openlan-py
this is openlan python implements, and now just implement simple demo. 

                                    ope(vps in wlan)
                                           |
                           --------------------------------
                          |                                |
                        cpe(vmware vm)             cpe(vmware vm)
                          |                                |
                        br-olan                          br-olan
                          | ethx                           | ethx
                      office wifi                      home wifi

# Start cpe
the machine cpe running on need install 'bridge-utils', 'iputils' and 'tun' kernel module. 

cd openlan-py && python -m cpe.bridge 144.10.123.1

# Start ope
cd openlan-py &&  python -m ope.gateway

# TODO
1. support syslog or file log;
2. ope support unicast;
3. support config opt;
