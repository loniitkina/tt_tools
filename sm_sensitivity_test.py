import numpy as np


#how important are snow depth and density for freeboard?

#beginning of winter on MYI
ii=.5
si=.1
#0.01707317073170731
#0.026829268292682923
#=35% difference

#beginning of winter on FYI
ii=.5
si=.1
#0.046341463414634146
#0.05609756097560976
#=17% difference

#end of winter on MYI
ii=2
si=.3
#0.1024390243902439
#0.13170731707317074
#=23%

#end of winter on FYI
ii=2
si=.3
#0.21951219512195125
#0.24878048780487805
#=12%

#SNOW DENSITY
#hydrostatic equilibrium with mean snow density and sea ice density (King et al, N-ICE2015) - similar to max MOSAiC density/spring density
rho_i = 882 #King et al reports ice densities at N-ICE from 860 to 920
rho_i = 860
#rho_i = 920

rho_w = 1025

rho_s = 313 #King et al
rho_s = 350 #end of the winter density at MOSAiC

#following Forsstrom et al, 2011, Annals of Glaciology
#fb = (ii - si * (rho_s/(rho_w-rho_i))) * (rho_w-rho_i)/rho_w

fb = (ii * (rho_w-rho_i)/rho_w ) - (si * rho_s/rho_w)
print(fb)

#hydrostatic equilibrium with min snow density/early winter density
rho_i = 882
rho_i = 860
#rho_i = 920

rho_w = 1025

rho_s = 313 #King et al
rho_s = 250 #beginning of the winter density at MOSAiC

fb = (ii * (rho_w-rho_i)/rho_w ) - (si * rho_s/rho_w)
print(fb)

#SNOW-ICE INTERFACE DETECTION ISSUES
