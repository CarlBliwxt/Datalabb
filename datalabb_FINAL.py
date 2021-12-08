#Import modules and define useful functions
import math
import matplotlib.pyplot as plt
import pandas as pd 

import cantera as ct
import numpy as np
import sys
import csv
from rankinefunktioner import printState 
import rankinefunktioner as rankine
import forbranningsfunktioner as forbr


####### RANKINE CYCLE ###############################################

# parameters for rankine cycle
eta_pump = 0.6     # pump isentropic efficiency
eta_turbine = 0.8  # turbine isentropic efficiency
p_max = 8.0e5       # maximum pressure

#create an object representing water
w = ct.Water()

#Beräkningar för rankine-cykelns olika punkter

# Punkt 1, innan trycksättningar
# start with saturated liquid water at 300 K
w.TQ = 300.0, 0.0
h1 = w.h
p1 = w.P

# Punkt 2, trycksatt, men innan tillförd värme
# pump it adiabatically to p_max
pump_work = rankine.pump(w, p_max, eta_pump)
h2 = w.h
w.PQ = p_max, 1.0
####### SLUT RANKINE CYCLE ###############################################

####### SKAPA VEKTORER SOM FYLLS MED DATA #################################
#Vektorer med resultat som ska fyllas i
# Vektorer för att lagra data
phi_luftoverskott=[];
effs=[]
heats=[]
chemicals=[]

npoints = 50
lower_bound = float(input("Enter minimum equivalence ratio:"))
higher_bound = float(input("Enter maximum equivalence ratio:"))

# fill array phi (the symbol for equivalen ratio) with values from minimum to maximum equivalence ratio
phi = np.linspace(lower_bound, higher_bound, npoints)

T_ad = [];
T_ad_Cantera = np.zeros(npoints)

####### SLUT SKAPA VEKTORER SOM FYLLS MED DATA #################################



########SÄTT FÖRUTSÄTTNINGAR FÖR FÖRBRÄNNING ###################################

T = 300.0
P = 101325.0

#Vattenflödet (kg/s)
waterrate_kg__s = 10
#Luftflödet (kg/s)
airrate_kg__s = 10;



########## VARIERA RELATIVA LUFT/BRÄNSLE-FÖRHÅLLANDEN ##########################
#                                                                              #
# Det är i denna delen ni ska genomföra ändringar                              #
#                                                                              #
################################################################################


#Luft/bränsle-förhållande
AFratio = 6.5

#Värmevärdet (för senare jämförelse med vad energin hamnar)
temp = forbr.LHVandTAD(T, 1)
delta_hc_J__kg = temp[0]

for i in range(npoints):
  #Visa att beräkningarna pågår (att datorn inte hängt sig
  #print('Calculating for phi = {0:12.4g}'.format(phi[i]))
  if (phi[i] <= 1): 
    #Beräknar adiabatiska flamtemperaturen
    temp = forbr.LHVandTAD(T, phi[i])
    T_ad_denna = temp[1]
    #Lägg till i arrayen för att kunna plotta senare
    phi_luftoverskott.append(phi[i])
    T_ad.append(T_ad_denna);
    

#Beräkna entalpiförändring, adiabatisk flamtemperatur och gassammansättning vid aktuellt relativt bränsle/luftförhållande med hjälp av Cantera
  hDiff_J__kg,T_ad_Cantera[i],forbr.Composition[:,i]=forbr.React(phi[i],T,P)
  #Totala flödet =  luftflödet + bränsleflödet. Bränsleflödet är per definition luftflödet / luft/bränsle-förhållandet.
  totalFlowrate_kg__s = airrate_kg__s + airrate_kg__s/AFratio 

  #Beräkna den effekt med vilken värme producerats under processen
  temp = forbr.React(phi[i],T, P) # skapar en temporär variabel som innehåller två element
  # första elementet abges delta_hc_J__Kg
  heatproduction_J__s = - temp[0] * totalFlowrate_kg__s

  #Beräkna den frigjorda
  heatreleased_J__kg = -hDiff_J__kg*(1 + AFratio)

  #Andel av energin i bränslet (värmevärdet) som omvandlats till värme
  heat_fraction = heatreleased_J__kg/delta_hc_J__kg
  #Resten kvar som kemisk energi hos gaserna som bildats
  chemical_fraction = 1 - heat_fraction
  
  #Beräkna hur mycket entalpin hos vattnet ökat (= producerad värme / vattenflödet)
  heat_added_J__kg = heatproduction_J__s/waterrate_kg__s

  #Beräkna entalpin för punkt 3 i Rankinecykeln
  h3 = heat_added_J__kg + h2
  
  #Sätt det nya tillståndet för punkt 3
  w.HP = h3,p_max

  # Beräkna utvunna energin när gå från punkt 3 till punkt 4
  # expand back to p1
  turbine_work = rankine.expand(w, p1, eta_turbine)

  #Beräkna effektiviteten för Rankinecykeln
  eff = (turbine_work - pump_work)/heat_added_J__kg
  #Lägg till värden till vektorer. Multiplicera med 100 (för att plotta värden som procent)
  effs.append(eff*100)
  heats.append(heat_fraction*100)
  chemicals.append(chemical_fraction*100)
#Presentera resultaten i figurer
box = dict(facecolor='yellow', pad=5, alpha=0.2)

#Figuren innehåller via subplottar (adiatisk flamtemperatur, 
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
fig.subplots_adjust(left=0.2, wspace=0)
ax1.set_xlabel('Rel. bränsle/luft-förh.')
ax1.set_ylabel('Adiabatisk flamtemperatur (K)')
ax1.plot(phi_luftoverskott, T_ad, label='"För hand"')
ax1.plot(phi,T_ad_Cantera, label='Cantera')
ax1.legend(loc=0)
#Körningför förgasning
# Syngas composition 
# 30-60 % Co 
# 25-30% H
# 0-5 CH4 
# 5-15 C02

if higher_bound <= 1 : 
  fig.suptitle('Förgasning')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('CO2'),:],label='CO2')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('CO'),:],label='CO')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('H2'),:],label='H2')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('H2O'),:],label='H20')

#Komplettera/ersätt med andra relevanta gaser enligt samma format (d.v.s. ersätt 'O2' med aktuell gasformel)
else: 
  fig.suptitle('Förbränning')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('CO2'),:],label='CO2')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('O2'),:],label='O2')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('N2'),:],label='N2')
  ax2.plot(phi, forbr.Composition[forbr.gas.species_index('H2O'),:],label='H2O')
ax2.set_yscale('log')
ax2.legend(loc=0)
ax2.set_xlabel('Rel. bränsle/luft-förh.')
ax2.set_ylabel('Concentration')


ax3.plot(phi, heats,label='Värme')
ax3.plot(phi, chemicals,label='Kemisk energi')
ax3.legend(loc=0)
ax3.set_xlabel('Rel. bränsle/luft-förh.')
ax3.set_ylabel('Fördelning (%)')
ax4.plot(phi, effs)
ax4.legend(loc=0)
ax4.set_xlabel('Rel. bränsle/luft-förh.')
ax4.set_ylabel('Elverkningsgrad')
plt.tight_layout()

plt.show()
