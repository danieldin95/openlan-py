# openlan-py
openlan python implements, and we just implement simple damo. 

      ope(vps in wlan)
             |
     -----------------
     |               |
    oce             oce
     |
   br-olan
     |
    eth0
     |
 your wifi

# start cpe
cd openlan-py && python -m cpe.bridge 144.10.123.1

# start ope
cd openlan-py &&  python -m ope.gateway
