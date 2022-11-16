import ctypes
import getpass
from krb5 import krb5

domain = 'ARM.LOC'

username = "kbtest"
password = getpass.getpass(prompt='Password: ')

principal = '%s@%s' % (username, domain)

try:
    krb5.get_init_creds_password(principal, password)
except BaseException as er:
    mess = str(er)
    if mess.find('Preauthentication failed') != -1:
        print('Preauthentication failed')
    elif mess.find('Password has expired') != -1:
        try:
            password_new = getpass.getpass(prompt='Password new: ')
            krb5.change_password(principal, password, password_new)
        except BaseException as e:
            #print(e)
            mess = str(e)
            if mess.find('Password does not meet complexity requirements') != -1:
                print('Password does not meet complexity requirements')
            elif mess.find('Password is already in password history') != -1:
                print('Password is already in password history.')
            else:
              print(mess)
    else:
      print(mess)
           
        
    
    
print('end prog')
    

    
exit

         