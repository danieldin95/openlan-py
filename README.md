# openlan-py
openlan python implements, and we just implement simple damo. 

                                            ope(vps in wlan)
                                                   |
                                   --------------------------------
                                  |                                |
                                oce(vmware vm)             oce(vmware vm)
                                  |                                |
                                br-olan                          br-olan
                                  | ethx                           | ethx
                              office wifi                      home wifi

# start cpe
cd openlan-py && python -m cpe.bridge 144.10.123.1

# start ope
cd openlan-py &&  python -m ope.gateway
