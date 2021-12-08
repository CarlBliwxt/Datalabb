#Import modules and define useful functions
import math
import matplotlib as plt
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
printState(1,w)

# Punkt 2, trycksatt, men innan tillförd värme
# pump it adiabatically to p_max
pump_work = rankine.pump(w, p_max, eta_pump)
h2 = w.h
w.PQ = p_max, 1.0
print(1,w)
####### SLUT RANKINE CYCLE ###############################################

####### SKAPA VEKTORER SOM FYLLS MED DATA #################################
#Vektorer med resultat som ska fyllas i
# Vektorer för att lagra data
phi_luftoverskott=[];
effs=[]
heats=[]
chemicals=[]

npoints = 50
lower_bound = float(0.1)
higher_bound = float(0.9)

# fill array phi (the symbol for equivalen ratio) with values from minimum to maximum equivalence ratio
phi = np.linspace(lower_bound, higher_bound, npoints)

T_ad = [];
T_ad_Cantera = np.zeros(npoints)

####### SLUT SKAPA VEKTORER SOM FYLLS MED DATA #################################



########SÄTT FÖRUTSÄTTNINGAR FÖR FÖRBRÄNNING ###################################

T = 300.0
P = 101325.0

#Vattenflödet (kg/s)
waterrate_kg__s=10
#Luftflödet (kg/s)
airrate_kg__s=10;



########## VARIERA RELATIVA LUFT/BRÄNSLE-FÖRHÅLLANDEN ##########################
#                                                                              #
# Det är i denna delen ni ska genomföra ändringar                              #
#                                                                              #
################################################################################


#Luft/bränsle-förhållande
AFratio = 3/2

#Värmevärdet (för senare jämförelse med vad energin hamnar)
delta_hc_J__kg = np.zeros(npoints)


for i in range(npoints):
  #Visa att beräkningarna pågår (att datorn inte hängt sig
  #print('Calculating for phi = {0:12.4g}'.format(phi[i]))
 
  
  #Beräkna adiabatiska flamtemperaturen "för hand" (som ni gjort tidigare under kursen)
  #Första variablen kallad "dummy" eftersom vi inte använder den (värmevärdet)
  #Beräknar bara för relativa bränsle/luft-värden som är lika med eller under ett
  #eftersom reaktionsformeln bara är korrekt för dessa
  if (phi[i]<=1):
    temp = forbr.LHVandTAD(T, phi[i])
    delta_hc_J__kg[i] = temp[0]
    T_ad_denna = temp[1]
    #Beräkna adiabatiska flamtemperaturen
    #dummy,T_ad_denna=...
  
    #Lägg till i vektorer för att kunna plotta senare
    phi_luftoverskott.append(phi[i])
    T_ad.append(T_ad_denna);

#Beräkna entalpiförändring, adiabatisk flamtemperatur och gassammansättning vid aktuellt relativt bränsle/luftförhållande med hjälp av Cantera
  hDiff_J__kg,T_ad_Cantera[i],forbr.Composition[:,i]=forbr.React(phi[i],T,P)
  

  #Totala flödet =  luftfcalödet + bränsleflödet. Bränsleflödet är per definition luftflödet / luft/bränsle-förhållandet.
  totalFlowrate_kg__s = airrate_kg__s + airrate_kg__s/AFratio 

  #Beräkna den effekt med vilken värme producerats under processen
  temp = forbr.React(phi[i],T, P)
  heatproduction_J__s = temp[0]

  #Beräkna den frigjorda
  heatreleased_J__kg=-hDiff_J__kg*(1+AFratio)

  #Andel av energin i bränslet (värmevärdet) som omvandlats till värme
  temp1 = forbr.React1(phi[i],T,P)
  before = temp1[0]
  after = temp1[1]
  heat_fraction = heatproduction_J__s/(before + after)

  print(heat_fraction)
  
  #Resten kvar som kemisk energi hos gaserna som bildats
  chemical_fraction=...
  
  #Beräkna hur mycket entalpin hos vattnet ökat (= producerad värme / vattenflödet)
  heat_added_J__kg = heat_added_J__kg/waterrate_kg__s

  #Beräkna entalpin för punkt 3 i Rankinecykeln
  w.PQ = p_max, 1.0
  h3 = w.h
  
  #Sätt det nya tillståndet för punkt 3
  w.HP = h3,p_max

  # Beräkna utvunna energin när gå från punkt 3 till punkt 4
  # expand back to p1
  turbine_work = rankine.expand(w, p1, eta_turbine)

  # Beräkna effektiviteten för Rankinecykeln
  eff =(turbine_work - pump_work)/heat_added_J__kg
  
  

  #Lägg till värden till vektorer. Multiplicera med 100 (för att plotta värden som procent)
  #effs.append(eff*100)
  #heats.append(heat_fraction*100)
  #chemicals.append(chemical_fraction*100)

