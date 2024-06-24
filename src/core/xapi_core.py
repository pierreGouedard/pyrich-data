import json
import socket
import time
import ssl
from threading import Thread

context = ssl.create_default_context()

# API inter-command timeout (in ms)
API_SEND_TIMEOUT = 100

# max connection tries
API_MAX_CONN_TRIES = 3


class TransactionSide(object):
    BUY = 0
    SELL = 1
    BUY_LIMIT = 2
    SELL_LIMIT = 3
    BUY_STOP = 4
    SELL_STOP = 5


class TransactionType(object):
    ORDER_OPEN = 0
    ORDER_CLOSE = 2
    ORDER_MODIFY = 3
    ORDER_DELETE = 4


class JsonSocket(object):

    def __init__(self, address, port, logger):

        # Set up socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.context = ssl.create_default_context()
        self.socket = self.context.wrap_socket(sock, server_hostname=address)

        # set other properties
        self.logger = logger
        self.conn = self.socket
        self._timeout = None
        self._address = address
        self._port = port
        self._decoder = json.JSONDecoder()
        self._receivedData = ''

    def connect(self):
        for i in range(API_MAX_CONN_TRIES):
            try:
                self.socket.connect((self.address, self.port))
            except socket.error as msg:
                self.logger.error("SockThread Error: %s" % msg)
                time.sleep(0.25);
                continue
            self.logger.info("Socket connected")
            return True
        return False

    def _sendObj(self, obj):
        msg = json.dumps(obj)
        self._waitingSend(msg)

    def _waitingSend(self, msg):
        if self.socket:
            sent = 0
            msg = msg.encode('utf-8')
            while sent < len(msg):
                sent += self.conn.send(msg[sent:])
                time.sleep(API_SEND_TIMEOUT/1000)

    def _read(self, bytesSize=4096):
        if not self.socket:
            raise RuntimeError("socket connection broken")
        while True:
            char = self.conn.recv(bytesSize).decode('utf-8', errors='ignore')
            self._receivedData += char
            try:
                (resp, size) = self._decoder.raw_decode(self._receivedData)
                if size == len(self._receivedData):
                    self._receivedData = ''
                    break
                elif size < len(self._receivedData):
                    self._receivedData = self._receivedData[size:].strip()
                    break
            except ValueError as e:
                continue
        return resp

    def _readObj(self):
        msg = self._read()
        return msg

    def close(self):
        self.logger.debug("Closing socket")
        self._closeSocket()
        if self.socket is not self.conn:
            self.logger.debug("Closing connection socket")
            self._closeConnection()

    def _closeSocket(self):
        self.socket.close()

    def _closeConnection(self):
        self.conn.close()

    def _get_timeout(self):
        return self._timeout

    def _set_timeout(self, timeout):
        self._timeout = timeout
        self.socket.settimeout(timeout)

    def _get_address(self):
        return self._address

    def _set_address(self, address):
        pass

    def _get_port(self):
        return self._port

    def _set_port(self, port):
        pass


    timeout = property(_get_timeout, _set_timeout, doc='Get/set the socket timeout')
    address = property(_get_address, _set_address, doc='read only property socket address')
    port = property(_get_port, _set_port, doc='read only property socket port')

    
class APIClient(JsonSocket):
    def __init__(self, address, port, logger):
        super(APIClient, self).__init__(address, port, logger)
        if not self.connect():
            raise Exception(
                "Cannot connect to " + address + ":" + str(port) +
                " after " + str(API_MAX_CONN_TRIES) + " retries"
            )

    def execute(self, dictionary):
        self._sendObj(dictionary)
        return self._readObj()    

    def disconnect(self):
        self.close()
        
    def commandExecute(self, commandName, arguments=None):
        return self.execute(baseCommand(commandName, arguments))


class APIStreamClient(JsonSocket):
    def __init__(
            self, address, port, logger, ssId=None
    ):
        super(APIStreamClient, self).__init__(address, port, logger)
        self._ssId = ssId
        
        if not self.connect():
            raise Exception(
                "Cannot connect to streaming on " + address + ":" + str(port) +
                " after " + str(API_MAX_CONN_TRIES) + " retries"
            )

        self.data = []
        self._running = True
        self._t = Thread(target=self._readStream, args=())
        self._t.daemon = True
        self._t.start()

    def _readStream(self):
        while self._running:
            msg = self._readObj()
            self.data.append(msg)

    def disconnect(self):
        self._running = False
        self._t.join()
        self.close()

    def execute(self, dictionary):
        self._sendObj(dictionary)

    def subscribePrice(self, symbol):
        self.execute(dict(command='getTickPrices', symbol=symbol, streamSessionId=self._ssId))
        
    def subscribePrices(self, symbols):
        for symbolX in symbols:
            self.subscribePrice(symbolX)
    
    def subscribeTrades(self):
        self.execute(dict(command='getTrades', streamSessionId=self._ssId))
        
    def subscribeBalance(self):
        self.execute(dict(command='getBalance', streamSessionId=self._ssId))

    def subscribeTradeStatus(self):
        self.execute(dict(command='getTradeStatus', streamSessionId=self._ssId))

    def subscribeProfits(self):
        self.execute(dict(command='getProfits', streamSessionId=self._ssId))

    def subscribeNews(self):
        self.execute(dict(command='getNews', streamSessionId=self._ssId))

    def unsubscribePrice(self, symbol):
        self.execute(dict(command='stopTickPrices', symbol=symbol, streamSessionId=self._ssId))
        
    def unsubscribePrices(self, symbols):
        for symbolX in symbols:
            self.unsubscribePrice(symbolX)
    
    def unsubscribeTrades(self):
        self.execute(dict(command='stopTrades', streamSessionId=self._ssId))
        
    def unsubscribeBalance(self):
        self.execute(dict(command='stopBalance', streamSessionId=self._ssId))

    def unsubscribeTradeStatus(self):
        self.execute(dict(command='stopTradeStatus', streamSessionId=self._ssId))

    def unsubscribeProfits(self):
        self.execute(dict(command='stopProfits', streamSessionId=self._ssId))

    def unsubscribeNews(self):
        self.execute(dict(command='stopNews', streamSessionId=self._ssId))


def baseCommand(commandName, arguments=None):
    if arguments==None:
        arguments = dict()
    return dict([('command', commandName), ('arguments', arguments)])


def loginCommand(userId, password, appName=''):
    return baseCommand('login', dict(userId=userId, password=password, appName=appName))
