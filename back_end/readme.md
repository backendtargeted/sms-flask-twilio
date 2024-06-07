Notes:

_Backend_

- Check enviroment variables
- Modify the send message module to take the leads from DB, filtering DNC
- Create the DNC endpoint
- Create boot script (NGROK, twilio update, start Flask, start node)
- Divide the sending of different numbers in different days
- Create Auto responses

_FrontEnd_

- Display the sent and received messages real time
- Create Auto responses

Initial Templates

Is this {{first_name}}? I hope I have the correct number!
Hi {{first_name}}, how is your day going? Hope I have the correct number.
Hi, I've been trying to reach you, is now a bad time?
Hey there! Is this {{first_name}}?
Hi {{first_name}} are you still at {{address}}?
Hey {{first_name}}, is now a bad time to talk?
Hey {{first_name}}, did you receive my call about {{address}}?
Is this {{first_name}} {{last_name}} at {{address}}?
Are you the manager of {{address}}?
Do you have any properties in {{city}} you aren't happy with?
I am looking for whoever is responsible for {{address}}. Is this the correct number?
Hello, how much work do you think {{address}} needs?
Hello, is this {{first_name}} {{last_name}}?
Can you help me find who to speak to in regards to {{address}}?
Roses are red, violets are purple. I want to pay $$ for {{address}}. What say you?
Is {{first_name}} {{last_name}} available?

Responses

This is David Baldwin and I am interested in purchasing {{address}}. Are you looking to sell?
Is the property tenant or owner occupied? If rented, how much is the rent? How would you rate the condition? Perfect, Good, Ugly or Scary?
I can give you an offer fairly quickly if we can go through a couple of questions. Is that ok?
Can you tell me a little bit about the property so I can determine my offer?
I had pulled a list of absentee owners and skip traced it to see if those owners may want to sell that property.
