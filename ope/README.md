# Multi-Ope
                           Memcached            
                               |                 
                 ----------------------------  
                 |             |            |    
               OPE0          OPE1         OPEx  
                 |             |            |    
              ------------------------------------ Your VPS
                               |
                           Internet
                               |
              ------------- TCP/UDP--------------- Your VMs
              |                |                 |
           Office CPE0      Home CPE1        Hotel CPEx
 
  Memcached: The OPE MUST share fully FIB to memcached.
  Open PEx: Other OPE will find one ethdst which cpe belongs to by memcached.
  Custom PEx: The CPE MUST establish fully connection to all PEx.

# Load-Balancing
