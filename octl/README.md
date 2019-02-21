# Multiple OPE

If OPE discover new host, it must shares this host to OCTL. And OCTL will forward this message to other OPE. 
When one CPE startup, it must establish fully connection to all OPE has same systemID. 
 
                             octl            
                               |                 
                 ----------------------------  
                 |             |            |    
               ope0          ope1         opex  
                 |             |            |    
                 ---------------------------- your VPS
                               |
                           Internet
                               |
              ------------- TCP/UDP--------------- your VMs
              |                |                 |
           office cpe0      home cpe1        hotel cpex

# Discover OPE

1. OPE send register message to OCTL;
2. OCTL received OPE register message, and saved it;
3. CPE send discover message to OCTL, and OCTL reply OPE information.
4. CPE received OPE information from OCTL, and connecting to all OPE has same systemID;
5. When CPE received ethernet frame from tap device, forwarding it to OPE evenly.

# Load-Balancing

As we see the above, every CPE establishes connections to multiple OPE for load-balancing it's traffic.
