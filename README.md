# hangouts_client
Class for sending/receiving messages on Google Hangouts (auth via OAUTH).

##### Before Use
1. Go to [Google APIs](https://console.developers.google.com/apis/) and generate secret client ID/password.
2. Fill in values in `config.ini`

##### Usage
e.g. Setup Hangouts bot instance, connect and send message:
```
config_file = '/path/to/config.ini'
message = 'Hello world!'
hangouts = HangoutsClient(config_file, message)
if hangouts.connect(address=('talk.google.com', 5222), reattempt=True, use_tls=True):
    hangouts.process(block=True)
```
![](https://thumbs.gfycat.com/SnoopyMenacingIsabellinewheatear-size_restricted.gif)
