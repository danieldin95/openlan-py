# Multi-Ope
If the ope discover new host, it must shares this host to memcached, and other ope will find frame's destination which cpe belongs to by memcached. When one cpe startup, it must establish fully connection to all ope as known.
 
                           memcached            
                               |                 
                 ----------------------------  
                 |             |            |    
               ope0          ope1         opex  
                 |             |            |    
              ------------------------------------ Your VPS
                               |
                           Internet
                               |
              ------------- TCP/UDP--------------- Your VMs
              |                |                 |
           Office cpe0      Home cpe1        Hotel cpex


# Load-Balancing
