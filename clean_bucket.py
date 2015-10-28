import swiftclient.client
import os

config = {'user':os.environ['OS_USERNAME'], 
          'key':os.environ['OS_PASSWORD'],
          'tenant_name':os.environ['OS_TENANT_NAME'],
          'authurl':os.environ['OS_AUTH_URL']}

conn = swiftclient.client.Connection(auth_version=2, **config)

bucket_name = "gr1_res"

# Clean up container in Swift
(r, ol) = conn.get_container(bucket_name)
# DELETE ALL OBJECTS
for obj in ol:
    conn.delete_object(bucket_name, obj['name'])
print "All Objects deleted..."
