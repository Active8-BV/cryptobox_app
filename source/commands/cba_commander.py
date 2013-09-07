# coding=utf-8
"""
python version
"""
import sys
import time
import threading


class XMLRPCThread(threading.Thread):
    """
    XMLRPCThread
    """

    def run(self):
        """
        run
        """
        from SimpleXMLRPCServer import SimpleXMLRPCServer
        from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler

        #noinspection PyClassicStyleClass
        class RequestHandler(SimpleXMLRPCRequestHandler):
            """
            RequestHandler
            """
            rpc_paths = ('/RPC2',)

        # Create server
        server = SimpleXMLRPCServer(("localhost", 8654), requestHandler=RequestHandler)
        server.register_introspection_functions()

        # Register a function under a different name
        def adder_function(x, y):
            """
            adder_function
            :param y:
            :param x:
            """
            for i in range(0, 3):
                sys.stdout.write("adding: " + str(x) + " and " + str(y))
                sys.stdout.flush()


            return x + y

        server.register_function(adder_function, 'add')
        server.serve_forever()


xx = XMLRPCThread()


xx.start()

#sys.stdout.write(sys.version.split("\n")[0] + " " + str(datetime.datetime.now().time()) + "\n")
