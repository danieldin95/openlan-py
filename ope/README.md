# Multi-Ope
 If OPE find new host, it MUST share this host to memcached, And other OPE will find frame's destination which CPE belongs to by memcached.
 When CPE booting load, it MUST establish fully connection to all PEx.
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


# Load-Balancing
