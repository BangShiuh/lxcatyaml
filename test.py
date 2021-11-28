import cantera as ct


# spec = ct.Species.listFromFile('oxygen-plasma.yaml')
# spec_gas = ct.Solution(thermo='IdealGas', species=spec)
coll = ct.Collision.listFromFile('oxygen-plasma.yaml')
print(coll[0].kind)
print(coll[0].threshold)
print(coll[0].equation)
print(coll[0].energy_data)
print(coll[0].cross_section_data)


# print(repr(coll[0]))
# gas = ct.Solution(thermo='IdealGas', kinetics='GasKinetics',
#                     species=spec, collisions=)
