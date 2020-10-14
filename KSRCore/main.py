import argparse
import KSRCore.networking as networking
import KSRCore.message as message
import KSRCore.config as config

def main():
    parser = argparse.ArgumentParser(description="Kent State Robotics Controler")
    parser.add_argument('-r', metavar='ROBOT', help='Is this a robot? Defaults to controller')
    parser.add_argument('-s', metavar='Server', help='Is this a server? Defaults to client')
    parser.add_argument('-p', type=int, metavar='PORT', default=networking.DEFAULT_PORT, help='Port to communicate over, default: {}'.format(networking.DEFAULT_PORT))
    parser.add_argument('-a', type=str, metavar='ADDRESS', help='Address to connect to host if discovery is not being used')
    parser.add_argument('-l', type=str, metavar='LOGFILE', help="File to store logs in")
    args = parser.parse_args()

    config.initLogging(args.l)

    if args.s is None:
        router = networking.Server(args.p)
    else:
        router = networking.Client((args.a, args.p))

    if args.r:
        serialConns = msgContainer()
        leftMotors = motorController(0, serialConns, 0)
        rightMotors = motorController(0, serialConns, 1)

    while True:
        try:
            command = input()
        except KeyboardInterrupt:
            command = 'e'
        if command == 'e':
            print("Closing")
            networkCore.close()
            return