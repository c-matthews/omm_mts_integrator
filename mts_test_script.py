"""
Small example of a new MTS method, implemented in OpenMM
Charles Matthews mail@cmatthe.ws
19 September 2022

set the parameters below and then run with
> python mts_test_script.py

"""

import time
from openmmtools import testsystems, integrators, forces

import numpy as np
try:
    import openmm.unit as unit
    import openmm as mm
    from openmm import app
except ImportError:  # OpenMM < 7.6
    import simtk.unit as unit
    import simtk.openmm as mm
    from simtk.openmm import app

from openmmtools.constants import kB
from openmmtools import respa, utils
from openmmtools.integrators import LangevinIntegrator
from openmmtools import testsystems, integrators, forces


#####
## Edit parameters here
#####

T = 0.1*unit.nanoseconds
temperature_value = 298.0 * unit.kelvin
friction_value = 1.0 / unit.picoseconds
timestep_value = 10.0 * unit.femtoseconds
num_fast_steps = 5
direct_force_group = 0

platform = mm.Platform.getPlatformByName( 'CUDA' )
platform_props = {
        'Precision' : 'mixed',
        'DeviceIndex' : '0' }


#####
## Instantiate integrators
#####

integrators = [
    mm.LangevinIntegrator(  temperature_value ,
                            friction_value ,
                            timestep_value ),

    mm.LangevinMiddleIntegrator(  temperature_value ,
                                  friction_value ,
                                  timestep_value ),

    mm.MTSLangevinIntegrator(  temperature_value ,
                               friction_value ,
                               timestep_value,
                               [(0,num_fast_steps),(1,1)] ),

    LangevinIntegrator( temperature_value,
                        friction_value,
                        timestep_value,
                        'V R O R V'),

    LangevinIntegrator(temperature_value,
                        friction_value,
                        timestep_value,
                        'V1 ' + 'V0 R O R V0 '*num_fast_steps + 'V1') ,

    LangevinIntegrator(temperature_value,
                        friction_value,
                        timestep_value,
                        'V1 ' +\
                        'V0 R R V0 '*((num_fast_steps-1)//2) +\
                        'V0 R O R V0 ' +\
                        'V0 R R V0 '*((num_fast_steps-1)//2) +\
                        'V1'
                         )

]

integrator_strings=[
    'Default LangevinIntegrator',
    'LangevinMiddleIntegrator',
    'MTSLangevinIntegrator',
    'LangevinIntegrator with Splitting="%s"' % integrators[3]._splitting,
    'LangevinIntegrator with Splitting="%s"' % integrators[4]._splitting,
    'LangevinIntegrator with Splitting="%s"' % integrators[5]._splitting,
]

#####
## Run some tests
#####
print("Running comparison with")
print(' T = ', str(T))
print(' h = ', str(timestep_value))
print(' number of fast steps = ', str(num_fast_steps))
print(' direct force group = ', str(direct_force_group))
print(' ')

for (integrator, integrator_string) in zip(integrators, integrator_strings):

    # Set up the example
    adp = testsystems.AlanineDipeptideExplicit(constraints=None)
    system = adp.system
    positions = adp.positions

    # Split the forces
    for force in system.getForces():
            if force.__class__.__name__ != 'NonbondedForce':
                force.setForceGroup( 0 )
            else:
                force.setForceGroup( direct_force_group )
                force.setReciprocalSpaceForceGroup( 1 )

    # Set up simulation
    sim = app.Simulation(adp.topology,
                         system,
                         integrator,
                         platform=platform ,
                         platformProperties=platform_props )

    # Minimize energy
    context = sim.context
    context.setPositions(positions)
    sim.minimizeEnergy()
    context.setVelocitiesToTemperature( temperature_value )

    # Run until time
    t=0*unit.femtoseconds
    potential_energies = []
    start_time = time.time()

    print("Integrator: {:s}...".format(integrator_string) )
    while (t<T):

        try:
            sim.step(100)
        except Exception as e:
            potential_energies = [ np.nan ]
            break

        t = t + 100*timestep_value
        st = context.getState(getEnergy=True)
        potential_energies.append( st.getPotentialEnergy() )


    # Burn the first 25% of the computed energies
    potential_energies = potential_energies[len(potential_energies)//4:]

    print("  Wall time: {:f}s\n  Mean   PE: {:s}\n  StdDev PE: {:s}\n".format(
                        time.time()-start_time,
                        str(np.mean(potential_energies)),
                        str(np.std(potential_energies))))
