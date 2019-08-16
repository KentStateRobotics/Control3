import argparse

def main():
    print("control main")
    parser = argparse.ArgumentParser(description="Robot controler")
    parser.add_argument('-p', type=int, help='port to communicate over')
    parser.add_argument('-d', type=int, help='port to preform network discovery over')
    parser.add_argument('-a', type=str, help='address to connect to if not host')
    args = parser.parse_args()