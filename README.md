# hangouts_client
Class for sending/receiving messages on Google Hangouts (auth via OAUTH).

##### Before Use
1. Go to [Google APIs](https://console.developers.google.com/apis/) and generate secret client ID/password.
2. Fill in values in `config.ini`

##### Usage
e.g. Setup Hangouts bot instance, connect and send message:
```
config_file = '/path/to/config.ini'
hangouts = HangoutsClient(config_file)
if hangouts.connect():
    hangouts.process(block=False)
else:
    print('Failed to connect to Hangouts!')
time.sleep(5)  # give time for roster to be fetched
# Sends to all Hngouts cDontacts found online: 
hangouts.send_to_all('Hope you enjoyed my stories.')
# Send to Hangouts user specified by full name:
hangouts.send_to(['Itiot Anton', ], 'Hey when is your wedding?')
# Send to Hangouts user specified by :
hangouts.send_to(['ahf9v8qah4wfnasd@public.talk.google.com', ], 'Wake up')
hangouts.disconnect(wait=True)
```
Outdated gif:
![](https://thumbs.gfycat.com/SnoopyMenacingIsabellinewheatear-size_restricted.gif)
