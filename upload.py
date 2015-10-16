import os
import glob
import swiftclient.client


def uploadf():
    config = {'user':os.environ['OS_USERNAME'],
          'key':os.environ['OS_PASSWORD'],
          'tenant_name':os.environ['OS_TENANT_NAME'],
          'authurl':os.environ['OS_AUTH_URL']}

    conn = swiftclient.client.Connection(auth_version=2, **config)
    angle ="0"
    bucket_name = "G1_Project_result"
    (response, bucket_list) = conn.get_account()
    for bucket in bucket_list:
        if bucket['name'] == bucket_name:
            print "*** Found bucket! ***"
	    break
    else:
        conn.put_container(bucket_name)
    	print "*** Creating bucket ***"



    directory="/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/results/*"
    dd = "/home/ubuntu/ACC_Project/naca_airfoil/navier_stokes_solver/results"
    result_folder = sorted(glob.glob(directory), key=os.path.getmtime)[::-1]
    for fil in result_folder:
        filename, file_extension = os.path.splitext(str(fil))
        xw=filename.replace(dd+"/","")
        filenamee = xw+str(file_extension)
	print "*** Uploading: '" +str(fil)+"' ***"
        with open(fil, 'r') as res_file:
            conn.put_object(bucket_name, str(angle)+"degrees/"+str(filenamee),
                            contents= res_file.read(),
                            content_type='text/plain')

    (response, obj_list) = conn.get_container(bucket_name)
    print "================ v OBJECT NAMES: v ================"
    for obj in obj_list:
        print obj['name']

uploadf()
