import ngrok
import subprocess

# #Get NGrok link
# listener = ngrok.forward("localhost:5000", authtoken='2YDEtECGkofUOsSrVOb8IUWSljw_oe5iPAeNZMpA3YSXyyXA')

# print(f"Ingress established at: {listener.url()}");

listener = 'https://8b42-2001-8a0-d945-fc00-1599-598b-b869-7c5d.ngrok-free.app'

#Fetch Available phones
command = 'twilio phone-numbers:list -o tsv --no-header --properties phoneNumber'
phones = subprocess.Popen(['powershell.exe', command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

# print(f'Twilio Response:\n{phones.stdout.read().decode().strip()}')

phones_list = [phones.stdout.read().decode().strip()]


#Update phone number webhook

for phone_number in phones_list:
    # twilio_webhook = f'twilio phone-numbers:update {{{phone_number}}} -l debug --sms-url {listener.url()}/sms'
    twilio_webhook = f'twilio phone-numbers:update {{{phone_number}}} -l debug --sms-url {listener}/sms'
    
    command = subprocess.run(['powershell.exe', twilio_webhook], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f'executing command: {command}')
    


