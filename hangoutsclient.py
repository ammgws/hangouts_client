# Standard library
import logging
import ssl
# import threading
from configparser import ConfigParser
# Third party imports
from google_auth import GoogleAuth
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from sleekxmpp.xmlstream import cert


class HangoutsClient(ClientXMPP):
    """
    Class for sending messages via Google Hangouts.
    """

    def __init__(self, config_filepath):
        # Read in config values
        self.config = ConfigParser()
        self.config.read(config_filepath)
        self.config_filepath = config_filepath
        logging.debug('Using config file: %s', config_filepath)

        # Get Hangouts OAUTH info from config file
        self.client_id = self.config.get('Hangouts', 'client_id')
        self.client_secret = self.config.get('Hangouts', 'client_secret')
        self.refresh_token = self.config.get('Hangouts', 'refresh_token')

        # Generate access token
        scope = ('https://www.googleapis.com/auth/googletalk '
                 'https://www.googleapis.com/auth/userinfo.email')
        self.oauth = GoogleAuth(self.config_filepath, scope, service='Hangouts')
        self.oauth.authenticate()

        # Get email address for Hangouts login
        hangouts_login_email = self.oauth.get_email()
        logging.debug('Going to login using: %s', hangouts_login_email)

        # Setup new SleekXMPP client to connect to Hangouts.
        # Not passing in actual password since using OAUTH2 to login
        super().__init__(jid=hangouts_login_email, password=None, sasl_mech='X-OAUTH2')
        self.auto_reconnect = True  # Restart stream in the event of an error
        self.reconnect_max_delay = 1  # Max time to delay between reconnection attempts (secs)
        self.use_ipv6 = False  # Not supported by Hangouts

        # TODO: roster ready notification
        # Used to indicate when roster has been fetched and thus messaging can proceed.
        #self.ready = threading.Event()

        # Register XMPP plugins (order does not matter.)
        # TODO: remove unused plugins
        self.register_plugin('xep_0030')  # Service Discovery
        self.register_plugin('xep_0004')  # Data Forms
        self.register_plugin('xep_0199')  # XMPP Ping

        # The session_start event will be triggered when the XMPP client
        # establishes its connection with the server and the XML streams are
        # ready for use. We want to listen for this event so that we can
        # initialize our roster. Need threaded=True so that the session_start
        # handler doesn't block event processing while we wait for presence
        # stanzas to arrive.
        self.add_event_handler("session_start", self.start, threaded=True)

        # Triggered whenever a 'connected' XMPP event is stanza is received,
        # in particular when connection to XMPP server is established.
        # Fetches a new access token and updates the class' access_token value.
        self.add_event_handler('connected', self.reconnect_workaround)

        # When using a Google Apps custom domain, the certificate does not
        # contain the custom domain, just the Hangouts server name. So we will
        # need to process invalid certificates ourselves and check that it
        # really is from Google.
        self.add_event_handler("ssl_invalid_cert", self.invalid_cert)

    def reconnect_workaround(self, event):  # pylint: disable=W0613
        """ Workaround for SleekXMPP reconnect.
        If a reconnect is attempted after access token is expired, auth fails
        and the client is stopped. Get around this by updating the access
        token whenever the client establishes a connection to the server.
        """
        self.oauth.authenticate()
        self.credentials['access_token'] = self.oauth.access_token

    def invalid_cert(self, pem_cert):
        """ Verify that certificate originates from Google. """
        der_cert = ssl.PEM_cert_to_DER_cert(pem_cert)
        try:
            cert.verify('talk.google.com', der_cert)
            logging.debug("Found Hangouts certificate")
        except cert.CertificateError as err:
            logging.error(err)
            self.disconnect(send_close=False)

    def start(self, event):  # pylint: disable=W0613
        """
        Process the session_start event.

        Broadcast initial presence stanza and request the roster.

        Args:
            event -- An empty dictionary. The session_start event does not
                     provide any additional data.
        """

        # Broadcast initial presence stanza
        self.send_presence()

        # Request the roster
        try:
            self.get_roster()
        except IqError as err:
            logging.error('There was an error getting the roster')
            logging.error(err.iq['error']['condition'])
            self.disconnect()
        except IqTimeout:
            logging.error('Server is taking too long to respond')
            self.disconnect(send_close=False)

        # TODO: roster ready notification
        # while len(self.client_roster) < 2:
        #     pass
        # self.ready.set()

    def in_roster(self, recipient):
        # TODO: come up with a cleaner way for this and `send_to` function
        if '@public.talk.google.com' in recipient:
            if recipient in self.client_roster:
                return True, recipient
        else:
            # If recipient is given by name, we need to check each client's name field
            # Note this is not guaranteed to be unique!
            for client in self.client_roster:
                if self.client_roster[client]['name'] == recipient:
                    return True, client

        return False, recipient

    def send_to(self, recipient_list, message):
        # Send message to specified user(s)
        logging.info('Message to send: %s', message)
        for recipient in recipient_list:
            check = self.in_roster(recipient)
            if check[0] is True:
                logging.info('Sending to: %s (%s)', recipient, check[1])
                self.send_message(mto=check[1], mbody=message, mtype='chat')
            else:
                logging.info('Recipient %s not found in roster', recipient)

    def send_to_all(self, message):
        # Send message to each user found in the roster
        logging.info('Message to send: %s', message)
        num_users = 0
        for recipient in self.client_roster:
            if recipient != self.boundjid:
                num_users += 1
                logging.info('Sending to: %s (%s)', self.client_roster[recipient]['name'], recipient)
                self.send_message(mto=recipient, mbody=message, mtype='chat')

    def connect(self):
        return super().connect(address=('talk.google.com', 5222),
                               reattempt=True, use_tls=True)


