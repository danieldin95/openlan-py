# Multiple OPE
If the ope discover new host, it must shares this host to octl. And the octl will forward this message to other ope. When one cpe startup, it must establish fully connection to all ope has same systemid. 
 
                              octl            
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
           office cpe0      home cpe1        hotel cpex

# Discover OPE
            ope            octl             cpe
            ----           ----             ---
                register to                 
             --------------->|                         
                               discover ope 
                             |<---------------         
                     return ope has samve systemid 
                             --------------->|
                          connect to ope                     
             |<-------------------------------

# Load-Balancing

              ope0             ope1          ope2
               |                 |             |
               ---------------------------------
                                 |
                               hotel cpe0
