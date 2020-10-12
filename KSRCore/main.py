import argparse
import KSRCore.networking as networking
import KSRCore.message as message
import KSRCore.config as config

def main():
    parser = argparse.ArgumentParser(description="Kent State Robotics Controler")
    parser.add_argument('-r', type=bool, metavar='IS ROBOT', default=False, help='Is this a robot? (not controller)')
    parser.add_argument('-p', type=int, metavar='PORT', default=networking.DEFAULT_PORT, help='port to communicate over, default: {}'.format(networking.DEFAULT_PORT))
    parser.add_argument('-a', type=str, metavar='HOST', help='address to connect to host if discovery is not being used')
    parser.add_argument('-d', type=int, metavar='DISCOVERY PORT', default=networking.DEFAULT_DISCOVERY_PORT, help='port to preform network discovery over, default: {}'.format(networking.DEFAULT_DISCOVERY_PORT))
    parser.add_argument('-i', type=str, metavar='DISCOVERY HOST', default="host", help='host name if discovery is being used')
    parser.add_argument('-l', type=str, metavar='LOG FILE', help="File to store logs in")
    args = parser.parse_args()

    config.initLogging(args.l)

    if args.a is None:
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