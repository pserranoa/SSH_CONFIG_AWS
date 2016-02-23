#!/usr/bin/python

import boto3
import os

ec2 = boto3.resource('ec2')

#ficheros de salida
CurPath=os.getcwd()

salida =CurPath+"/config_ssh"
if os.path.isfile(salida):
	try:
		os.remove(salida)
	except OSError:
		pass

def default_username( image_name ):
	if image_name.startswith('CentOS'):
		luser = "centos"
	else:
  		if image_name.startswith('ubuntu'):
  			luser = "ubuntu"
		else:
			if image_name.startswith('Fedora'):
	  			luser = "ec2-user"
			else:
				if image_name.startswith('amzn'):
		  			luser = "ec2-user"
				else:
					if image_name.startswith('debian'):
						luser = "admin"
					else:
						if image_name.startswith('OmniOS'):
							luser = "root"
						else:
							if image_name.startswith('FreeBDS'):
								luser = "ec2-user"
							else:
								if image_name.startswith('SUSE'):
									luser = "root"
								else:
									if image_name.startswith('RHEL'):
										luser = "ec2-user"
									else:
										luser="ec2-user"
	return luser;

instances=ec2.instances.all()
target=open(salida, 'w')
target.write("#automatic created by secdevops")
list_keys=[]
tinstances=0
for instance in instances:
	instance_id = instance.id
	state = instance.state
	current_state = state.get('Name')
	if current_state != "terminated":
        	print("[%s] - %s" %(instance_id,current_state))
                tinstances+=1
		vpc_id = instance.vpc_id
		tagsinstance = instance.tags
		ssh_key =  instance.key_name
                if ssh_key not in list_keys:
     			list_keys.append(ssh_key) 	
		ip = instance.private_ip_address
		ip_public = instance.public_ip_address
		try:
			ami = ec2.Image(instance.image_id)
			image_name = ami.name
		except AttributeError:
			image_name = "X"
		for tag in tagsinstance:
			if tag['Key'] == 'Name':
				try:
					InstanceName = tag['Value']
				except ValueError:
					InstanceName=None
		Filters_route = [{'Name':'vpc-id', 'Values':[vpc_id]}]
		vpc_routes = ec2.route_tables.filter(Filters=Filters_route)
		for route in vpc_routes:
			is_gateway = False
			for item in route.routes:
				try:
					route_instance_id = item.get('InstanceId')
				except ValueError:
					route_instance_id=None
				if route_instance_id != None:
					if route_instance_id == instance_id:
						is_gateway = True
					gateway = ec2.Instance(route_instance_id)
					gatewaytags = gateway.tags
					for tag in gatewaytags:
						if tag['Key'] == 'Name':
							try:
								GatewayName = tag['Value']
							except ValueError:
								GatewayName=None
					break
	#write file
		target.write("\n")
		target.write("host %s\n" % (InstanceName))
		if is_gateway == False:
			target.write("	hostname %s\n" % (ip))
			target.write("	ProxyCommand ssh -W %h:%p")
			target.write(" %s\n" %(GatewayName))
			target.write("	StrictHostKeyChecking no\n")
			target.write("	ControlMaster auto\n")
			target.write("	ControlPath ~/.ssh/tmp/%h_%p_%r\n")
		else:
			target.write("	hostname %s\n" % (ip_public))
		target.write("	User %s\n" %(default_username (image_name)))
		target.write("	IdentityFile    ~/.ssh/%s.pem\n" % (ssh_key))
target.close()
print("\n\n")
print("Total number of instances created on config: %s\n" %(tinstances))
print("You will need the follogint keys on your home .ssh path:\n")
for needkey in list_keys:
    print("- %s.pem" % (needkey))
