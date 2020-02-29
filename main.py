import sys
from stock import Stock_bot

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: ./Stock_bot TOKEN")
        exit(0)

    bot = Stock_bot(sys.argv[1])
