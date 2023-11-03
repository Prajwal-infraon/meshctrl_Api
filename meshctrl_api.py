import subprocess


# Specify the path to your JavaScript file
js_file = "meshctrl.js"

# try:
    
# result = subprocess.run(["node", js_file],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
# print("JavaScript execution result:")
# print(result.stdout)
# print("-------------------------------------------------------------------------------------------------------")

#condition to create groups
def adddevicegroup(group_name):
    #action_cmd=input("enter Action to be performe ")
    command= f'node meshctrl adddevicegroup --name {group_name}'
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        print("Command execution result:")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running the command:")
        print(e.stderr)
    
    
#to perform single_action
def generalinfo(action):   
    #action=input("\n>>>>>>>>>>>>>>>>>>>>>>>>Enter the Action<<<<<<<<<<<<<<<<<<<<<<<<\nconfig\t,indexagenterrorlog\t,serverinfo\t,userinfo\t,listusers\t,listusersessions\t,listusergroups\t,listdevicegroups\t,listdevices\t,listevents\t,logintokens\t,listusersofdevicegroup\t,deviceinfo\t,removedevice\t\n")
    command = f'node meshctrl {action} --json'
    # print("------------------------------------------------------------------------------------------------------------")
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running the command:")
        print(e.stderr)

#help menu displays all the commands
def help(help_cmd):   
    #help=input("enter the above Command to know the syntax \n")
    command = f'node meshctrl help {help_cmd} --json'
    # print("------------------------------------------------------------------------------------------------------------")
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        #print("Command execution result:")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running the command:")
        print(e.stderr)

#user can enter the manual command to execute     
def random_cmd(rand):
    # rand=input("enter the command according to the syntax\n")
    command= f'node {rand} --json'
    try:
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        # print("Command execution result:")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("Error running the command:")
        print(e.stderr)
        
def menu():
    result = subprocess.run(["node", js_file],stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    return result.stdout
        
# calling function using while loop
def check_function(): 
    while (True):
        value=input("Choose one of the following operator:\n1.addcevicegroup\n2.generalinfo\n3.random_cmd\n4.help\n0.exit()\n")
        match value:
            case '1':
                adddevicegroup()
                
            case '2':
                generalinfo()
        
            case '3':
                random_cmd()
                    
            case '4':
                help()
                
            case '5':
                menu()
                
            case '0':
                break
    
# except subprocess.CalledProcessError as e:
#     print("Error running JavaScript:")
#     print(e.stderr)
