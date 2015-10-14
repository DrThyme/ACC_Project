#!/bin/bash

# Usage: ./convert_to_xml.sh <directory where .msh is located>
# eg: /home/ubuntu/ACC_Project/naca_airfoil/msh


cd $1
for f in *; do 
    dolfin-convert --output xml "$f" "${f%.*}.xml"
done

for x in *.xml; do 
    mv "$x" ../xml
done

