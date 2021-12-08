import numpy as np
import cantera as ct

def LHVandTAD(T_i,phi):
  #Funktion som beräknar det lägre värmevärdet och den adiabatiska flamtemperaturen för metanol
  #Den använder följande indata
  #
  # T_i         Temperatur före förbränning
  # phi         Relativt bränsle/luft-förhållande
  

  #Formation enthalpies
  hfi_CH3OH = -201011     #kJ/kmol (Table B.2)
  hfi_C2H5OH = -236277    #kJ/kmol (Table B.1)
  hfi_O2 = 0              #kJ/kmol (Table A.11)
  hfi_N2 = 0              #kJ/kmol (Table A.7)
  hfi_CO2 = -393546       #kJ/kmol (Table A. )
  hfi_H2O = -241845       #kJ/kmol (Table A.

  #Reaction enthalpy
  delta_hr = 1*hfi_CO2+2*hfi_H2O-1*hfi_CH3OH #kj/kmol
  #Enthalpy of combustion
  delta_hc = -delta_hr #kj/kmol
  delta_hc_J__kg=delta_hc*1000/(12+4+16)

  #Heat capacities, in J kmol-1 K-1 (from the same tables as above)
  CP_TEMPS=[300,400,500,600,700,800,900,1000,1100,1200,1300,1400,1500]; #Temperatures for the values
  CP_CO2 =[37.28,41.276,44.569,47.313,49.617,51.55,53.136,54.360,55.333,56.205, 56.984,57.677,58.292] #kJ/kmol*K
  CP_H2O =[33.468,34.437,35.3337,36.288,37.364,38.587,39.930,41.315,42.638,43.874,45.027,46.102,47.103]  #kJ/kmol*K
  CP_N2 = [29.075,29.319,29.636,30.086,30.684,31.394,32.131,32.762,33.258,33.797,34.113,34.477,34.804]  #kJ/kmol*K
  CP_O2 = [29.331,30.210,31.114,32.030,32.927,33.757,34.454,34.936,35.27,35.593,35.903,36.202,36.49]    #kJ/kmol*K

  #Calculate amount of different molecules based on equivalence ratio
  co2=phi*1
  h2o=phi*2
  o2=(1-phi)*1.5
  n2=1.5*3.76;
  delta_hr = co2*hfi_CO2+h2o*hfi_H2O-phi*hfi_CH3OH #kj/kmol
  delta_hc = -delta_hr #kj/kmol

  #Iterate to get a good value of the adiabatic flame temperature
  T_guess=(T_i+2200)/2
  T_guess_old=0;
  while (abs(T_guess-T_guess_old)>1):
    cp_co2=np.interp(T_guess,CP_TEMPS,CP_CO2)
    cp_h2o=np.interp(T_guess,CP_TEMPS,CP_H2O)
    cp_n2=np.interp(T_guess,CP_TEMPS,CP_N2)
    cp_o2=np.interp(T_guess,CP_TEMPS,CP_O2)
    cp_total = co2*cp_co2+h2o*cp_h2o+n2*cp_n2+o2*cp_o2
    T_ad=T_i+(delta_hc/cp_total);
    T_guess_old=T_guess;
    T_guess=(T_i+T_ad)/2
  return delta_hc_J__kg,T_ad


def React(phi,T_i,P):
  #Funktion som beräknar entalpiförändringen, adiabatiska flamtemperaturen och sammansättningen på produktgaserna med hjälp av Cantera
  #Den använder följande indata
  #
  # phi         Relativt bränsle/luft-förhållande  
  # T_i         Temperatur före förbränning
  # P           Tryck 

  carbon = ct.Solution('graphite.xml')
  mix_phases = [(gas, 1.0), (carbon, 0.0)]


  #Sätt relativa bränsle-luft-förhållandet i gasen
  gas.set_equivalence_ratio(phi, 'CH3OH', 'O2:1.0, N2:3.76')
  mix = ct.Mixture(mix_phases)

  #Sätt temperatur och tryck för blandning går till jämvikt
  mix.T = T_i
  mix.P = P

  #Entalpin för blandningen före reaktion (=innan blandningen gått till jämvikt
  hBefore_J__kg=mix.phase(0).h

  #Sätt blandningen till jämvikt
  mix.equilibrate('HP', solver='gibbs', max_steps=1000)
  
  #Läs av temperature = Adiabatiska flamtemperaturen om alla reaktioner får gå till jämvikt (=mer korrekt än att anta att bara CO2 och H2O bildas)
  tad = mix.T
  #Sammansättningen på de bildade gaserna
  xeq = mix.species_moles
  #Läs av vid 298.15 K för att få bildningsentalpin (alltså entalpin exklusive den sensibla entalpin)
  mix.T=298.15
  #Entalpin efter reaktionen
  hAfter_J__kg=mix.phase(0).h
  #Entalpiförändringen
  hDiff_J__kg=hAfter_J__kg-hBefore_J__kg
  return hDiff_J__kg,tad,xeq






# phases
gas = ct.Solution('gri30.xml')
carbon = ct.Solution('graphite.xml')

# the phases that will be included in the calculation, and their initial moles
mix_phases = [(gas, 1.0), (carbon, 0.0)]

# create a mixture of 1 mole of gas, and 0 moles of solid carbon.
mix = ct.Mixture(mix_phases)

# equivalence ratio range
npoints = 50


Composition=np.zeros((mix.n_species,npoints));
