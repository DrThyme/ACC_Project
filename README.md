# ACC Project: Airfoil


> A group project for the Applied Cloud Computing course at Uppsala University

Using a [2D NavierStokes solver](https://github.com/TDB-UU/naca_airfoil) based on the Finite Element Method (FEM), and
implemented using the open source framework [FEniCS/Dolfin](http://fenicsproject.org/) together
with the Mesh generation software [Gmsh](http://geuz.org/gmsh/), We are developing a cloudbased
solution and service for conducting experiments to assess the influence of the angle of attack on the lift
force (for different values of the other inputs to the program).



  
## Getting Started

#### Dowload / Clone
Clone the repo using Git:

```bash
git clone https://github.com/DrThyme/ACC_Project.git
```

> Alternatively you can [download as .zip](https://github.com/DrThyme/ACC_Project/archive/master.zip)!

#### USAGE

##### Run the setup script
```bash
source setup.sh
# Enter your credentials etc.
```
> This requires that you have an account on the SMOG cloud (regionOne)

##### Create your cluster (Note: this might take a while)
```bash
python cw2.py
# URL to flower dashboard and Web UI will be printed in the terminal.
```
> This requires that you have an account on the SMOG cloud (regionOne)

##### Run some calculations, using the Web-UI

#### Known Errors and limitations:
Running multiple sequential calculations from the Web-UI  may cause
the task queue to crash.

Some parameters are set and can not be changed in the current
implementation.




## Modifying the code

##### The worker tasks can be defined in the file w_worker_tasks.py 
```Python
@celery.task
def calc_lift_force(ang):
#....
# Your function
#....
```
##### And be called in utils.py 
```Python
@apps.route('/result')
def start():
maxAngle = request.args['maxAngle']
minAngle = request.args['minAngle']
numSamples = request.args['numSamples']
#....
# Do Stuff with input from the form in airfoil.html
#....
tasks = [calc_lift_force.s(angle) for angle in a_list]
task_group = group(tasks)
group_result = task_group()
while (group_result.ready() == False):
    time.sleep(2)
res = group_result.get()
#....
# Return stuff
#....
```

## Authors
Group 1:
* Andreas Gäwerth
* Tim Josefsson
* Adam Ruul


## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -m 'Added my new feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request!
