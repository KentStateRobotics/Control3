import argparse
import networking
import networking.message

def main():
    parser = argparse.ArgumentParser(description="Robot controler")
    parser.add_argument('name', type=str, help='id used over network, first {} characters must be unique'.format(networking.message.Message.NAME_LENGTH))
    parser.add_argument('-p', type=int, metavar='PORT', default=networking.DEFAULT_PORT, help='port to communicate over, default: {}'.format(networking.DEFAULT_PORT))
    parser.add_argument('-d', type=int, metavar='DISCOVERY PORT', default=networking.DEFAULT_DISCOVERY_PORT, help='port to preform network discovery over, default: {}'.format(networking.DEFAULT_DISCOVERY_PORT))
    parser.add_argument('-a', type=str, metavar='HOST', help='address to connect to host, or host name if discovery is being used')
    args = parser.parse_args()

    if not args.d is None and not args.a is None:
        networkCore = networking.Client(args.name, args.p, discoveryPort=args.d, discoveryId=args.a)
    elif not args.a is None:
        networkCore = networking.Client(args.name, args.p, args.a)
    else:
        pass

    while True:
        try:
            command = input()
        except KeyboardInterrupt:
            command = 'e'
        if command == 'e':
            print("Closing")
            networkCore.close()
            return