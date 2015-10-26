#!/bin/sh
# To use an OpenStack cloud you need to authenticate against the Identity
# service named keystone, which returns a **Token** and **Service Catalog**.
# The catalog contains the endpoints for all services the user/tenant has
# access to - such as Compute, Image Service, Identity, Object Storage, Block
# Storage, and Networking (code-named nova, glance, keystone, swift,
# cinder, and neutron).
#
# *NOTE*: Using the 2.0 *Identity API* does not necessarily mean any other
# OpenStack API is version 2.0. For example, your cloud provider may implement
# Image API v1.1, Block Storage API v2, and Compute API v2.0. OS_AUTH_URL is
# only for the Identity API served through keystone.
export OS_AUTH_URL=http://smog.uppmax.uu.se:5000/v2.0

# With the addition of Keystone we have standardized on the term **tenant**
# as the entity that owns the resources.
export OS_TENANT_ID=3c9d997982e04c6db0e02b82fa18fdd8
export OS_TENANT_NAME="ACC-Course"
export OS_PROJECT_NAME="ACC-Course"

# In addition to the owning entity (tenant), OpenStack stores the entity
# performing the action as the **user**.

echo "Please enter OpenStack Username: [ex: 'adru8091']"
read OS_USERNAMEX
echo "You entered: $OS_USERNAMEX"
echo "************************************************"
export OS_USERNAME=$OS_USERNAMEX


# With Keystone you pass the keystone password.
echo "Please enter your OpenStack Password: "
read -sr OS_PASSWORD_INPUT
export OS_PASSWORD=$OS_PASSWORD_INPUT
echo "************************************************"



echo "Please enter ssh keypair name: [ex: 'l3_key_r']"
read KP_NAME_X
echo "You entered: $KP_NAME_X"
echo "************************************************"
export KP_NAME=$KP_NAME_X

echo "Please enter the maximum number of workers needed for your cluster [ex: '3']"
read NR_WORKERS_X
echo "You entered: $NR_WORKERS_X"
echo "************************************************"
export NR_WORKERS=$NR_WORKERS_X


echo "Please enter Absolute path to PRIVATE ssh key: [ex: '/Users/adamruul/datormoln/cloud.key']"
read PRIV_KEY_X
echo "You entered: $PRIV_KEY_X"
echo "************************************************"
export PRIV_KEY=$PRIV_KEY_X

echo "Please enter Absolute path to PUBLIC ssh key: [ex: '/Users/adamruul/datormoln/cloud.key.pub']"
read PUB_KEY_X
echo "You entered: $PUB_KEY_X"
echo "************************************************"
export PUB_KEY=$PUB_KEY_X



# If your configuration has multiple regions, we set that information here.
# OS_REGION_NAME is optional and only valid in certain environments.
export OS_REGION_NAME="regionOne"
# Don't leave a blank variable, unset it if it was empty
if [ -z "$OS_REGION_NAME" ]; then unset OS_REGION_NAME; fi



echo "**********************************************"
echo "Setup finished!"
echo "**********************************************"

