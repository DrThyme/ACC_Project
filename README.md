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
git clone --bare https://github.com/DrThyme/ACC_Project.git
```

> Alternatively you can [download as .zip](https://github.com/DrThyme/ACC_Project/archive/master.zip)!

#### USAGE

Create instance based on image 'PROJECT1_BASE' and ssh into it.

The 'PROJECT1_BASE'-image has the following installed:
* fenics
* git
* pip
* rabbitmq-server
* gmsh
* celery
* Flask


```bash
cd ACC_Project/naca_airfoil/
./run.sh 0 30 10 200 3
cd ..
./convert_to_xml.sh /home/ubuntu/ACC_Project/naca_airfoil/msh
cd naca_airfoil/navier_stokes_solver/
export LC_ALL=C
./airfoil  10 0.0001 10. 1 ../xml/r0a0n200.xml
```
> In your userdata-file...Clone this repo

## Examples

##### Get the mouse location and move it. 
```JavaScript
var ex = require("example");

//Get the mouse position, returns an object with x and y. 
var mouse=ex.getMousePos();
console.log("Mouse is at x:" + mouse.x + " y:" + mouse.y);

//Move the mouse down by 100 pixels.
robot.moveMouse(mouse.x,mouse.y+100);

//Left click!
robot.mouseClick();
```

##### Run some FizzBuzz:
```JavaScript
for (var i=1; i <= 20; i++)
{
    if (i % 15 == 0)
        console.log("FizzBuzz");
    else if (i % 3 == 0)
        console.log("Fizz");
    else if (i % 5 == 0)
        console.log("Buzz");
    else
        console.log(i);
}
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
