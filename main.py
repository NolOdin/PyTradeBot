# main.py
import argparse
from trade_engine import TradeEngine
from backtest import Backtester
from optimizer import StrategyOptimizer
from monitor import Monitor
import signal
import sys

def signal_handler(sig, frame):
    print('\nБот остановлен.')
    sys.exit(0)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--backtest', action='store_true')
    parser.add_argument('--optimize', action='store_true')
    parser.add_argument('--days', type=int, default=60)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)

    if args.optimize:
        StrategyOptimizer().run_grid_search()
    elif args.backtest:
        Backtester(days=args.days).run()
    else:
        Monitor.log_trade('START', 0)
        engine = TradeEngine()
        try:
            while True:
                engine.run_cycle()
        except KeyboardInterrupt:
            Monitor.log_trade('STOP', 0)
