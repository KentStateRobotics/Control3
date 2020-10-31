import argparse
import logging
import sys
import KSRCore.networking as networking
import KSRCore.message as message
import KSRCore.config as config
import KSRCore.httpserver as httpserver
import KSRCore.logging

def main(argv=None):
    parser = argparse.ArgumentParser(description="Kent State Robotics Controler")
    parser.add_argument('-r', action='store_true', help='Is this a robot? Defaults to controller')
    parser.add_argument('-s', action='store_true', help='Is this the server? Defaults to client')
    parser.add_argument('-d', type=str, help='If this is the server, directory for the http server to serve from')
    parser.add_argument('-p', type=int, default=config.DEFAULT_PORT, help='Port to communicate over, default: {}'.format(config.DEFAULT_PORT))
    parser.add_argument('-a', type=str, help='Address to connect to host if discovery is not being used')
    parser.add_argument('-log_level', type=int, help="Logging filter level 10-debug, 20-default")
    parser.add_argument('-log_dir', type=str, help="File to store logs in")
    args = parser.parse_args(argv if argv else sys.argv[1:])

    router = None
    httpServer = None
    #Start services depending on whether this is the server or not
    if args.s:
        #Set the directory to serve the http server from
        if args.d is None:
            httpDir = 'KSRWebGUI/src/'
        else:
            httpDir = args.d
        router = networking.Server(args.p)
        httpServer = httpserver.HttpServer(router.queue, httpDir)
    else:
        router = networking.Client((args.a, args.p))

    #Init logging
    KSRCore.logging.initLogging(router.queue, args.log_level, args.log_dir)
    logger = logging.getLogger('Main')
    logger.info("Starting KSRC")

    #Start services depending on whether this is a robot or not
    if args.r:
        pass
        #serialConns = msgContainer()
        #leftMotors = motorController(0, serialConns, 0)
        #rightMotors = motorController(0, serialConns, 1)
    else:
        pass

    #Take command line input
    while True:
        try:
            command = input()
        except KeyboardInterrupt:
            command = 'e'
        if command == 'h':
            print('''List of commands:
                h - Help
                e - Exit program
                ''')
        elif command == 'e':
            logger.info("Keyboard close command received, closing program")
            router.stop()
            if httpServer:
                httpServer.stop()
            return