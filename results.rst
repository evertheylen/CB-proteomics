
Crux Comet
==========

Command::

    ../etc\ \[NS\]/crux/bin/crux comet --overwrite T --missed-cleavages 1 --score xcorr --decoy_search 1  data/qExactive01819_1.mgf data/uniprot-human-reviewed-trypsin-november-2016.fasta

For ``_1``, generally seems to report only these peptides:

  - LEAPSLAR, xcorr = 0.825
  - LSNPSLVK, xcorr = 0.782
  - LIAISVLK, xcorr = 0.769
  - ILNALRR, xcorr = 0.726
  - LINALRR, xcorr = 0.726


Own results
===========

First rough implementation of Sequest

==  ==================  ========================================================
#   score               name                                                    
==  ==================  ========================================================
 1   11817.44323360772  TARGET LEWLRDWMEGSGR                                    
 2  11587.847136115834  TARGET LEVSVDGLTLSPDPEERPGAEGAPLLPPPLPPPSPPGSGR         
 3    9862.39148564642  TARGET IEGEIATLKDNDPAPK                                 
 4   9621.682045165662  TARGET ELEGTAK                                          
 5   9544.118521784198  TARGET ELADHAGSGR                                       
 6   9544.118521784198  TARGET ELADLARLHPTSCAPNGLNPNLMVTGGPALAGSGR              
 7    9527.89183199998  TARGET LEWVQDNIRAAQDLCEEALR                             
 8   9508.616109632068  DECOY  IEWAYSGDRLMFIAR                                  
 9   9500.858043001994  DECOY  LEWYTDNSVWAERQNADIVK                             
10   9498.840488731512  TARGET IEWNSRVVSTCHSLVVGIFGLYIFLFDEATK                  
11   9488.252195016092  TARGET IEWDTWTCVLGPTCEGIWPAHSDITDVNAASLTKDCSLLATGDDFGFVK
12   9487.375260750372  TARGET LEWTRLVDEPGHCADFHPSGTVVAIGTHSGR                  
13   9477.613419629577  DECOY  LEWHGSGVGADGDK                                   
14   9476.315873886244  TARGET IEWVWLHWSEYLLAR                                  
15   9476.315873886244  DECOY  LEWSNTSGASNSCHGLLAR                              
16   9476.315873886244  DECOY  IEWSQRVGDGAAMLAGCGLTNTVLLAR                      
17   9476.113055498923  DECOY  LEWADIDPK                                        
18     9471.1988134029  DECOY  LESVSMSSSLSVQFENGALMKVTLDWGM                     
19   9462.867507432022  TARGET LPGGSADGKPK                                      
20   9454.816874589831  TARGET IEWNSR                                           
==  ==================  ========================================================


Second, with optimizations and normalization

==  ==================  ===============================================
#   score               name                                           
==  ==================  ===============================================
 1                 1.0  TARGET LEWLRDWMEGSGR                           
 2  0.9818747501332132  TARGET LEVSVDGLTLSPDPEERPGAEGAPLLPPPLPPPSPPGSGR
 3  0.8344819608349591  TARGET IEGEIATLKDNDPAPK                        
 4  0.8138269179905716  TARGET ELEGTAK                                 
 5  0.8072602568706192  TARGET ELADHAGSGR                              
 6  0.8072602568706192  TARGET ELADLARLHPTSCAPNGLNPNLMVTGGPALAGSGR     
 7  0.8061626455888643  TARGET LEWVQDNIRAAQDLCEEALR                    
 8  0.8045307298233845  DECOY  IEWAYSGDRLMFIAR                         
 9   0.803839438530928  TARGET IEWNSRVVSTCHSLVVGIFGLYIFLFDEATK         
10  0.8029381198115211  DECOY  LEWYTDNSVWAERQNADIVK                    
11  0.8028687726362798  TARGET LEWTRLVDEPGHCADFHPSGTVVAIGTHSGR         
12  0.8020423183991274  DECOY  LEWHGSGVGADGDK                          
13  0.8018339951374115  TARGET LPGGSADGKPK                             
14  0.8009794962296892  DECOY  LEWADIDPK                               
15  0.8008603376182201  TARGET IEWVWLHWSEYLLAR                         
16  0.8008603376182201  DECOY  LEWSNTSGASNSCHGLLAR                     
17  0.8008603376182201  DECOY  IEWSQRVGDGAAMLAGCGLTNTVLLAR             
18  0.7999759941740311  TARGET IEWNSR                                  
19   0.799816042168412  DECOY  LEWSNTSGASNSCHGLLARLFPQNSIHDDDLYLDNK    
20  0.7995383095789251  DECOY  LEWSAISGDSDEADPK                        
==  ==================  ===============================================

Third, now with major rewrite!

==  ==================  ============
#   score               name        
==  ==================  ============
 1                 1.0  TARGET LNPS 
 2  0.9317865739670309  TARGET GESH 
 3  0.9208869048758906  DECOY  HAAM 
 4  0.6627497323197895  TARGET FGCC 
 5   0.654003086473352  TARGET HSGE 
 6  0.6522521521353196  TARGET QVLA 
 7  0.6272875081705239  TARGET NPAK 
 8  0.6267032076946166  TARGET NAPK 
 9  0.6259401629695412  TARGET AILN 
10  0.6215194551448977  TARGET APDK 
11  0.6211920606548391  TARGET ADPK 
12  0.6187727552094202  TARGET ASPR 
13  0.6169329474465026  TARGET APSR 
14  0.6112434366935157  TARGET AAIR 
15  0.6112434366935157  TARGET AALR 
16  0.6040846378631027  TARGET AIAR 
17  0.6040846378631027  TARGET ALAR 
18  0.5923207053537102  TARGET GGPAK
19  0.5917364048778028  DECOY  GGAPK
20   0.587147311893423  TARGET AALGV
==  ==================  ============

