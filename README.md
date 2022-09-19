# OpenMM MTS test script

This short piece of Python3 code tests the performance of six integrators. The first five are well known, but the sixth is (to the best of my knowledge) novel. The six integrators are

- `openmm.LangevinIntegrator`
- `openmm.LangevinMiddleIntegrator`
- `openmm.MTSLangevinIntegrator`
- `openmmtools.integrators.LangevinIntegrator` with the following splittings:
    - `V R O R V`
    - `V1` + $5\times$`(V0 R O R V0)` + `V1`
    - `V1` + $2\times$`(V0 R R V0)` + `(V0 R O R V0)` + $2\times$`(V0 R R V0)` + `V1`

The latter of these splittings is novel. It adds a velocity verlet step inside the usual R-RESPA style multiple timestepping method. In the example we use five cheap steps with force group `V0`, and one kick with force group `V1`.

# Parameters

The provided script is meant to be a short example using the latter scheme. The example runs on solvated alanine dipeptide with rigid water and a flexible protein (and no HMR). Feel free to experiment by constraining all H bonds and potentially adding HMR, but we would not expect the method to work well if the water is left unconstrained as well.

At the start of the file you can see some parameters for the experiment, including the length of the run, temperature, and timestep value. You can also specify which force group the direct non-bonded force should be in (either 1 or 0). 

# Usage

Run the script with 

``$> python mts_test_script.py``

# Sample output

Let's alter the parameters of the script and run two examples at different timesteps. The mean and standard deviation of the potential energy is output.

- Example #1
```
Running comparison with
 T =  5.0 ns
 h =  2.0 fs
 number of fast steps =  5
 direct force group =  0
 
Integrator: Default LangevinIntegrator...
  Wall time: 674.612839s
  Mean   PE: -28765.244929120916 kJ/mol
  StdDev PE: 185.55197122562552
  
Integrator: LangevinMiddleIntegrator...
  Wall time: 703.144003s
  Mean   PE: -28845.740959823004 kJ/mol
  StdDev PE: 180.19662273145232

Integrator: MTSLangevinIntegrator...
  Wall time: 1974.896122s
  Mean   PE: -28808.415974173164 kJ/mol
  StdDev PE: 178.83605602572098
  
Integrator: LangevinIntegrator with Splitting="V R O R V"...
  Wall time: 902.185686s
  Mean   PE: -28846.000793139396 kJ/mol
  StdDev PE: 182.70083567141015
  
Integrator: LangevinIntegrator with Splitting="V1 V0 R O R V0 V0 R O R V0 V0 R O R V0 V0 R O R V0 V0 R O R V0 V1"...
  Wall time: 2470.131505s
  Mean   PE: -28847.637608784782 kJ/mol
  StdDev PE: 178.32850041505384
  
Integrator: LangevinIntegrator with Splitting="V1 V0 R R V0 V0 R R V0 V0 R O R V0 V0 R R V0 V0 R R V0 V1"...
  Wall time: 2373.489681s
  Mean   PE: -28842.059131768016 kJ/mol
  StdDev PE: 175.8657786915866
```

- Example #2
```
Running comparison with
 T =  5.0 ns
 h =  12.0 fs
 number of fast steps =  5
 direct force group =  0
 
Integrator: Default LangevinIntegrator...
  Wall time: 0.068689s
  Mean   PE: nan
  StdDev PE: nan

Integrator: LangevinMiddleIntegrator...
  Wall time: 0.017874s
  Mean   PE: nan
  StdDev PE: nan

Integrator: MTSLangevinIntegrator...
  Wall time: 391.621593s
  Mean   PE: -28668.655621398222 kJ/mol
  StdDev PE: 182.75565711677342

Integrator: LangevinIntegrator with Splitting="V R O R V"...
  Wall time: 0.003246s
  Mean   PE: nan
  StdDev PE: nan

Integrator: LangevinIntegrator with Splitting="V1 V0 R O R V0 V0 R O R V0 V0 R O R V0 V0 R O R V0 V0 R O R V0 V1"...
  Wall time: 481.455753s
  Mean   PE: -28779.301313448537 kJ/mol
  StdDev PE: 183.15921356462258

Integrator: LangevinIntegrator with Splitting="V1 V0 R R V0 V0 R R V0 V0 R O R V0 V0 R R V0 V0 R R V0 V1"...
  Wall time: 460.739472s
  Mean   PE: -28831.97468129074 kJ/mol
  StdDev PE: 176.49907441336393
```
