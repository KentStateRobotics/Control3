import sys
import networking


def main(args):
    isServer = len(args) > 1 and args[1] == 's'
    if isServer:
        print("starting server")
        core = networking.NetworkCore("server", 4242)
    else:
        print("starting client")
        core = networking.NetworkCore("client", 4242, '127.0.0.1')

    try:
        while True:
            toSend = input()
            if toSend == "q":
                core.destory()
                return
            else:
                if isServer:
                    core.send(toSend, "client")
                else:
                    core.send(toSend, "server")
    except KeyboardInterrupt as e:
        print(e)
        core.destory()

if __name__ == "__main__":
    main(sys.argv)
