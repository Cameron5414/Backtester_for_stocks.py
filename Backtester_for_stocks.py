# 1. IMPORTS
import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import json
import shutil
from enum import Enum
import time  # Add this
import threading  # Add this
import queue  # Add this
import atexit  # Add this
import traceback

# 2. PAGE CONFIGURATION
st.set_page_config(
    page_title="ASX Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Add custom title with styling
st.markdown("""
    <h1 style='text-align: center; margin-bottom: 30px; color: #3498db;'>
        📈 ASX Trading Dashboard
    </h1>
""", unsafe_allow_html=True)


# 3. CONSTANTS AND ENUMS
class Strategy(Enum):
    SWING = "Gann Swing"
    TRENDLINE = "Trendline"

# Create a queue for price updates
price_update_queue = queue.Queue()

def test_yfinance_connection(stock='CBA'):
    try:
        print(f"Testing connection for {stock}")
        ticker = yf.Ticker(f"{stock}.AX")
        data = ticker.history(period="1d")
        print(f"Successfully retrieved data for {stock}")
        print(data)
        return True
    except Exception as e:
        print(f"Error retrieving stock data: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

test_yfinance_connection()

ASX_100_STOCKS = {
    'Financial': ['CBA', 'NAB', 'WBC', 'ANZ', 'MQG', 'ASX', 'AMP', 'IAG', 'QBE', 'SUN'],
    'Materials': ['BHP', 'RIO', 'FMG', 'NCM', 'AMC', 'JHX', 'ORI', 'BSL', 'IGO', 'MIN'],
    'Healthcare': ['CSL', 'RMD', 'COH', 'SHL', 'FPH', 'NEA', 'PME', 'RHC', 'ANN'],
    'Consumer': ['WOW', 'WES', 'COL', 'JBH', 'HVN', 'DMP', 'ALL', 'TAH', 'ARB'],
    'Energy': ['WDS', 'STO', 'ORG', 'WHC', 'PDN', 'BPT', 'PLS'],
    'Real Estate': ['GMG', 'SCG', 'SGP', 'LLC', 'DXS', 'VCX', 'MGR'],
    'Telecom & Tech': ['TLS', 'REA', 'CAR', 'XRO', 'WTC', 'TPG', 'CPU', 'ALU'],
    'Industrials': ['TCL', 'TWE', 'QAN', 'BXB', 'DOW', 'SEK', 'AZJ', 'SVW'],
    'Utilities': ['APA', 'AGL', 'MCY']
}

time_periods = {
    "Max": None,
    "1 Day": 1,
    "1 Month": 30,
    "1 Year": 365,
    "5 Years": 1825,
}


# 4. UTILITY FUNCTIONS

def comprehensive_price_update_diagnostics():
    """
    Comprehensive diagnostics for price update functionality
    """
    diagnostics = {
        'network_checks': [],
        'stock_data_retrieval': [],
        'price_manager_tests': []
    }

    # 1. Network and Basic Connectivity Checks
    try:
        import socket
        socket.create_connection(("www.google.com", 80))
        diagnostics['network_checks'].append({
            'test': 'Internet Connectivity',
            'status': 'PASS',
            'details': 'Successfully connected to internet'
        })
    except Exception as e:
        diagnostics['network_checks'].append({
            'test': 'Internet Connectivity',
            'status': 'FAIL',
            'error': str(e)
        })

    # 2. YFinance Connectivity Test
    def test_yfinance_stock(stock_symbol):
        try:
            ticker = yf.Ticker(f"{stock_symbol}.AX")
            data = ticker.history(period="1d")

            if data is not None and len(data) > 0:
                return {
                    'stock': stock_symbol,
                    'status': 'PASS',
                    'data_points': len(data),
                    'latest_close': data['Close'].iloc[-1] if len(data) > 0 else None
                }
            else:
                return {
                    'stock': stock_symbol,
                    'status': 'FAIL',
                    'error': 'No data retrieved'
                }
        except Exception as e:
            return {
                'stock': stock_symbol,
                'status': 'FAIL',
                'error': str(e),
                'traceback': traceback.format_exc()
            }

    # Test a sample of stocks from different sectors
    sample_stocks = [
        'CBA',  # Financial
        'BHP',  # Materials
        'CSL',  # Healthcare
        'WOW',  # Consumer
        'WDS'  # Energy
    ]

    for stock in sample_stocks:
        stock_result = test_yfinance_stock(stock)
        diagnostics['stock_data_retrieval'].append(stock_result)

    # 3. Price Update Manager Functionality Test
    try:
        # Simulate price update manager functionality
        class MockPriceUpdateManager:
            def __init__(self):
                self.last_prices = {}

            def simulate_price_updates(self, stocks):
                for stock in stocks:
                    try:
                        ticker = yf.Ticker(f"{stock}.AX")
                        data = ticker.history(period="1d")
                        if len(data) > 0:
                            self.last_prices[stock] = data['Close'].iloc[-1]
                        else:
                            self.last_prices[stock] = None
                    except Exception as e:
                        self.last_prices[stock] = f"Error: {str(e)}"

        price_manager = MockPriceUpdateManager()
        price_manager.simulate_price_updates(sample_stocks)

        price_update_results = {
            'total_stocks': len(sample_stocks),
            'stocks_updated': sum(1 for price in price_manager.last_prices.values() if isinstance(price, (int, float))),
            'stocks_failed': sum(
                1 for price in price_manager.last_prices.values() if not isinstance(price, (int, float))),
            'last_prices': price_manager.last_prices
        }

        diagnostics['price_manager_tests'].append({
            'test': 'Price Update Simulation',
            'status': 'PASS' if price_update_results['stocks_updated'] > 0 else 'FAIL',
            'details': price_update_results
        })

    except Exception as e:
        diagnostics['price_manager_tests'].append({
            'test': 'Price Update Simulation',
            'status': 'FAIL',
            'error': str(e),
            'traceback': traceback.format_exc()
        })

    return diagnostics


def display_price_update_diagnostics(diagnostics):
    """
    Display diagnostics results in Streamlit
    """
    st.header("🔍 Price Update Diagnostics")

    # Network Checks
    st.subheader("1. Network Connectivity")
    for check in diagnostics['network_checks']:
        status_color = "green" if check['status'] == 'PASS' else "red"
        st.markdown(f"**{check['test']}:** :{status_color}[{check['status']}]")
        if check['status'] == 'FAIL':
            st.error(f"Error: {check.get('error', 'Unknown error')}")

    # Stock Data Retrieval
    st.subheader("2. Stock Data Retrieval")
    for stock_result in diagnostics['stock_data_retrieval']:
        status_color = "green" if stock_result['status'] == 'PASS' else "red"
        st.markdown(f"**{stock_result['stock']}:** :{status_color}[{stock_result['status']}]")

        if stock_result['status'] == 'PASS':
            st.write(f"Data Points: {stock_result.get('data_points', 'N/A')}")
            st.write(f"Latest Close Price: ${stock_result.get('latest_close', 'N/A'):.2f}")
        else:
            st.error(f"Error: {stock_result.get('error', 'Unknown error')}")
            if 'traceback' in stock_result:
                with st.expander("Error Details"):
                    st.code(stock_result['traceback'])

    # Price Manager Tests
    st.subheader("3. Price Update Manager")
    for test in diagnostics['price_manager_tests']:
        status_color = "green" if test['status'] == 'PASS' else "red"
        st.markdown(f"**{test['test']}:** :{status_color}[{test['status']}]")

        if test['status'] == 'PASS':
            details = test.get('details', {})
            st.write(f"Total Stocks: {details.get('total_stocks', 'N/A')}")
            st.write(f"Stocks Updated: {details.get('stocks_updated', 'N/A')}")
            st.write(f"Stocks Failed: {details.get('stocks_failed', 'N/A')}")

            with st.expander("Last Prices"):
                st.json(details.get('last_prices', {}))
        else:
            st.error(f"Error: {test.get('error', 'Unknown error')}")
            if 'traceback' in test:
                with st.expander("Error Details"):
                    st.code(test['traceback'])


def test_live_price_updates():
    """
    Comprehensive test function to verify live price updates and backtest synchronization.
    """
    try:
        # Initialize test results
        results = {
            'success': False,
            'price_updates': {
                'status': False,
                'details': [],
                'errors': []
            },
            'backtest_updates': {
                'status': False,
                'details': [],
                'errors': []
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 1. Test Price Update Functionality
        try:
            if not ASX_100_STOCKS:
                results['price_updates']['errors'].append("No stocks defined in ASX_100_STOCKS")
                return results

            sample_stock = list(ASX_100_STOCKS.values())[0][0]

            try:
                sample_data = get_stock_data(sample_stock, period=1)
                if sample_data is None or len(sample_data) == 0:
                    results['price_updates']['errors'].append(f"Failed to retrieve data for {sample_stock}")
                else:
                    results['price_updates']['status'] = True
                    results['price_updates']['details'].append(f"Successfully retrieved data for {sample_stock}")
                    results['price_updates']['details'].append(f"Data points: {len(sample_data)}")
                    results['price_updates']['details'].append(
                        f"Date range: {sample_data.index[0]} to {sample_data.index[-1]}")
            except Exception as data_error:
                results['price_updates']['errors'].append(f"Data retrieval error: {str(data_error)}")

        except Exception as price_update_error:
            results['price_updates']['errors'].append(f"Price update test failed: {str(price_update_error)}")

        # 2. Test Backtest Update Functionality
        try:
            timeframes = ["Weekly", "Monthly"]
            successful_backtests = []
            backtest_errors = []

            for timeframe in timeframes:
                try:
                    # Get sample data
                    sample_data = get_stock_data(sample_stock, period=365, timeframe=timeframe)

                    if sample_data is not None and len(sample_data) > 0:
                        # Instead of actually logging the backtest, just verify we can run it
                        _, swing_points = calculate_gann_swing(sample_data)
                        backtest_results = backtest_gann_swing_strategy(
                            sample_data,
                            swing_points,
                            initial_capital=10000,
                            position_size_pct=0.5
                        )

                        # Don't log the results, just verify we can calculate them
                        total_trades = len(backtest_results.trades)
                        winning_trades = len([t for t in backtest_results.trades if t['profit'] > 0])
                        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

                        successful_backtests.append({
                            'timeframe': timeframe,
                            'trades': total_trades,
                            'win_rate': win_rate
                        })
                    else:
                        backtest_errors.append(f"Insufficient data for {timeframe} backtest")

                except Exception as backtest_error:
                    backtest_errors.append(f"Error in {timeframe} backtest: {str(backtest_error)}")

            # Update results based on backtest attempts
            if successful_backtests:
                results['backtest_updates']['status'] = True
                for backtest in successful_backtests:
                    results['backtest_updates']['details'].append(
                        f"Successfully ran {backtest['timeframe']} backtest "
                        f"(Trades: {backtest['trades']}, Win Rate: {backtest['win_rate']:.1f}%)"
                    )

            if backtest_errors:
                for error in backtest_errors:
                    results['backtest_updates']['errors'].append(error)

        except Exception as backtest_update_error:
            results['backtest_updates']['errors'].append(f"Backtest update test failed: {str(backtest_update_error)}")

        # Determine overall success
        results['success'] = (
                results['price_updates']['status'] and
                results['backtest_updates']['status']
        )

        return results

    except Exception as general_error:
        return {
            'success': False,
            'error': str(general_error),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

# In your Streamlit app, you can now use this:

def display_test_results(results):
    """Display the test results in a formatted way using Streamlit."""
    st.header("🧪 Live Price Test Results")

    # Safely get value from nested dictionary
    def safe_get(dictionary, *keys, default=None):
        for key in keys:
            try:
                dictionary = dictionary[key]
            except (KeyError, TypeError):
                return default
        return dictionary

    # Overall status
    success = safe_get(results, 'success', default=False)
    status_color = "green" if success else "red"
    st.markdown(
        f"**Overall Status:** :{status_color}[{'✅ PASSED' if success else '❌ FAILED'}]"
    )
    st.markdown(f"**Test Time:** {safe_get(results, 'timestamp', default='N/A')}")

    # Error handling
    if 'error' in results:
        st.error(f"Test Error: {results['error']}")
        return

    # Price Updates Section
    st.subheader("Price Update Tests")
    price_updates = safe_get(results, 'price_updates', default={})
    price_status = safe_get(price_updates, 'status', default=False)
    st.markdown(
        f"Status: :{status_color}[{'✅ PASSED' if price_status else '❌ FAILED'}]"
    )

    price_details = safe_get(price_updates, 'details', default=[])
    if price_details:
        st.markdown("**Details:**")
        for detail in price_details:
            st.markdown(f"- {detail}")

    price_errors = safe_get(price_updates, 'errors', default=[])
    if price_errors:
        st.markdown("**Errors:**")
        for error in price_errors:
            st.error(error)

    # Backtest Updates Section
    st.subheader("Backtest Update Tests")
    backtest_updates = safe_get(results, 'backtest_updates', default={})
    backtest_status = safe_get(backtest_updates, 'status', default=False)
    st.markdown(
        f"Status: :{status_color}[{'✅ PASSED' if backtest_status else '❌ FAILED'}]"
    )

    backtest_details = safe_get(backtest_updates, 'details', default=[])
    if backtest_details:
        st.markdown("**Details:**")
        for detail in backtest_details:
            st.markdown(f"- {detail}")

    backtest_errors = safe_get(backtest_updates, 'errors', default=[])
    if backtest_errors:
        st.markdown("**Errors:**")
        for error in backtest_errors:
            st.error(error)


# Example usage in the Streamlit app:
# if st.button("Run Live Price Tests"):

class PriceUpdateManager:
    def __init__(self, update_interval=60):
        print(f"Initializing PriceUpdateManager with interval {update_interval}")

        self.update_interval = update_interval
        self.last_prices = {}
        self.stop_event = threading.Event()

        # Explicitly set update_thread as None
        self.update_thread = None

        # Global queue initialization
        global price_update_queue
        if 'price_update_queue' not in globals():
            price_update_queue = queue.Queue()

    def start_updates(self):
        print("Starting updates")
        print(f"Current update_thread status: {self.update_thread}")

        if self.update_thread is None or not self.update_thread.is_alive():
            self.stop_event.clear()
            self.update_thread = threading.Thread(target=self._update_loop)
            self.update_thread.daemon = True
            self.update_thread.start()

        print(f"After start - update_thread: {self.update_thread}")

    def stop_updates(self):
        print("Stopping updates")
        if self.stop_event:
            self.stop_event.set()
        if self.update_thread:
            self.update_thread.join(timeout=5)

    def _update_loop(self):
        print("Entering update loop")
        while not self.stop_event.is_set():
            try:
                self._check_price_updates()
                time.sleep(self.update_interval)
            except Exception as e:
                print(f"Error in update loop: {e}")
                traceback.print_exc()

    def _check_price_updates(self):
        print("Checking price updates")
        # Minimal implementation for testing
        pass


def test_live_price_updates():
    print("Starting test_live_price_updates")
    try:
        # Create manager explicitly
        test_manager = PriceUpdateManager(update_interval=10)

        # Verify thread attribute before start
        print(f"Before start - hasattr update_thread: {hasattr(test_manager, 'update_thread')}")
        print(f"Before start - update_thread value: {test_manager.update_thread}")

        # Start updates
        test_manager.start_updates()

        # Wait and verify
        time.sleep(5)

        print(f"After start - hasattr update_thread: {hasattr(test_manager, 'update_thread')}")
        print(f"After start - update_thread value: {test_manager.update_thread}")
        print(f"Thread alive: {test_manager.update_thread.is_alive() if test_manager.update_thread else 'No thread'}")

        # Stop updates
        test_manager.stop_updates()

        return {
            'success': True,
            'details': 'Price update test completed successfully',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    except Exception as e:
        print(f"Test failed with error: {e}")
        traceback.print_exc()
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


# Initialization function to ensure proper setup
def initialize_price_update_manager():
    if 'price_manager' not in st.session_state:
        st.session_state.price_manager = PriceUpdateManager()

    # Start updates if not already running
    if not hasattr(st.session_state.price_manager, 'update_thread') or \
            st.session_state.price_manager.update_thread is None or \
            not st.session_state.price_manager.update_thread.is_alive():
        st.session_state.price_manager.start_updates()

# 3. Add this to the UTILITY FUNCTIONS section
def process_price_updates():
    while not price_update_queue.empty():
        update = price_update_queue.get()

        period_days = time_periods[st.session_state.selected_period]
        df = get_stock_data(update['stock'], period=period_days,
                            timeframe=st.session_state.selected_timeframe)

        if df is not None and len(df) > 0:
            if st.session_state.selected_timeframe == "Weekly":
                strategy = Strategy.SWING
                _, swing_points = calculate_gann_swing(df)
                results = backtest_gann_swing_strategy(
                    df,
                    swing_points,
                    initial_capital=10000,
                    position_size_pct=1
                )
            else:
                strategy = Strategy.TRENDLINE
                results = backtest_trendline_strategy(
                    df,
                    initial_capital=10000,
                    position_size_pct=1
                )

            log_backtest_result(
                update['stock'],
                st.session_state.selected_period,
                st.session_state.selected_timeframe,
                10000,
                0.5,
                results
            )

            if results.trades:
                latest_trade = results.trades[-1]
                if latest_trade['exit_date'] > (datetime.now() - timedelta(days=1)):
                    st.session_state.show_notifications = True
                    st.session_state.notification_message = (
                        f"New signal for {update['stock']}: "
                        f"{'BUY' if results.current_position else 'SELL'} "
                        f"at ${update['new_price']:.2f}"
                    )

def _check_price_updates(self):
    try:
        print("Starting price update check...")
        for sector in ASX_100_STOCKS.values():
            for stock in sector:
                try:
                    current_data = get_stock_data(stock, period=1, timeframe="Daily")
                    if current_data is not None and len(current_data) > 0:
                        print(f"Successfully retrieved data for {stock}")
                    else:
                        print(f"No data retrieved for {stock}")
                except Exception as e:
                    print(f"Error updating {stock}: {e}")
    except Exception as e:
        print(f"Critical error in price update process: {e}")


def test_backtest_update_functionality():
    """
    Comprehensive diagnostic for backtest update functionality
    """
    diagnostics = {
        'backtest_retrieval': [],
        'backtest_logging': [],
        'backtest_processing': [],
        'detailed_errors': [],
        'overall_status': 'FAIL'
    }

    try:
        # 1. Test Backtest Logging
        def test_single_stock_backtest(stock, timeframe):
            try:
                # Retrieve stock data
                df = get_stock_data(stock, period=365, timeframe=timeframe)

                if df is None or len(df) < 2:
                    return {
                        'stock': stock,
                        'timeframe': timeframe,
                        'status': 'FAIL',
                        'error': 'Insufficient data for backtest'
                    }

                # Perform backtest
                strategy = Strategy.SWING if timeframe == "Weekly" else Strategy.TRENDLINE

                if strategy == Strategy.SWING:
                    _, swing_points = calculate_gann_swing(df)
                    backtest_results = backtest_gann_swing_strategy(
                        df,
                        swing_points,
                        initial_capital=10000,
                        position_size_pct=1
                    )
                else:
                    backtest_results = backtest_trendline_strategy(
                        df,
                        initial_capital=10000,
                        position_size_pct=1
                    )

                # Log backtest results
                log_backtest_result(
                    stock,
                    "1 Year",
                    timeframe,
                    10000,
                    0.5,
                    backtest_results
                )

                # Verify logging
                logs = get_backtest_logs()
                matching_logs = [
                    log for log in logs
                    if log['stock'] == stock and log['timeframe'] == timeframe
                ]

                return {
                    'stock': stock,
                    'timeframe': timeframe,
                    'status': 'PASS' if matching_logs else 'FAIL',
                    'trades_count': len(backtest_results.trades),
                    'logged_entries': len(matching_logs)
                }

            except Exception as e:
                return {
                    'stock': stock,
                    'timeframe': timeframe,
                    'status': 'FAIL',
                    'error': str(e),
                    'traceback': traceback.format_exc()
                }

        # Sample stocks and timeframes to test
        test_cases = [
            ('CBA', 'Daily'),
            ('BHP', 'Weekly'),
            ('CSL', 'Monthly')
        ]

        # Run backtest tests
        backtest_results = []
        for stock, timeframe in test_cases:
            result = test_single_stock_backtest(stock, timeframe)
            backtest_results.append(result)

            # Categorize results
            if result['status'] == 'PASS':
                diagnostics['backtest_logging'].append(result)
            else:
                diagnostics['detailed_errors'].append(result)

        # Determine overall status
        diagnostics['overall_status'] = (
            'PASS' if all(result['status'] == 'PASS' for result in backtest_results)
            else 'FAIL'
        )

    except Exception as e:
        diagnostics['detailed_errors'].append({
            'status': 'FAIL',
            'error': str(e),
            'traceback': traceback.format_exc()
        })
        diagnostics['overall_status'] = 'FAIL'

    return diagnostics


def test_live_price_updates():
    """
    Modify to include backtest update diagnostics
    """
    # Existing price update diagnostics
    price_diagnostics = comprehensive_price_update_diagnostics()

    # Run backtest update diagnostics
    backtest_diagnostics = test_backtest_update_functionality()

    # Prepare results
    results = {
        'success': (
                all(test.get('status') == 'PASS'
                    for test_group in ['network_checks', 'stock_data_retrieval', 'price_manager_tests']
                    for test in price_diagnostics.get(test_group, [])
                    ) and
                backtest_diagnostics['overall_status'] == 'PASS'
        ),
        'price_updates': {
            'status': all(
                test.get('status') == 'PASS'
                for test_group in ['network_checks', 'stock_data_retrieval', 'price_manager_tests']
                for test in price_diagnostics.get(test_group, [])
            ),
            'details': [],
            'errors': []
        },
        'backtest_updates': {
            'status': backtest_diagnostics['overall_status'] == 'PASS',
            'details': [],
            'errors': []
        },
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Collect backtest details and errors
    if results['backtest_updates']['status']:
        results['backtest_updates']['details'] = [
            f"Successful backtest for {result['stock']} ({result['timeframe']})"
            for result in backtest_diagnostics.get('backtest_logging', [])
        ]
    else:
        results['backtest_updates']['errors'] = [
            f"Backtest failed for {error.get('stock', 'Unknown Stock')} ({error.get('timeframe', 'Unknown Timeframe')}): {error.get('error', 'Unknown Error')}"
            for error in backtest_diagnostics.get('detailed_errors', [])
        ]

    return results

def delete_all_backtest_data():
    """Delete all backtest data files and reset the logs."""
    import os
    import shutil
    import json

    try:
        # Check if backtest_logs directory exists
        if os.path.exists('backtest_logs'):
            # Remove the entire directory and its contents
            shutil.rmtree('backtest_logs')

            # Recreate empty directory and log file
            os.makedirs('backtest_logs')
            with open('backtest_logs/backtest_log.json', 'w') as f:
                json.dump([], f)

            return True, "Successfully cleared all backtest data"
        else:
            # Create fresh directory and log file
            os.makedirs('backtest_logs')
            with open('backtest_logs/backtest_log.json', 'w') as f:
                json.dump([], f)

            return True, "No existing data found. Created new empty backtest logs."

    except Exception as e:
        return False, f"Error while deleting backtest data: {str(e)}"


def get_stock_data(ticker, period=None, timeframe="Daily"):
    try:
        print(f"Attempting to retrieve data for {ticker}")
        interval = {
            "Daily": "1d",
            "Weekly": "1wk",
            "Monthly": "1mo"
        }[timeframe]

        stock = yf.Ticker(f"{ticker}.AX")

        # Add more detailed error handling
        try:
            if period is None:
                data = stock.history(period="max", interval=interval)
            else:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=period)
                data = stock.history(start=start_date, end=end_date, interval=interval)
        except Exception as detailed_error:
            print(f"Detailed retrieval error for {ticker}: {detailed_error}")
            return None

        if data.empty:
            print(f"No data available for {ticker}")
            return None

        print(f"Successfully retrieved {len(data)} data points for {ticker}")
        return data
    except Exception as e:
        print(f"Unexpected error retrieving data for {ticker}: {e}")
        return None

        if len(data) < 2:
            st.warning("Insufficient data points for the selected period.")
            return None

        # For monthly timeframe, ensure we only have one bar per month
        if timeframe == "Monthly":
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)

            data = data.groupby([data.index.year, data.index.month]).agg({
                'Open': 'first',
                'High': 'max',
                'Low': 'min',
                'Close': 'last',
                'Volume': 'sum'
            })

            data.index = pd.to_datetime([f"{year}-{month:02d}-01" for year, month in data.index])

        return data
    except Exception as e:
        st.error(f"Error retrieving data: {e}")
        return None


def get_stock_metrics(ticker):
    """Retrieve additional stock metrics including ASX ranking."""
    try:
        stock = yf.Ticker(f"{ticker}.AX")
        info = stock.info

        def safe_convert(value, convert_func=float, default='N/A'):
            try:
                # Remove percentage sign if present
                if isinstance(value, str):
                    value = value.replace('%', '').replace('$', '').strip()

                # Convert if possible
                return convert_func(value) if value else default
            except (ValueError, TypeError):
                return default

        market_cap = safe_convert(info.get("marketCap"), float, 0)
        market_cap_billion = market_cap / 1e9 if market_cap else "N/A"

        asx_ranking = "Outside ASX 300"
        if market_cap_billion != "N/A":
            if market_cap_billion > 30:
                asx_ranking = "ASX 50"
            elif market_cap_billion > 10:
                asx_ranking = "ASX 100"
            elif market_cap_billion > 3:
                asx_ranking = "ASX 200"
            elif market_cap_billion > 1:
                asx_ranking = "ASX 300"

        metrics = {
            "ASX Ranking": asx_ranking,
            "Market Cap (B)": f"${market_cap_billion:.2f}B" if market_cap_billion != "N/A" else "N/A",
            "EPS Current": safe_convert(info.get("trailingEps"), float, "N/A"),
            "EPS Past": safe_convert(info.get("forwardEps"), float, "N/A"),
            "EPS Projected": safe_convert(info.get("forwardEps"), float, "N/A"),
            "P/E Ratio": safe_convert(info.get("trailingPE"), float, "N/A"),
            "Dividend Yield": f"{safe_convert(info.get('dividendYield'), lambda x: float(x) * 100, 0):.2f}%"
            if info.get("dividendYield") is not None else "N/A",
        }
        return metrics
    except Exception as e:
        st.error(f"Error retrieving stock metrics: {e}")
        return None


def get_backtest_logs():
    """Retrieve backtest logs from the saved JSON file."""
    log_file = 'backtest_logs/backtest_log.json'
    try:
        with open(log_file, 'r') as f:
            logs = json.load(f)

        if not logs:
            return []

        return logs  # ✅ Ensure it returns the full logs, including trades

    except (FileNotFoundError, json.JSONDecodeError):
        return []

        # Dictionary to store best results per stock and timeframe
        stock_results = {}

        for log in logs:
            stock = log['stock']
            timeframe = log.get('timeframe', 'Unknown')

            if timeframe not in ['Weekly', 'Monthly']:
                continue

            # Create unique key for stock-timeframe combination
            stock_tf_key = f"{stock}_{timeframe}"

            # Initialize stock in results dict if not present
            if stock not in stock_results:
                stock_results[stock] = {}

            # Update best result for this stock and timeframe
            if (timeframe not in stock_results[stock] or
                    log['total_profit'] > stock_results[stock][timeframe]['total_profit']):
                stock_results[stock][timeframe] = log

        final_performance_list = []

        for stock, timeframe_results in stock_results.items():
            for timeframe, log in timeframe_results.items():
                win_rate = (log['winning_trades'] / log['total_trades'] * 100) if log['total_trades'] > 0 else 0

                if win_rate <= 60:
                    continue

                final_performance = {
                    'stock': stock,
                    'timeframe': timeframe,
                    'total_trades': log['total_trades'],
                    'winning_trades': log['winning_trades'],
                    'win_rate': win_rate,
                    'total_profit': log['total_profit'],
                    'avg_profit_percentage': log['profit_percentage'],
                    'best_profit_percentage': log['profit_percentage'],
                    'worst_profit_percentage': log['profit_percentage'],
                    'periods': log['period']
                }
                final_performance_list.append(final_performance)

        # Sort by stock first, then by total profit within each stock
        return sorted(final_performance_list,
                      key=lambda x: (x['stock'], -x['total_profit']))

    except (FileNotFoundError, json.JSONDecodeError):
        return []


def calculate_max_drawdown(equity_curve):
    """Calculate maximum drawdown from equity curve."""
    if not equity_curve:
        return 0.0

    equity_df = pd.DataFrame(equity_curve)

    if 'portfolio_value' not in equity_df.columns and 'equity' in equity_df.columns:
        equity_df['portfolio_value'] = equity_df['equity']

    equity_df['peak'] = equity_df['portfolio_value'].cummax()
    equity_df['drawdown'] = (equity_df['portfolio_value'] - equity_df['peak']) / equity_df['peak'] * 100

    return abs(equity_df['drawdown'].min()) if len(equity_df) > 0 else 0.0


# 5. TECHNICAL ANALYSIS FUNCTIONS
def calculate_gann_swing(data):
    """Calculate Gann Swing points"""
    if len(data) < 2:
        return data, []

    df = data.copy()
    df['SwingHigh'] = np.nan
    df['SwingLow'] = np.nan
    swing_points = []

    def classify_bar(current, previous):
        if current['High'] > previous['High'] and current['Low'] > previous['Low']:
            return 'Up'
        elif current['High'] < previous['High'] and current['Low'] < previous['Low']:
            return 'Down'
        elif current['High'] <= previous['High'] and current['Low'] >= previous['Low']:
            return 'Inside'
        else:
            return 'Outside'

    current_trend = None
    consecutive_count = 0
    current_trend_bars = []

    for i in range(1, len(df)):
        current_bar = df.iloc[i]
        previous_bar = df.iloc[i - 1]
        bar_type = classify_bar(current_bar, previous_bar)

        if bar_type in ['Inside', 'Outside']:
            if current_trend is not None:
                current_trend_bars.append(i)
            continue

        if current_trend is None:
            if bar_type in ['Up', 'Down']:
                current_trend = bar_type
                consecutive_count = 1
                current_trend_bars = [i]
        else:
            if bar_type == current_trend:
                consecutive_count += 1
                current_trend_bars.append(i)
            else:
                if consecutive_count > 0:
                    if current_trend == 'Up':
                        high_idx = df.iloc[current_trend_bars]['High'].idxmax()
                        high_price = df.iloc[current_trend_bars]['High'].max()
                        df.loc[high_idx, 'SwingHigh'] = high_price
                        swing_points.append((high_idx, high_price, 'high'))
                    else:
                        low_idx = df.iloc[current_trend_bars]['Low'].idxmin()
                        low_price = df.iloc[current_trend_bars]['Low'].min()
                        df.loc[low_idx, 'SwingLow'] = low_price
                        swing_points.append((low_idx, low_price, 'low'))

                current_trend = bar_type
                consecutive_count = 1
                current_trend_bars = [i]

    if current_trend and consecutive_count > 0:
        if current_trend == 'Up':
            high_idx = df.iloc[current_trend_bars]['High'].idxmax()
            high_price = df.iloc[current_trend_bars]['High'].max()
            df.loc[high_idx, 'SwingHigh'] = high_price
            swing_points.append((high_idx, high_price, 'high'))
        else:
            low_idx = df.iloc[current_trend_bars]['Low'].idxmin()
            low_price = df.iloc[current_trend_bars]['Low'].min()
            df.loc[low_idx, 'SwingLow'] = low_price
            swing_points.append((low_idx, low_price, 'low'))

    return df, swing_points


def identify_valid_trendlines(data, min_bars=12):
    """
    Identify valid trend lines based on Gann's rules:
    - Minimum 12 bars to confirm trend
    - Three troughs for uptrends, three peaks for downtrends
    - Points can deviate slightly from line (within 2%)
    - Line extends until broken by 2%
    """
    if len(data) < min_bars:
        return []

    trends = []
    df = data.copy()

    def calculate_line_equation(point1, point2):
        """Calculate slope and intercept of line between two points"""
        x1 = pd.Timestamp(point1[0]).timestamp()
        x2 = pd.Timestamp(point2[0]).timestamp()
        y1 = point1[1]
        y2 = point2[1]

        slope = (y2 - y1) / (x2 - x1)
        intercept = y1 - slope * x1

        return slope, intercept

    def calculate_line_price(x, slope, intercept):
        """Calculate price at given x coordinate using line equation"""
        return slope * x + intercept

    def find_line_break(data, start_date, slope, intercept, is_downtrend=True):
        """Find where the line is broken by 2%"""
        for idx, row in data.loc[start_date:].iterrows():
            x = pd.Timestamp(idx).timestamp()
            line_price = calculate_line_price(x, slope, intercept)

            if is_downtrend:
                if row['High'] > line_price * 1.02:  # 2% break above line
                    return idx
            else:
                if row['Low'] < line_price * 0.98:  # 2% break below line
                    return idx
        return None

    def find_peaks_troughs(data, lookback=5, lookahead=5):
        """Identify peaks and troughs using price action"""
        peaks = []
        troughs = []

        for i in range(lookback, len(data) - lookahead):
            current_bar = data.iloc[i]
            prev_bars = data.iloc[i - lookback:i]
            next_bars = data.iloc[i + 1:i + lookahead + 1]

            # Check for peak
            if all(current_bar['High'] >= bar['High'] for _, bar in prev_bars.iterrows()) and \
                    all(current_bar['High'] >= bar['High'] for _, bar in next_bars.iterrows()):
                peaks.append((data.index[i], current_bar['High']))

            # Check for trough
            if all(current_bar['Low'] <= bar['Low'] for _, bar in prev_bars.iterrows()) and \
                    all(current_bar['Low'] <= bar['Low'] for _, bar in next_bars.iterrows()):
                troughs.append((data.index[i], current_bar['Low']))

        return peaks, troughs

    def validate_trendline(points, is_downtrend=True):
        """
        Validate trend line points:
        - Points should move in correct direction
        - All points should be within 2% of line
        - For uptrends, need three valid troughs
        - For downtrends, need three valid peaks
        """
        if len(points) < 3:
            return False

        sorted_points = sorted(points, key=lambda x: x[0])
        slope, intercept = calculate_line_equation(sorted_points[0], sorted_points[-1])

        # Check direction
        if is_downtrend:
            if sorted_points[-1][1] >= sorted_points[0][1]:
                return False
        else:
            if sorted_points[-1][1] <= sorted_points[0][1]:
                return False

        # Validate points are within 2% of line
        for point in sorted_points:
            x = pd.Timestamp(point[0]).timestamp()
            line_price = calculate_line_price(x, slope, intercept)
            deviation = abs(point[1] - line_price) / line_price * 100

            if deviation > 2:
                return False

        return True

    def extend_trendline(points, data, is_downtrend=True):
        """Extend trendline until broken"""
        sorted_points = sorted(points, key=lambda x: x[0])
        slope, intercept = calculate_line_equation(sorted_points[0], sorted_points[-1])

        # Find break point
        break_date = find_line_break(data, sorted_points[-1][0], slope, intercept, is_downtrend)

        if break_date is None:
            end_date = data.index[-1]
        else:
            end_date = break_date

        # Calculate final point
        end_x = pd.Timestamp(end_date).timestamp()
        end_price = calculate_line_price(end_x, slope, intercept)

        return sorted_points + [(end_date, end_price)]

    # Find all peaks and troughs
    peaks, troughs = find_peaks_troughs(df)

    # Identify uptrend lines
    for i in range(len(troughs) - 2):
        # Check for minimum 12 bars trending up before the second trough
        if i > 0:  # Skip first trough as it's the starting point
            trend_start = troughs[i][0]
            trend_bars = df.loc[:trend_start].tail(min_bars)
            if len(trend_bars) >= min_bars:
                if not all(trend_bars.iloc[j]['Low'] <= trend_bars.iloc[j + 1]['Low']
                           for j in range(len(trend_bars) - 1)):
                    continue

        for j in range(i + 1, len(troughs) - 1):
            for k in range(j + 1, len(troughs)):
                trough_points = [troughs[i], troughs[j], troughs[k]]
                if validate_trendline(trough_points, is_downtrend=False):
                    extended_points = extend_trendline(trough_points, df, is_downtrend=False)
                    trends.append({
                        'type': 'uptrend',
                        'points': extended_points,
                        'start_idx': extended_points[0][0],
                        'end_idx': extended_points[-1][0],
                        'start_price': extended_points[0][1],
                        'end_price': extended_points[-1][1]
                    })

    # Identify downtrend lines (existing code remains the same)
    for i in range(len(peaks) - 2):
        for j in range(i + 1, len(peaks) - 1):
            for k in range(j + 1, len(peaks)):
                peak_points = [peaks[i], peaks[j], peaks[k]]
                if validate_trendline(peak_points, is_downtrend=True):
                    extended_points = extend_trendline(peak_points, df, is_downtrend=True)
                    trends.append({
                        'type': 'downtrend',
                        'points': extended_points,
                        'start_idx': extended_points[0][0],
                        'end_idx': extended_points[-1][0],
                        'start_price': extended_points[0][1],
                        'end_price': extended_points[-1][1]
                    })

    return trends


def create_ohlc_chart_with_trendlines(data, show_swing_lines=True):
    """Create OHLC chart with extended trend lines"""
    if data is None or len(data) < 2:
        return None

    # Create base chart
    fig = go.Figure()

    # Add OHLC bars
    fig.add_trace(
        go.Ohlc(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350'
        )
    )

    # Add trend lines
    trends = identify_valid_trendlines(data, min_bars=12)

    for trend in trends:
        points = trend['points']
        dates = [point[0] for point in points]
        prices = [point[1] for point in points]

        # Add trend line
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=prices,
                mode='lines',
                line=dict(
                    color='green' if trend['type'] == 'uptrend' else 'red',
                    width=2,
                    dash='solid'
                ),
                name=f"{trend['type'].capitalize()} Line"
            )
        )

        # Add first three points used to create the trend line
        fig.add_trace(
            go.Scatter(
                x=dates[:3],  # Only the first three points
                y=prices[:3],
                mode='markers',
                marker=dict(
                    color='green' if trend['type'] == 'uptrend' else 'red',
                    size=8,
                    symbol='circle'
                ),
                name=f"{trend['type'].capitalize()} Points"
            )
        )

    # Update layout
    fig.update_layout(
        title='Stock Price Chart with Trend Lines',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            type='date',
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        margin=dict(b=40),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)"
        )
    )

    return fig

def get_historical_signals(data, strategy=Strategy.SWING):
    """Get all trading signals from the historical data"""
    signals = []

    if strategy == Strategy.SWING:
        _, swing_points = calculate_gann_swing(data)

        for i in range(1, len(swing_points)):
            current_swing = swing_points[i]
            previous_swing = swing_points[i - 1]

            if current_swing[2] == 'low' and previous_swing[2] == 'low':
                if current_swing[1] > previous_swing[1]:
                    signals.append({
                        'type': 'BUY',
                        'price': current_swing[1],
                        'timestamp': current_swing[0],
                        'message': f"Buy Signal: Higher trough pattern detected at ${current_swing[1]:.2f}"
                    })

            elif current_swing[2] == 'high' and previous_swing[2] == 'high':
                if current_swing[1] < previous_swing[1]:
                    signals.append({
                        'type': 'SELL',
                        'price': current_swing[1],
                        'timestamp': current_swing[0],
                        'message': f"Sell Signal: Lower peak pattern detected at ${current_swing[1]:.2f}"
                    })
    else:  # Trendline strategy
        trends = identify_valid_trendlines(data, min_bars=12)
        current_trend = None

        for trend in trends:
            if current_trend is None:
                current_trend = trend
                continue

            # Generate signals based on trend line breaks
            if current_trend['type'] == 'downtrend' and trend['type'] == 'uptrend':
                signals.append({
                    'type': 'BUY',
                    'price': trend['start_price'],
                    'timestamp': trend['start_idx'],
                    'message': f"Buy Signal: Uptrend confirmed at ${trend['start_price']:.2f}"
                })
            elif current_trend['type'] == 'uptrend' and trend['type'] == 'downtrend':
                signals.append({
                    'type': 'SELL',
                    'price': trend['start_price'],
                    'timestamp': trend['start_idx'],
                    'message': f"Sell Signal: Downtrend confirmed at ${trend['start_price']:.2f}"
                })

            current_trend = trend

    return signals


def get_trading_goers_stocks():
    """Get unique list of stocks from backtest logs that meet performance criteria."""
    logs = get_backtest_logs()  # This already filters for win rate > 60% and min 4 trades

    # Get unique stocks from logs
    trading_goers = list(set(log['stock'] for log in logs))

    # Sort alphabetically
    trading_goers.sort()

    return trading_goers


def update_sector_dictionary():
    """Update the ASX_100_STOCKS dictionary to include Trading Goers sector."""
    global ASX_100_STOCKS

    # Get Trading Goers stocks
    trading_goers = get_trading_goers_stocks()

    # Create new dictionary with Trading Goers as first sector
    updated_sectors = {
        'Trading Goers': trading_goers,
        **ASX_100_STOCKS  # Add all existing sectors
    }

    return updated_sectors


# Function to refresh sectors in session state
def refresh_sectors():
    """Refresh sectors and update session state."""
    updated_sectors = update_sector_dictionary()

    # Update session state
    if 'selected_sector' not in st.session_state or st.session_state.selected_sector not in updated_sectors:
        st.session_state.selected_sector = list(updated_sectors.keys())[0]

    # If current stock is not in the selected sector's stocks, reset to first stock in sector
    current_sector_stocks = updated_sectors[st.session_state.selected_sector]
    if 'selected_stock' not in st.session_state or st.session_state.selected_stock not in current_sector_stocks:
        st.session_state.selected_stock = current_sector_stocks[0] if current_sector_stocks else \
        list(updated_sectors.values())[0][0]

    return updated_sectors


def display_trading_signals():
    """Display trading signals for Trading Goers with multiple timeframes."""
    signals = get_trading_goers_signals()

    if not signals:
        st.warning("No trading signals found.")
        return

    signals_df = pd.DataFrame(signals)
    signals_df['timestamp'] = pd.to_datetime(signals_df['timestamp'])

    # Sort by timestamp (descending) and then by stock and timeframe
    signals_df = signals_df.sort_values(['timestamp', 'stock', 'timeframe'],
                                        ascending=[False, True, True])

    st.header("🚨 Trading Goers Signals")

    # Group signals by stock to show multiple timeframes together
    current_stock = None

    for _, signal in signals_df.iterrows():
        if current_stock != signal['stock']:
            if current_stock is not None:
                st.markdown("---")  # Add separator between stocks
            current_stock = signal['stock']
            st.subheader(f"Stock: {current_stock}")

        color = "green" if signal['type'] == 'BUY' else "red"
        icon = "🟢" if signal['type'] == 'BUY' else "🔴"

        signal_message = (
            f"{icon} **{signal['type']} Signal** "
            f"({signal['timeframe']} timeframe) "
            f"on {signal['timestamp'].strftime('%Y-%m-%d')} "
            f"at ${signal['price']:.2f}\n"
            f"*Strategy: {signal['strategy']}*\n\n"
            f"*{signal['message']}*"
        )

        st.markdown(f"<div style='color: {color};'>", unsafe_allow_html=True)
        st.markdown(signal_message)
        st.markdown("</div>", unsafe_allow_html=True)
        st.divider()


# Add these functions with the other functions, before the UI code
def backtest_gann_swing_strategy(data, swing_points, initial_capital=10000, position_size_pct=1):
    """
    Backtest the Gann Swing trading strategy with improved signal detection.
    """
    results = BacktestResults(initial_capital=initial_capital)
    fixed_position_value = initial_capital * position_size_pct

    if len(swing_points) < 3:
        return results

    swing_df = pd.DataFrame(swing_points, columns=['date', 'price', 'type'])
    swing_df = swing_df.sort_values('date')

    def find_last_two_swings(current_date, swing_type):
        past_swings = swing_df[
            (swing_df['date'] <= current_date) &
            (swing_df['type'] == swing_type)
            ].tail(2)
        return past_swings if len(past_swings) == 2 else None

    def check_higher_trough(current_date):
        last_lows = find_last_two_swings(current_date, 'low')
        if last_lows is None:
            return None, None

        last_high = swing_df[
            (swing_df['date'] > last_lows.iloc[0]['date']) &
            (swing_df['date'] < last_lows.iloc[1]['date']) &
            (swing_df['type'] == 'high')
            ]

        if len(last_high) > 0:
            prev_low = last_lows.iloc[0]['price']
            current_low = last_lows.iloc[1]['price']
            high_price = last_high.iloc[-1]['price']

            if current_low > prev_low:
                return high_price + 0.01, high_price

        return None, None

    def check_lower_peak(current_date):
        last_highs = find_last_two_swings(current_date, 'high')
        if last_highs is None:
            return None, None

        last_low = swing_df[
            (swing_df['date'] > last_highs.iloc[0]['date']) &
            (swing_df['date'] < last_highs.iloc[1]['date']) &
            (swing_df['type'] == 'low')
            ]

        if len(last_low) > 0:
            prev_high = last_highs.iloc[0]['price']
            current_high = last_highs.iloc[1]['price']
            low_price = last_low.iloc[-1]['price']

            if current_high < prev_high:
                return low_price - 0.01, low_price

        return None, None

    for i in range(2, len(data)):
        current_date = data.index[i]
        current_price = data['High'].iloc[i]
        current_low = data['Low'].iloc[i]

        if not results.current_position:
            buy_trigger, pattern_high = check_higher_trough(current_date)
            if buy_trigger is not None and current_price >= buy_trigger:
                shares = int(fixed_position_value / buy_trigger)
                if shares > 0:
                    results.open_position(current_date, buy_trigger, shares)

        elif results.current_position:
            sell_trigger, pattern_low = check_lower_peak(current_date)
            if sell_trigger is not None and current_low <= sell_trigger:
                results.close_position(current_date, sell_trigger)

        results.update_equity(current_date, data['Close'].iloc[i])

    return results


def backtest_trendline_strategy(data, initial_capital=10000, position_size_pct=1, min_bars=12):
    """
    Backtest trading strategy based on trend line analysis.
    """
    results = BacktestResults(initial_capital=initial_capital)
    if len(data) < min_bars:
        return results

    def calculate_stop_loss(trend_type, entry_price, atr):
        atr_multiplier = 2.0
        if trend_type == 'uptrend':
            return entry_price - (atr * atr_multiplier)
        else:
            return entry_price + (atr * atr_multiplier)

    def calculate_atr(data, period=14):
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()

    data['ATR'] = calculate_atr(data)
    active_position = {'trend': None, 'stop_loss': None, 'entry_price': None}

    def should_enter_trade(current_bar, trend):
        """
        Determine if we should enter a trade based on trend line analysis
        """
        if trend['type'] == 'uptrend':
            # Enter long when price breaks above the trend line's end point
            return (current_bar['Close'] > trend['end_price'] and
                    current_bar['Close'] > current_bar['Open'])
        elif trend['type'] == 'downtrend':
            # Enter short when price breaks below the trend line's end point
            return (current_bar['Close'] < trend['end_price'] and
                    current_bar['Close'] < current_bar['Open'])
        return False

    def should_exit_trade(current_bar, position_details, current_trends):
        """
        Determine if we should exit a trade based on trend line breaks and stop loss
        """
        if not position_details['trend']:
            return False

        # Check stop loss
        if position_details['trend'] == 'uptrend':
            if current_bar['Low'] < position_details['stop_loss']:
                return True
        else:
            if current_bar['High'] > position_details['stop_loss']:
                return True

        # Check for trend reversal
        if current_trends:
            latest_trend = current_trends[-1]
            if latest_trend['type'] != position_details['trend']:
                if (latest_trend['type'] == 'downtrend' and
                        current_bar['Low'] < latest_trend['end_price']):
                    return True
                elif (latest_trend['type'] == 'uptrend' and
                      current_bar['High'] > latest_trend['end_price']):
                    return True

        return False

    for i in range(min_bars, len(data)):
        current_date = data.index[i]
        current_bar = data.iloc[i]
        current_data = data.iloc[:i + 1]

        # Use the new identify_valid_trendlines function
        active_trends = identify_valid_trendlines(current_data, min_bars=min_bars)

        if not active_trends:
            continue

        available_capital = results.cash
        position_value = available_capital * position_size_pct
        potential_shares = int(position_value / current_bar['Close'])

        # Handle existing position
        if results.current_position:
            if should_exit_trade(current_bar, active_position, active_trends):
                exit_price = (min(current_bar['Open'], active_position['stop_loss'])
                              if active_position['trend'] == 'uptrend'
                              else max(current_bar['Open'], active_position['stop_loss']))

                results.close_position(current_date, exit_price)
                active_position['trend'] = None
                active_position['stop_loss'] = None
                active_position['entry_price'] = None

        # Handle new position entry
        elif potential_shares > 0 and active_trends:
            latest_trend = active_trends[-1]
            if should_enter_trade(current_bar, latest_trend):
                entry_price = current_bar['Open']
                stop_loss = calculate_stop_loss(
                    latest_trend['type'],
                    entry_price,
                    current_bar['ATR']
                )

                results.open_position(current_date, entry_price, potential_shares)
                active_position['trend'] = latest_trend['type']
                active_position['stop_loss'] = stop_loss
                active_position['entry_price'] = entry_price

        results.update_equity(current_date, current_bar['Close'])

    return results


# 6. VISUALIZATION FUNCTIONS
def create_ohlc_chart(data, show_swing_lines=True):
    """Create OHLC chart with swing line implementation (no point markers)"""
    if data is None or len(data) < 2:
        st.warning("Insufficient data for chart creation")
        return None

    # Ensure index is datetime
    data.index = pd.to_datetime(data.index)

    # Create base chart
    fig = go.Figure()

    # Add OHLC bars
    fig.add_trace(
        go.Ohlc(
            x=data.index,
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            name='OHLC',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350'
        )
    )

    # Add Gann swing lines if enabled
    if show_swing_lines:
        df_with_swings, swing_points = calculate_gann_swing(data)

        if swing_points and len(swing_points) > 1:
            # Sort swing points by date to ensure proper line connection
            swing_points.sort(key=lambda x: x[0])

            # Create arrays for line coordinates
            dates = [point[0] for point in swing_points]
            prices = [point[1] for point in swing_points]

            # Add only the swing line, without point markers
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=prices,
                    mode='lines',
                    line=dict(
                        color='rgba(0, 128, 255, 0.8)',
                        width=2,
                        dash='solid'
                    ),
                    name='Swing Line',
                    showlegend=True
                )
            )

    # Update layout
    fig.update_layout(
        title='Stock Price Chart',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            type='date',
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        margin=dict(b=40),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)"
        )
    )

    return fig


def create_strategy_specific_chart(df, strategy, min_trend_bars=12):
    """
    Create a chart with strategy-specific visualizations

    Args:
        df: DataFrame with OHLC data
        strategy: Strategy enum value (SWING or TRENDLINE)
        min_trend_bars: Minimum bars for trend line identification
    """
    if df is None or len(df) < 2:
        return None

    # Create base chart
    fig = go.Figure()

    # Add OHLC bars
    fig.add_trace(
        go.Ohlc(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='OHLC',
            increasing_line_color='#26A69A',
            decreasing_line_color='#EF5350'
        )
    )

    # Add strategy-specific visualizations
    if strategy == Strategy.SWING.value:
        # Add Gann swing lines
        _, swing_points = calculate_gann_swing(df)
        if swing_points and len(swing_points) > 1:
            # Sort swing points by date
            swing_points.sort(key=lambda x: x[0])

            # Create arrays for line coordinates
            dates = [point[0] for point in swing_points]
            prices = [point[1] for point in swing_points]

            # Add swing line
            fig.add_trace(
                go.Scatter(
                    x=dates,
                    y=prices,
                    mode='lines',
                    line=dict(
                        color='rgba(0, 128, 255, 0.8)',
                        width=2,
                        dash='solid'
                    ),
                    name='Swing Line'
                )
            )

    elif strategy == Strategy.TRENDLINE.value:
        # Add trend lines
        trends = identify_valid_trendlines(df, min_bars=min_trend_bars)
        if trends:
            for trend in trends:
                dates = [point[0] for point in trend['points']]
                prices = [point[1] for point in trend['points']]

                # Add trend line
                fig.add_trace(
                    go.Scatter(
                        x=dates,
                        y=prices,
                        mode='lines',
                        line=dict(
                            color='green' if trend['type'] == 'uptrend' else 'red',
                            width=2,
                            dash='solid'
                        ),
                        name=f"{trend['type'].capitalize()} Line"
                    )
                )

                # Add first three points used to create the trend line
                fig.add_trace(
                    go.Scatter(
                        x=dates[:3],
                        y=prices[:3],
                        mode='markers',
                        marker=dict(
                            color='green' if trend['type'] == 'uptrend' else 'red',
                            size=8,
                            symbol='circle'
                        ),
                        name=f"{trend['type'].capitalize()} Points"
                    )
                )

    # Update layout
    fig.update_layout(
        title=f'Price Chart with {strategy} Analysis',
        xaxis_title='Date',
        yaxis_title='Price',
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            type='date',
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)',
            rangeslider=dict(visible=False)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255, 255, 255, 0.1)'
        ),
        margin=dict(b=40),
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01,
            bgcolor="rgba(0,0,0,0.5)"
        )
    )

    return fig

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def log_backtest_result(stock, period, timeframe, initial_capital, position_size_pct, results):
    """
    Log backtest results with fixed win rate comparison.
    """
    try:
        # Calculate performance metrics
        total_trades = len(results.trades)
        if total_trades < 4:  # Minimum trade requirement
            print(f"Skipping {stock} ({timeframe}): Not enough trades ({total_trades})")
            return False, "Insufficient trades"

        winning_trades = len([t for t in results.trades if t['profit'] > 0])
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        print(f"Debug: Calculated win rate: {win_rate:.2f}%")

        # Changed comparison to include exactly 60%
        if win_rate < 59.99:  # Using 59.99 to handle floating point imprecision
            print(f"Skipping {stock} ({timeframe}): Win rate too low ({win_rate:.2f}%)")
            return False, "Low win rate"

        total_profit = sum(t['profit'] for t in results.trades)
        profit_percentage = (total_profit / initial_capital) * 100
        max_drawdown = calculate_max_drawdown(results.equity_curve)
        avg_trade_duration = calculate_avg_trade_duration(results.trades)

        # Prepare new log entry
        new_log_entry = {
            'timestamp': datetime.now().isoformat(),
            'stock': stock,
            'period': period,
            'timeframe': timeframe,
            'initial_capital': initial_capital,
            'position_size_pct': position_size_pct,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_profit': total_profit,
            'profit_percentage': profit_percentage,
            'max_drawdown': max_drawdown,
            'avg_trade_duration': avg_trade_duration,
            'trades': results.trades,
            'current_position': results.current_position,
            'equity_curve': results.equity_curve
        }

        # Load existing logs
        logs = load_existing_logs()

        # Find existing entries for this stock and timeframe
        existing_logs = [
            log for log in logs
            if log['stock'] == stock and log['timeframe'] == timeframe
        ]

        should_update = True
        if existing_logs:
            best_existing = max(
                existing_logs,
                key=lambda x: (x.get('win_rate', 0), x.get('total_profit', 0))
            )

            # Only update if new performance is better
            if (best_existing['win_rate'] > win_rate or
                    (abs(best_existing['win_rate'] - win_rate) < 0.01 and  # Handle equal win rates
                     best_existing['total_profit'] >= total_profit)):
                should_update = False
                print(f"Skipping {stock} ({timeframe}): Existing performance is better")
                return False, "Existing performance is better"

        if should_update:
            # Remove existing logs for this stock/timeframe combination
            logs = [
                log for log in logs
                if not (log['stock'] == stock and log['timeframe'] == timeframe)
            ]
            # Add new log
            logs.append(new_log_entry)

            # Save updated logs
            save_logs(logs)
            print(f"Successfully logged backtest for {stock} ({timeframe})")
            return True, "Successfully logged backtest"

        return False, "No update needed"

    except Exception as e:
        print(f"Error in backtest logging: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return False, str(e)


def save_logs(logs):
    """Save logs with error handling but maintain existing format."""
    try:
        os.makedirs('backtest_logs', exist_ok=True)
        temp_file = 'backtest_logs/backtest_log_temp.json'
        backup_file = 'backtest_logs/backtest_log_backup.json'
        target_file = 'backtest_logs/backtest_log.json'

        # First write to temporary file
        with open(temp_file, 'w') as f:
            json.dump(logs, f, indent=4, default=json_serial)

        # If successful, create backup of current file if it exists
        if os.path.exists(target_file):
            shutil.copy2(target_file, backup_file)

        # Then rename temp file to actual file
        shutil.move(temp_file, target_file)
        return True
    except Exception as e:
        print(f"Error saving logs: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        # If we have a backup, restore it
        if os.path.exists(backup_file):
            try:
                shutil.copy2(backup_file, target_file)
                print("Restored backup file after save error")
            except Exception as restore_error:
                print(f"Error restoring backup: {restore_error}")
        return False


def load_existing_logs():
    """Load and parse existing backtest logs with improved error handling."""
    try:
        os.makedirs('backtest_logs', exist_ok=True)
        log_file = 'backtest_logs/backtest_log.json'

        if not os.path.exists(log_file):
            return []

        with open(log_file, 'r') as f:
            logs = json.load(f)

        # Basic validation without modifying the data
        validated_logs = []
        for log in logs:
            if isinstance(log, dict) and 'stock' in log and 'timeframe' in log:
                validated_logs.append(log)
            else:
                print(f"Skipping invalid log entry: {log}")

        return validated_logs
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading logs: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error loading logs: {e}")
        print(f"Stack trace: {traceback.format_exc()}")
        return []


def get_backtest_logs():
    """
    Retrieve and filter backtest logs with backwards compatibility.
    Only weekly and monthly timeframes, win rate > 60%, minimum 4 trades.
    """
    logs = load_existing_logs()

    filtered_logs = []
    for log in logs:
        try:
            # Basic validation of required fields
            if not all(key in log for key in ['timeframe', 'total_trades', 'win_rate']):
                continue

            if (log['timeframe'].lower() in ['weekly', 'monthly'] and
                    log['total_trades'] >= 4 and
                    log['win_rate'] > 59):
                filtered_logs.append(log)
        except Exception as e:
            print(f"Error processing log entry: {e}")
            continue

    return sorted(
        filtered_logs,
        key=lambda x: (-x.get('win_rate', 0), -x.get('total_profit', 0))
    )


def calculate_avg_trade_duration(trades):
    """Calculate average trade duration in days"""
    durations = []
    for trade in trades:
        if trade['exit_date'] != 'OPEN' and trade['entry_date'] and trade['exit_date']:
            entry = pd.to_datetime(trade['entry_date'])
            exit = pd.to_datetime(trade['exit_date'])
            duration = (exit - entry).days
            durations.append(duration)
    return sum(durations) / len(durations) if durations else 0

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


# 7. BACKTEST RESULTS CLASS
class BacktestResults:
    def __init__(self, initial_capital=10000):
        self.trades = []  # List to store all trades
        self.positions = []
        self.current_position = None
        self.cash = initial_capital
        self.initial_capital = initial_capital
        self.portfolio_value = self.cash
        self.equity_curve = []

    def open_position(self, date, price, shares):
        self.current_position = {
            'entry_date': date,
            'entry_price': price,
            'shares': shares,
            'cost': price * shares
        }
        self.cash -= price * shares
        self.positions.append(self.current_position)
        self.update_equity(date, price)

    def close_position(self, date, price):
        if self.current_position:
            profit = (price - self.current_position['entry_price']) * self.current_position['shares']
            self.cash += (price * self.current_position['shares'])

            trade = {
                'entry_date': self.current_position['entry_date'],
                'entry_price': self.current_position['entry_price'],
                'exit_date': date,
                'exit_price': price,
                'shares': self.current_position['shares'],
                'profit': profit,
                'return_pct': (profit / self.current_position['cost']) * 100
            }

            self.trades.append(trade)
            self.current_position = None
            self.update_equity(date, price)

    def update_equity(self, date, current_price):
        if self.current_position:
            position_value = current_price * self.current_position['shares']
            self.portfolio_value = self.cash + position_value
        else:
            self.portfolio_value = self.cash

        self.equity_curve.append({
            'date': date,
            'portfolio_value': self.portfolio_value
        })


# 8. MAIN APP UI LOGIC
def main():
    # Initialize price update manager if not exists
    if 'price_manager' not in st.session_state:
        st.session_state.price_manager = PriceUpdateManager()
        st.session_state.price_manager.start_updates()

        initialize_price_update_manager()

    # Process any pending price updates
    process_price_updates()

    # Show notifications if enabled
    if st.session_state.show_notifications:
        st.info(st.session_state.notification_message)
        # Clear notification after showing
        st.session_state.show_notifications = False
        st.session_state.notification_message = ""

    # Rest of your existing main() function code...
    period_days = time_periods[st.session_state.selected_period]
    df = get_stock_data(st.session_state.selected_stock, period=period_days,
                        timeframe=st.session_state.selected_timeframe)

    if df is not None and len(df) > 0:
        try:
            stock = yf.Ticker(f"{st.session_state.selected_stock}.AX")
            info = stock.info
            current_price = df['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            price_change = current_price - previous_close
            change_color = "green" if price_change >= 0 else "red"
            metrics = get_stock_metrics(st.session_state.selected_stock)

            with col2:
                stock = yf.Ticker(f"{st.session_state.selected_stock}.AX")
                company_name = stock.info.get("longName", st.session_state.selected_stock)

                st.markdown(
                    f"""
                    <h2 style='text-align: center'>📌 {st.session_state.selected_stock}</h2>
                    <p style='text-align: center; font-size: 1.2em; color: grey;'>{company_name}</p>
                    """,
                    unsafe_allow_html=True
                )

                price_cols = st.columns([1, 1])
                with price_cols[0]:
                    st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
                    st.markdown(
                        f"<p style='margin: 0; font-size: 18px; color: #666;'>Current Price</p>"
                        f"<p style='font-size: 28px; font-weight: bold; margin: 0;'>${current_price:.2f}</p>",
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)
                with price_cols[1]:
                    st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
                    st.markdown(
                        f"<div style='padding: 5px;'>"
                        f"<p style='margin: 0; font-size: 18px; color: #666;'>Change (Today)</p>"
                        f"<p style='color: {change_color}; font-size: 28px; font-weight: bold; margin: 0;'>"
                        f"${price_change:+.2f}</p>"
                        f"</div>",
                        unsafe_allow_html=True
                    )
                    st.markdown("</div>", unsafe_allow_html=True)

                if metrics:
                    st.markdown("---")
                    st.markdown("<h3 style='text-align: center'>📊 Market Metrics</h3>", unsafe_allow_html=True)
                    metric_cols = st.columns(4)

                    with metric_cols[0]:
                        st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
                        st.metric("ASX Ranking", metrics.get("ASX Ranking", "N/A"))
                        st.markdown("</div>", unsafe_allow_html=True)

                    with metric_cols[1]:
                        st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
                        current_eps = metrics.get("EPS Current", "N/A")
                        if current_eps != "N/A":
                            current_eps = f"${current_eps:.2f}"
                        st.metric("Current EPS", current_eps)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with metric_cols[2]:
                        st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
                        pe_ratio = metrics.get("P/E Ratio", "N/A")
                        if pe_ratio != "N/A":
                            pe_ratio = f"{float(pe_ratio):.2f}"
                        st.metric("P/E Ratio", pe_ratio)
                        st.markdown("</div>", unsafe_allow_html=True)

                    with metric_cols[3]:
                        st.markdown("<div style='text-align: center'>", unsafe_allow_html=True)
                        st.metric("Dividend Yield", metrics.get("Dividend Yield", "N/A"))
                        st.markdown("</div>", unsafe_allow_html=True)

                st.markdown("---")

                fig = create_ohlc_chart(df)
                if fig is not None:
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        config={
                            'scrollZoom': True,
                            'displaylogo': False,
                            'modeBarButtonsToAdd': [
                                'drawline',
                                'drawopenpath',
                                'eraseshape',
                                'pan',
                                'zoom',
                                'select2d',
                                'lasso2d',
                                'zoomIn2d''zoomOut2d',
                                'autoScale2d',
                                'resetScale2d'
                            ],
                            'modeBarButtonsToRemove': [],
                            'dragmode': 'zoom'
                        }
                    )

        except Exception as e:
            st.error(f"Error displaying price data: {str(e)}")
            return
    else:
        st.warning("No data available for the selected stock and date range.")


def display_backtest_results(results):
    """Display backtest results in Streamlit"""
    st.subheader("Backtest Results")

    total_trades = len(results.trades)
    if results.current_position:
        total_trades += 1

    winning_trades = len([t for t in results.trades if t['profit'] > 0])
    losing_trades = len([t for t in results.trades if t['profit'] <= 0])
    open_trades = 1 if results.current_position else 0

    win_rate = (winning_trades / len(results.trades) * 100) if results.trades else 0

    winning_returns = [t['return_pct'] for t in results.trades if t['profit'] > 0]
    losing_returns = [t['return_pct'] for t in results.trades if t['profit'] <= 0]

    avg_win = sum(winning_returns) / len(winning_returns) if winning_returns else 0
    avg_loss = sum(losing_returns) / len(losing_returns) if losing_returns else 0

    realized_profit = sum(t['profit'] for t in results.trades)
    unrealized_profit = 0 if not results.current_position else (
            results.portfolio_value - results.cash - results.current_position['cost'])
    total_profit = realized_profit + unrealized_profit

    total_outlaid = sum(t['entry_price'] * t['shares'] for t in results.trades)
    if results.current_position:
        total_outlaid += results.current_position['cost']
    profit_on_outlaid = (total_profit / total_outlaid * 100) if total_outlaid > 0 else 0

    trade_durations = []
    for trade in results.trades:
        duration = (trade['exit_date'] - trade['entry_date']).days
        trade_durations.append(duration)
    avg_days = int(sum(trade_durations) / len(trade_durations)) if trade_durations else 0

    st.write("### Trading Performance Summary")
    summary_data = {
        "Metric": [
            "Total Trades", "Winning Trades", "Losing Trades", "Open Trades",
            "Win Rate %", "Av Profit on Winning Trades %", "Av Loss on Losing Trades %",
            "Net Overall Profit (Loss)", "Total $ Net Overall Profit (Loss) on Money Outlaid %",
            "Av Cal Days in Trade"
        ],
        "Value": [
            total_trades,
            winning_trades,
            losing_trades,
            open_trades,
            f"{win_rate:.2f}%",
            f"{avg_win:.2f}%",
            f"{avg_loss:.2f}%",
            f"${total_profit:,.2f}",
            f"{profit_on_outlaid:.2f}%",
            avg_days
        ]
    }

    summary_df = pd.DataFrame(summary_data)
    st.dataframe(
        summary_df,
        hide_index=True,
        column_config={
            "Metric": "Metric",
            "Value": "Value"
        },
        use_container_width=True
    )

    if total_trades > 0:
        equity_container = st.container()
        with equity_container:
            equity_df = pd.DataFrame(results.equity_curve)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=equity_df['date'],
                y=equity_df['portfolio_value'],
                mode='lines',
                name='Portfolio Value'
            ))
            fig.update_layout(
                title="Portfolio Equity Curve",
                xaxis_title="Date",
                yaxis_title="Portfolio Value ($)",
                template="plotly_dark",
                dragmode='zoom',
                xaxis=dict(fixedrange=False),
                yaxis=dict(fixedrange=False)
            )
            st.plotly_chart(
                fig,
                use_container_width=True,
                config={
                    'scrollZoom': True,
                    'displaylogo': False,
                    'modeBarButtonsToAdd': [
                        'drawline',
                        'drawopenpath',
                        'eraseshape',
                        'pan',
                        'zoom',
                        'select2d',
                        'lasso2d',
                        'zoomIn2d',
                        'zoomOut2d',
                        'autoScale2d',
                        'resetScale2d'
                    ],
                    'modeBarButtonsToRemove': [],
                    'dragmode': 'zoom'
                }
            )

        trade_list_container = st.container()
        with trade_list_container:
            with st.expander("Trade List", expanded=True):
                trades_list = []
                if results.trades:
                    trades_list.extend(results.trades)

                if results.current_position:
                    open_trade = {
                        'entry_date': results.current_position['entry_date'],
                        'entry_price': results.current_position['entry_price'],
                        'exit_date': 'OPEN',
                        'exit_price': None,
                        'shares': results.current_position['shares'],
                        'profit': None,
                        'return_pct': None
                    }
                    trades_list.append(open_trade)

                if trades_list:
                    trade_df = pd.DataFrame(trades_list)
                    trade_df['entry_date'] = pd.to_datetime(trade_df['entry_date']).dt.strftime('%Y-%m-%d')
                    trade_df['exit_date'] = trade_df['exit_date'].apply(
                        lambda x: pd.to_datetime(x).strftime('%Y-%m-%d') if x != 'OPEN' else 'OPEN'
                    )
                    for col in ['profit', 'return_pct', 'entry_price', 'exit_price']:
                        trade_df[col] = trade_df[col].apply(lambda x: round(x, 2) if pd.notnull(x) else '')

                    def style_trades(val):
                        try:
                            if val['exit_date'] == 'OPEN':
                                return ['background-color: rgba(80, 80, 80, 1.0)'] * len(val)
                            elif isinstance(val['profit'], (int, float)) and not pd.isna(val['profit']):
                                return ['background-color: rgba(0, 140, 35, 1.0)'] * len(val) if val[
                                                                                                     'profit'] > 0 else [
                                                                                                                            'background-color: rgba(180, 50, 50, 1.0)'] * len(
                                    val)
                            else:
                                return [''] * len(val)
                        except:
                            return [''] * len(val)

                    styled_df = trade_df.style.apply(style_trades, axis=1)

                    st.dataframe(
                        styled_df,
                        column_config={
                            'entry_date': 'Entry Date',
                            'exit_date': 'Exit Date',
                            'entry_price': st.column_config.NumberColumn('Entry Price', format="$%.2f"),
                            'exit_price': st.column_config.NumberColumn('Exit Price', format="$%.2f"),
                            'shares': 'Shares',
                            'profit': st.column_config.NumberColumn('Profit/Loss', format="$%.2f"),
                            'return_pct': st.column_config.NumberColumn('Return %', format="%.2f%%")
                        },
                        use_container_width=True
                    )
    else:
        st.warning("No trades were executed during the backtest period.")


def display_individual_trades(trades_df):
    """Display individual trades in an expandable format."""
    for idx, trade in trades_df.iterrows():
        with st.expander(f"Trade {idx + 1}: {trade['entry_date']} to {trade['exit_date']}", expanded=False):
            entry_col, exit_col = st.columns(2)

            with entry_col:
                st.markdown("#### 📈 Entry")
                st.markdown(f"**Date:** {trade['entry_date']}")
                st.markdown(f"**Price:** ${trade['entry_price']:.2f}")
                st.markdown(f"**Shares:** {trade['shares']}")
                st.markdown(f"**Strategy:** {trade['strategy']}")
                st.markdown(f"**Timeframe:** {trade['timeframe']}")

            with exit_col:
                st.markdown("#### 📉 Exit")
                st.markdown(f"**Date:** {trade['exit_date']}")
                st.markdown(f"**Price:** ${trade['exit_price']:.2f}")
                profit_color = "green" if trade['profit'] > 0 else "red"
                st.markdown(f"**Profit/Loss:** :{profit_color}[${trade['profit']:.2f}]")
                st.markdown(f"**Return:** :{profit_color}[{trade['return_pct']:.2f}%]")
                st.markdown(f"**Win Rate:** {trade['win_rate']:.1f}%")

            st.markdown("---")


def display_stock_trade_list(stock, backtest_logs):
    """Display detailed trade list for a specific stock."""
    st.subheader(f"📊 Trade List for {stock}")

    stock_logs = [log for log in backtest_logs if log['stock'] == stock]

    if not stock_logs:
        st.warning(f"No trade data found for {stock}")
        return

    all_trades = []
    for log in stock_logs:
        if 'trades' in log:
            for trade in log['trades']:
                trade_info = {
                    'Timeframe': log['timeframe'],
                    'Strategy': "Gann Swing" if log['timeframe'] == "Weekly" else "Trendline",
                    'Entry Date': trade['entry_date'],
                    'Entry Price': trade['entry_price'],
                    'Exit Date': trade['exit_date'],
                    'Exit Price': trade['exit_price'],
                    'Shares': trade['shares'],
                    'Profit': trade['profit'],
                    'Return %': trade['return_pct']
                }
                all_trades.append(trade_info)

    if not all_trades:
        st.warning("No trades found for this stock")
        return

    trades_df = pd.DataFrame(all_trades)
    trades_df = trades_df.sort_values('Entry Date', ascending=False)

    # Display trade summary
    total_trades = len(trades_df)
    winning_trades = len(trades_df[trades_df['Profit'] > 0])
    total_profit = trades_df['Profit'].sum()
    avg_return = trades_df['Return %'].mean()
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Trades", total_trades)
    col2.metric("Winning Trades", winning_trades)
    col3.metric("Win Rate", f"{win_rate:.1f}%")
    col4.metric("Total Profit", f"${total_profit:,.2f}")
    col5.metric("Average Return", f"{avg_return:.1f}%")

    # Display full trade list
    st.subheader("Detailed Trade List")
    st.dataframe(
        trades_df,
        column_config={
            'Entry Date': 'Entry Date',
            'Exit Date': 'Exit Date',
            'Entry Price': st.column_config.NumberColumn('Entry Price', format="$%.2f"),
            'Exit Price': st.column_config.NumberColumn('Exit Price', format="$%.2f"),
            'Profit': st.column_config.NumberColumn('Profit', format="$%.2f"),
            'Return %': st.column_config.NumberColumn('Return %', format="%.2f%%")
        },
        use_container_width=True
    )

    # Download button for CSV
    csv = trades_df.to_csv(index=False)
    st.download_button(
        label="Download Trade List as CSV",
        data=csv,
        file_name=f"{stock}_trades.csv",
        mime="text/csv"
    )


    # Style function for trades
    def style_trades(trades):
        # Color coding for profit/loss
        styles = []
        for _, trade in trades.iterrows():
            if trade['profit'] > 0:
                style = 'background-color: rgba(0, 255, 0, 0.1)'
            else:
                style = 'background-color: rgba(255, 0, 0, 0.1)'
            styles.append(style)
        return styles

    # Styled dataframe
    styled_trades = trades_df.style.apply(style_trades, axis=1)

    st.dataframe(
        styled_trades,
        column_config={
            'entry_date': 'Entry Date',
            'exit_date': 'Exit Date',
            'entry_price': st.column_config.NumberColumn('Entry Price', format="$%.2f"),
            'exit_price': st.column_config.NumberColumn('Exit Price', format="$%.2f"),
            'profit': st.column_config.NumberColumn('Profit', format="$%.2f"),
            'return_pct': st.column_config.NumberColumn('Return %', format="%.2f%%"),
            'win_rate': st.column_config.NumberColumn('Win Rate %', format="%.1f%%")
        },
        use_container_width=True
    )

    # Download button
    csv = trades_df.to_csv(index=False)
    st.download_button(
        label="Download Trade List as CSV",
        data=csv,
        file_name=f"{stock}_trades.csv",
        mime="text/csv"
    )

    # Optional: Profit Distribution Chart
    st.subheader("Profit Distribution")
    fig = go.Figure([
        go.Histogram(x=trades_df['profit'], nbinsx=20, name='Profit Distribution')
    ])
    fig.update_layout(
        title='Distribution of Trade Profits',
        xaxis_title='Profit ($)',
        yaxis_title='Frequency',
        template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)


def render_backtest_logs_tab():
    """Display backtest logs with both summary and trade details."""
    st.header("🔍 Backtest Performance Logs")

    # Add reset button in a container at the top
    reset_container = st.container()
    with reset_container:
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("🗑️ Reset Logs", type="primary", help="Clear all backtest logs data"):
                success, message = delete_all_backtest_data()
                if success:
                    st.success("Successfully reset backtest logs")
                    st.rerun()
                else:
                    st.error(f"Error resetting logs: {message}")

    backtest_logs = get_backtest_logs()

    if not backtest_logs:
        st.info("No backtest logs available. Run some backtests to populate the logs.")
        return

    summary_tab, trade_list_tab = st.tabs(["Summary View", "Trade List"])

    with summary_tab:
        st.subheader("📊 Backtest Summary")
        logs_df = pd.DataFrame(backtest_logs)
        if not logs_df.empty:
            if 'win_rate' not in logs_df.columns:
                logs_df['win_rate'] = 0

            # Sort by win rate and total profit
            logs_df = logs_df.sort_values(by=['win_rate', 'total_profit'], ascending=[False, False])

            # Display the summary with formatted columns
            st.dataframe(
                logs_df[[
                    'stock', 'timeframe', 'total_trades', 'winning_trades',
                    'win_rate', 'total_profit', 'profit_percentage'
                ]],
                column_config={
                    'stock': 'Stock',
                    'timeframe': 'Timeframe',
                    'total_trades': st.column_config.NumberColumn('Total Trades'),
                    'winning_trades': st.column_config.NumberColumn('Winning Trades'),
                    'win_rate': st.column_config.NumberColumn('Win Rate %', format="%.1f%%"),
                    'total_profit': st.column_config.NumberColumn('Total Profit', format="$%.2f"),
                    'profit_percentage': st.column_config.NumberColumn('Return %', format="%.1f%%")
                },
                use_container_width=True
            )
        else:
            st.warning("No backtest summaries available.")

    with trade_list_tab:
        st.subheader("📊 Trade List from Backtests")
        trades_list = []

        for log in backtest_logs:
            # Process closed trades
            for trade in log.get('trades', []):
                trades_list.append({
                    'Stock': log['stock'],
                    'Timeframe': log['timeframe'],
                    'Entry Date': pd.to_datetime(trade['entry_date']).strftime('%Y-%m-%d') if trade[
                        'entry_date'] else 'N/A',
                    'Entry Price': trade['entry_price'],
                    'Exit Date': pd.to_datetime(trade['exit_date']).strftime('%Y-%m-%d') if trade['exit_date'] and
                                                                                            trade[
                                                                                                'exit_date'] != 'OPEN' else 'OPEN',
                    'Exit Price': trade['exit_price'] if trade['exit_date'] != 'OPEN' else None,
                    'Shares': trade['shares'],
                    'Profit': trade['profit'] if trade['exit_date'] != 'OPEN' else None,
                    'Return %': trade['return_pct'] if trade['exit_date'] != 'OPEN' else None,
                    'Status': 'Closed' if trade['exit_date'] != 'OPEN' else 'Open'
                })

            # Process open position if it exists
            if log.get('current_position'):
                current_pos = log['current_position']
                trades_list.append({
                    'Stock': log['stock'],
                    'Timeframe': log['timeframe'],
                    'Entry Date': pd.to_datetime(current_pos['entry_date']).strftime('%Y-%m-%d') if current_pos[
                        'entry_date'] else 'N/A',
                    'Entry Price': current_pos['entry_price'],
                    'Exit Date': 'OPEN',
                    'Exit Price': None,
                    'Shares': current_pos['shares'],
                    'Profit': None,
                    'Return %': None,
                    'Status': 'Open'
                })

        if trades_list:
            trades_df = pd.DataFrame(trades_list)
            trades_df = trades_df.sort_values(['Entry Date', 'Stock'], ascending=[False, True])

            # Style function for trades DataFrame
            def style_trades(row):
                if row['Status'] == 'Open':
                    return ['background-color: rgba(255, 165, 0, 0.1)'] * len(row)
                elif pd.notnull(row['Profit']) and row['Profit'] > 0:
                    return ['background-color: rgba(0, 255, 0, 0.1)'] * len(row)
                else:
                    return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)

            # Apply styling and display
            styled_trades = trades_df.style.apply(style_trades, axis=1)
            st.dataframe(
                styled_trades,
                column_config={
                    'Entry Price': st.column_config.NumberColumn(format="$%.2f"),
                    'Exit Price': st.column_config.NumberColumn(format="$%.2f"),
                    'Profit': st.column_config.NumberColumn(format="$%.2f"),
                    'Return %': st.column_config.NumberColumn(format="%.2f%%"),
                    'Status': 'Status'
                },
                use_container_width=True
            )

            # Add CSV download button
            csv = trades_df.to_csv(index=False)
            st.download_button(
                label="Download Trade List as CSV",
                data=csv,
                file_name="backtest_trade_list.csv",
                mime="text/csv"
            )
        else:
            st.warning("No trades found in backtest logs.")

        if selected_stock:
            # Get trades for selected stock
            stock_logs = [log for log in backtest_logs if log['stock'] == selected_stock]

            if stock_logs:
                # Combine all trades from different timeframes
                all_trades = []
                for log in stock_logs:
                    if 'trades' in log and log['trades']:
                        for trade in log['trades']:
                            trade_info = {
                                'Timeframe': log['timeframe'],
                                'Strategy': "Gann Swing" if log['timeframe'] == "Weekly" else "Trendline",
                                'Entry Date': pd.to_datetime(trade['entry_date']).strftime('%Y-%m-%d'),
                                'Entry Price': trade['entry_price'],
                                'Exit Date': trade['exit_date'] if trade['exit_date'] == 'OPEN' else pd.to_datetime(
                                    trade['exit_date']).strftime('%Y-%m-%d'),
                                'Exit Price': trade['exit_price'],
                                'Shares': trade['shares'],
                                'Profit/Loss': trade['profit'],
                                'Return %': trade['return_pct'],
                                'Win Rate': log.get('win_rate', 0)
                            }
                            all_trades.append(trade_info)

                if all_trades:
                    # Convert to DataFrame and sort by entry date
                    trades_df = pd.DataFrame(all_trades)
                    trades_df = trades_df.sort_values('Entry Date', ascending=False)

                    # Calculate summary metrics
                    total_trades = len(trades_df)
                    winning_trades = len(trades_df[trades_df['Profit/Loss'] > 0])
                    total_profit = trades_df['Profit/Loss'].sum()
                    avg_return = trades_df['Return %'].mean()
                    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

                    # Display summary metrics
                    st.subheader(f"Summary for {selected_stock}")
                    col1, col2, col3, col4, col5 = st.columns(5)

                    with col1:
                        st.metric("Total Trades", f"{total_trades}")
                    with col2:
                        st.metric("Winning Trades", f"{winning_trades}")
                    with col3:
                        st.metric("Win Rate", f"{win_rate:.1f}%")
                    with col4:
                        st.metric("Total Profit/Loss", f"${total_profit:,.2f}")
                    with col5:
                        st.metric("Average Return", f"{avg_return:.1f}%")

                    # Style function for the trades DataFrame
                    def style_detailed_trades(row):
                        color = 'background-color: rgba(0, 255, 0, 0.1)' if row[
                                                                                'Profit/Loss'] > 0 else 'background-color: rgba(255, 0, 0, 0.1)'
                        return [color] * len(row)

                    # Display full trade list with styling
                    st.subheader("Detailed Trade List")
                    styled_trades_df = trades_df.style.apply(style_detailed_trades, axis=1)

                    st.dataframe(
                        styled_trades_df,
                        column_config={
                            'Entry Price': st.column_config.NumberColumn(format="$%.2f"),
                            'Exit Price': st.column_config.NumberColumn(format="$%.2f"),
                            'Profit/Loss': st.column_config.NumberColumn(format="$%.2f"),
                            'Return %': st.column_config.NumberColumn(format="%.2f%%"),
                            'Win Rate': st.column_config.NumberColumn(format="%.1f%%")
                        },
                        use_container_width=True
                    )

                    # Add trade list download button
                    csv = trades_df.to_csv(index=False)
                    st.download_button(
                        label=f"Download {selected_stock} Trade List",
                        data=csv,
                        file_name=f"{selected_stock}_trades.csv",
                        mime="text/csv"
                    )

                    # Display trades by timeframe
                    st.subheader("Analysis by Timeframe")
                    for timeframe in trades_df['Timeframe'].unique():
                        with st.expander(f"{timeframe} Trades"):
                            timeframe_trades = trades_df[trades_df['Timeframe'] == timeframe]
                            timeframe_styled = timeframe_trades.style.apply(style_detailed_trades, axis=1)

                            # Calculate timeframe metrics
                            tf_total_trades = len(timeframe_trades)
                            tf_winning_trades = len(timeframe_trades[timeframe_trades['Profit/Loss'] > 0])
                            tf_total_profit = timeframe_trades['Profit/Loss'].sum()
                            tf_avg_return = timeframe_trades['Return %'].mean()
                            tf_win_rate = (tf_winning_trades / tf_total_trades * 100) if tf_total_trades > 0 else 0

                            # Display timeframe metrics
                            cols = st.columns(5)
                            cols[0].metric("Trades", tf_total_trades)
                            cols[1].metric("Winning", tf_winning_trades)
                            cols[2].metric("Win Rate", f"{tf_win_rate:.1f}%")
                            cols[3].metric("Total P/L", f"${tf_total_profit:,.2f}")
                            cols[4].metric("Avg Return", f"{tf_avg_return:.1f}%")

                            st.dataframe(
                                timeframe_styled,
                                column_config={
                                    'Entry Price': st.column_config.NumberColumn(format="$%.2f"),
                                    'Exit Price': st.column_config.NumberColumn(format="$%.2f"),
                                    'Profit/Loss': st.column_config.NumberColumn(format="$%.2f"),
                                    'Return %': st.column_config.NumberColumn(format="%.2f%%"),
                                    'Win Rate': st.column_config.NumberColumn(format="%.1f%%")
                                },
                                use_container_width=True
                            )
                else:
                    st.info("No trades found for this stock")
            else:
                st.info("No backtest data found for this stock")

# Add this callback function near the top of the file, before the main UI code
def update_stock_selection():
    """Update stock selection when sector changes"""
    # Get the current sector from session state
    current_sector = st.session_state.selected_sector

    # Update the selected stock to be the first stock in the new sector
    st.session_state.selected_stock = ASX_100_STOCKS[current_sector][0]


# Initialize session state
if 'show_notifications' not in st.session_state:
    st.session_state.show_notifications = False

if 'show_signals_state' not in st.session_state:
    st.session_state.show_signals_state = False

# Use single session state variables for sector and stock
if 'selected_sector' not in st.session_state:
    st.session_state.selected_sector = list(ASX_100_STOCKS.keys())[0]
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = ASX_100_STOCKS[st.session_state.selected_sector][0]
if 'selected_period' not in st.session_state:
    st.session_state.selected_period = list(time_periods.keys())[0]
if 'selected_timeframe' not in st.session_state:
    st.session_state.selected_timeframe = "Monthly"

# Initialize session state
if 'show_notifications' not in st.session_state:
    st.session_state.show_notifications = False

# Use single session state variables for sector and stock
if 'selected_sector' not in st.session_state:
    st.session_state.selected_sector = list(ASX_100_STOCKS.keys())[0]
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = ASX_100_STOCKS[st.session_state.selected_sector][0]
if 'selected_period' not in st.session_state:
    st.session_state.selected_period = list(time_periods.keys())[0]
if 'selected_timeframe' not in st.session_state:
    st.session_state.selected_timeframe = "Daily"


def sync_stock_selection(tab_prefix):
    """Synchronize stock selection across tabs"""
    # Update the selected stock based on the new sector
    current_sector = st.session_state[f'{tab_prefix}_sector']
    st.session_state.selected_sector = current_sector

    # If the current stock isn't in the new sector, select the first stock
    if st.session_state.selected_stock not in ASX_100_STOCKS[current_sector]:
        st.session_state.selected_stock = ASX_100_STOCKS[current_sector][0]
        st.session_state[f'{tab_prefix}_stock'] = st.session_state.selected_stock


def sync_stock_only(tab_prefix):
    """Synchronize individual stock selection"""
    st.session_state.selected_stock = st.session_state[f'{tab_prefix}_stock']


# First, let's add a function to get signals from backtest results
def get_signals_from_backtest(stock, period, timeframe, strategy, initial_capital=10000, position_size_pct=1):
    """Get trading signals from backtest results"""
    df = get_stock_data(stock, period=period, timeframe=timeframe)
    if df is None or len(df) == 0:
        return []

    # Run backtest based on strategy
    if strategy == Strategy.SWING.value:
        _, swing_points = calculate_gann_swing(df)
        results = backtest_gann_swing_strategy(
            df,
            swing_points,
            initial_capital=initial_capital,
            position_size_pct=position_size_pct
        )
    else:
        results = backtest_trendline_strategy(
            df,
            initial_capital=initial_capital,
            position_size_pct=position_size_pct
        )

    # Convert trades to signals
    signals = []
    for trade in results.trades:
        # Entry signal (BUY)
        signals.append({
            'type': 'BUY',
            'timestamp': trade['entry_date'],
            'price': trade['entry_price'],
            'stock': stock,
            'timeframe': timeframe,
            'strategy': strategy,
            'message': f"Entry at ${trade['entry_price']:.2f}"
        })

        # Exit signal (SELL)
        signals.append({
            'type': 'SELL',
            'timestamp': trade['exit_date'],
            'price': trade['exit_price'],
            'stock': stock,
            'timeframe': timeframe,
            'strategy': strategy,
            'message': f"Exit at ${trade['exit_price']:.2f} (Profit: ${trade['profit']:.2f})"
        })

    return signals


# Update the header container code
# Update the header container code
header_container = st.container()
with header_container:
    # Button row
    _, _, button_col = st.columns([3, 3, 1])
    with button_col:
        if st.button("📊 Show Signals", key="show_signals_button",
                     help="Toggle trading signals display",
                     type="primary" if st.session_state.show_signals_state else "secondary"):
            st.session_state.show_signals_state = not st.session_state.show_signals_state

    # Signals display using Trading Goers results
    if st.session_state.show_signals_state:
        logs = get_backtest_logs()

        if not logs:
            st.warning("No Trading Goers results found.")
        else:
            signals = []
            # Ensure current_date is timezone naive
            current_date = pd.Timestamp.now().tz_localize(None)
            thirty_days_ago = current_date - pd.DateOffset(days=30)


            def convert_to_naive_timestamp(date_str):
                """Convert a date string to a naive timestamp"""
                if not date_str or date_str == 'OPEN':
                    return None
                # Convert to timestamp and ensure it's naive
                ts = pd.to_datetime(date_str)
                if ts.tzinfo is not None:
                    ts = ts.tz_localize(None)
                return ts


            for log in logs:
                win_rate = log.get('win_rate', 0)

                if win_rate > 60:
                    stock = log['stock']
                    timeframe = log['timeframe']

                    # Process closed trades
                    if 'trades' in log and log['trades']:
                        for trade in log['trades']:
                            try:
                                entry_date = convert_to_naive_timestamp(trade['entry_date'])
                                exit_date = convert_to_naive_timestamp(trade['exit_date'])

                                # Only include trades from the last 30 days
                                should_include = False
                                if entry_date and entry_date > thirty_days_ago:
                                    should_include = True
                                elif exit_date and exit_date > thirty_days_ago:
                                    should_include = True
                                elif trade.get('exit_date') == 'OPEN':
                                    should_include = True

                                if should_include:
                                    # Entry signal
                                    signals.append({
                                        'type': 'BUY',
                                        'timestamp': entry_date,
                                        'price': trade['entry_price'],
                                        'stock': stock,
                                        'timeframe': timeframe,
                                        'strategy': "Gann Swing" if timeframe == "Weekly" else "Trendline",
                                        'shares': trade['shares'],
                                        'profit': trade.get('profit'),
                                        'return_pct': trade.get('return_pct'),
                                        'win_rate': win_rate,
                                        'status': 'OPEN' if not exit_date else 'CLOSED',
                                        'message': f"Entry at ${trade['entry_price']:.2f}"
                                    })

                                    # Exit signal (only for closed trades)
                                    if exit_date and exit_date > thirty_days_ago:
                                        signals.append({
                                            'type': 'SELL',
                                            'timestamp': exit_date,
                                            'price': trade['exit_price'],
                                            'stock': stock,
                                            'timeframe': timeframe,
                                            'strategy': "Gann Swing" if timeframe == "Weekly" else "Trendline",
                                            'shares': trade['shares'],
                                            'profit': trade.get('profit'),
                                            'return_pct': trade.get('return_pct'),
                                            'win_rate': win_rate,
                                            'status': 'CLOSED',
                                            'message': f"Exit at ${trade['exit_price']:.2f} (Profit: ${trade.get('profit', 0):.2f}, Return: {trade.get('return_pct', 0):.2f}%)"
                                        })
                            except Exception as e:
                                print(
                                    f"Error processing trade: {e}")  # Using print instead of st.write for cleaner output

                    # Process current (open) position
                    if log.get('current_position'):
                        current_pos = log['current_position']
                        try:
                            entry_date = convert_to_naive_timestamp(current_pos['entry_date'])

                            if entry_date and entry_date > thirty_days_ago:
                                signals.append({
                                    'type': 'BUY',
                                    'timestamp': entry_date,
                                    'price': current_pos['entry_price'],
                                    'stock': stock,
                                    'timeframe': timeframe,
                                    'strategy': "Gann Swing" if timeframe == "Weekly" else "Trendline",
                                    'shares': current_pos['shares'],
                                    'profit': None,
                                    'return_pct': None,
                                    'win_rate': win_rate,
                                    'status': 'OPEN',
                                    'message': f"Open Position Entry at ${current_pos['entry_price']:.2f}"
                                })
                        except Exception as e:
                            print(f"Error processing current position: {e}")  # Using print instead of st.write

            if not signals:
                st.warning("No signals found in Trading Goers results for the last 30 days.")
            else:
                signals_df = pd.DataFrame(signals)
                signals_df = signals_df.sort_values('timestamp', ascending=False)

                st.markdown("### Trading Goers Signals (Last 30 Days)")
                signal_cols = st.columns(2)
                col_idx = 0

                for _, signal in signals_df.iterrows():
                    with signal_cols[col_idx]:
                        if signal['status'] == 'OPEN':
                            color = "orange"
                            icon = "🟠"
                            profit_message = "<p style='margin: 0; color: orange;'>Open Position</p>"
                        elif signal['type'] == 'BUY':
                            color = "green"
                            icon = "🟢"
                            profit_message = ""
                        else:
                            color = "red"
                            icon = "🔴"
                            profit_color = "green" if signal.get('profit', 0) > 0 else "red"
                            profit_message = f"""
                            <p style='margin: 0; color: {profit_color};'>
                                Profit: ${signal.get('profit', 0):.2f} ({signal.get('return_pct', 0):.1f}%)
                            </p>
                            """ if signal.get('profit') is not None else ""

                        st.markdown(
                            f"""
                            <div style='border: 1px solid {color}; padding: 10px; margin: 5px; border-radius: 5px;'>
                                <p style='color: {color}; margin: 0;'>
                                    {icon} <strong>{signal['stock']}</strong> - {signal['type']} Signal
                                    ({signal['timeframe']} timeframe)
                                </p>
                                <p style='margin: 0;'>Date: {signal['timestamp'].strftime('%Y-%m-%d')}</p>
                                <p style='margin: 0;'>Price: ${signal['price']:.2f}</p>
                                <p style='margin: 0;'>Win Rate: {signal['win_rate']:.1f}%</p>
                                <p style='margin: 0;'><em>Strategy: {signal['strategy']}</em></p>
                                {profit_message}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    col_idx = (col_idx + 1) % 2
# Then create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Chart Analysis", "Backtest Analysis", "Backtest Logs", "System Tests"])

# Tab content
with tab1:
    col1, col2 = st.columns([1, 4])

    with col1:
        # Use unique keys with tab1 prefix
        selected_sector = st.selectbox(
            "Select Sector",
            list(ASX_100_STOCKS.keys()),
            key='tab1_sector',
            on_change=sync_stock_selection,
            args=('tab1',),
            index=list(ASX_100_STOCKS.keys()).index(st.session_state.selected_sector)
        )

        selected_stock = st.selectbox(
            "Select Stock",
            ASX_100_STOCKS[st.session_state.selected_sector],
            key='tab1_stock',
            on_change=sync_stock_only,
            args=('tab1',),
            index=ASX_100_STOCKS[st.session_state.selected_sector].index(st.session_state.selected_stock)
        )

        st.session_state.selected_period = st.selectbox(
            "Select Time Period",
            list(time_periods.keys()),
            key='period_selector'
        )

        show_volume = st.checkbox("Show Volume", value=True)
        show_swing_lines = st.checkbox("Show Swing Lines", value=True)

    main()

with tab2:
    bt_col1, bt_col2 = st.columns([1, 4])

    with bt_col1:
        selected_strategy = st.selectbox(
            "Select Strategy",
            [strategy.value for strategy in Strategy],
            key='strategy_selector'
        )

        # Use unique keys with tab2 prefix
        selected_sector = st.selectbox(
            "Select Sector",
            list(ASX_100_STOCKS.keys()),
            key='tab2_sector',
            on_change=sync_stock_selection,
            args=('tab2',),
            index=list(ASX_100_STOCKS.keys()).index(st.session_state.selected_sector)
        )

        selected_stock = st.selectbox(
            "Select Stock",
            ASX_100_STOCKS[st.session_state.selected_sector],
            key='tab2_stock',
            on_change=sync_stock_only,
            args=('tab2',),
            index=ASX_100_STOCKS[st.session_state.selected_sector].index(st.session_state.selected_stock)
        )

        st.session_state.selected_period = st.selectbox(
            "Select Time Period",
            list(time_periods.keys()),
            key='backtest_period_selector'
        )

        st.session_state.selected_timeframe = st.selectbox(
            "Select Timeframe",
            ["Daily", "Weekly", "Monthly"],
            index=["Daily", "Weekly", "Monthly"].index(st.session_state.selected_timeframe),
            key='backtest_timeframe_selector'
        )

        backtest_initial_capital = st.number_input(
            "Initial Capital ($)",
            min_value=1000,
            max_value=10000000,
            value=10000,
            step=1000,
            help="Starting capital for the backtest"
        )
        backtest_position_size_pct = st.slider(
            "Position Size (%)",
            min_value=10,
            max_value=100,
            value=50,
            step=10,
            help="Percentage of capital to use per trade"
        ) / 100

        if selected_strategy == Strategy.TRENDLINE.value:
            min_trend_bars = st.slider(
                "Minimum Trend Bars",
                min_value=12,
                max_value=50,
                value=12,
                help="Minimum number of bars required to identify a trend"
            )
        else:
            min_trend_bars = 12
    # In the main UI code, within tab2 (Backtest Analysis tab)
    # Within tab2 (bt_col2), replace the existing chart creation code with:
    with bt_col2:
        # Get the backtest data
        backtest_df = get_stock_data(
            st.session_state.selected_stock,
            period=time_periods[st.session_state.selected_period],
            timeframe=st.session_state.selected_timeframe
        )

        if backtest_df is not None and len(backtest_df) > 0:
            # Run backtest based on selected strategy
            if selected_strategy == Strategy.SWING.value:
                # Gann Swing strategy
                _, swing_points = calculate_gann_swing(backtest_df)
                backtest_results = backtest_gann_swing_strategy(
                    backtest_df,
                    swing_points,
                    initial_capital=backtest_initial_capital,
                    position_size_pct=backtest_position_size_pct
                )
            else:
                # Trendline strategy
                backtest_results = backtest_trendline_strategy(
                    backtest_df,
                    initial_capital=backtest_initial_capital,
                    position_size_pct=backtest_position_size_pct,
                    min_bars=min_trend_bars
                )

            # Create strategy-specific chart
            fig = create_strategy_specific_chart(
                backtest_df,
                selected_strategy,
                min_trend_bars if selected_strategy == Strategy.TRENDLINE.value else None
            )

            if fig is not None:
                # Add trade markers
                entry_dates = [trade['entry_date'] for trade in backtest_results.trades]
                entry_prices = [trade['entry_price'] for trade in backtest_results.trades]

                if backtest_results.current_position:
                    entry_dates.append(backtest_results.current_position['entry_date'])
                    entry_prices.append(backtest_results.current_position['entry_price'])

                if entry_dates:
                    fig.add_trace(
                        go.Scatter(
                            x=entry_dates,
                            y=entry_prices,
                            mode='markers',
                            marker=dict(
                                symbol='triangle-up',
                                size=15,
                                color='lime',
                                line=dict(width=2, color='white')
                            ),
                            name='Buy Entry'
                        )
                    )

                # Add exit points
                exit_dates = [trade['exit_date'] for trade in backtest_results.trades]
                exit_prices = [trade['exit_price'] for trade in backtest_results.trades]

                if exit_dates:
                    fig.add_trace(
                        go.Scatter(
                            x=exit_dates,
                            y=exit_prices,
                            mode='markers',
                            marker=dict(
                                symbol='triangle-down',
                                size=15,
                                color='red',
                                line=dict(width=2, color='white')
                            ),
                            name='Sell Exit'
                        )
                    )

                # Display the chart
                st.plotly_chart(
                    fig,
                    use_container_width=True,
                    config={
                        'scrollZoom': True,
                        'displaylogo': False,
                        'modeBarButtonsToAdd': [
                            'drawline',
                            'drawopenpath',
                            'eraseshape',
                            'pan',
                            'zoom',
                            'select2d',
                            'lasso2d',
                            'zoomIn2d',
                            'zoomOut2d',
                            'autoScale2d',
                            'resetScale2d'
                        ],
                        'modeBarButtonsToRemove': [],
                        'dragmode': 'zoom'
                    }
                )

                # Log the backtest results
                # Add right after the backtest is run and before displaying results
                success, message = log_backtest_result(
                    st.session_state.selected_stock,
                    st.session_state.selected_period,
                    st.session_state.selected_timeframe,
                    backtest_initial_capital,
                    backtest_position_size_pct,
                    backtest_results
                )

                if not success:
                    st.warning(f"Note: This backtest was not added to the summary. Reason: {message}")

                # Display backtest results
                display_backtest_results(backtest_results)
            else:
                st.warning("No data available for chart creation.")
        else:
            st.warning("No data available for the selected stock and date range.")
with tab3:
    render_backtest_logs_tab()

# Add this in the main UI code after your existing tab definitions:
with tab4:
    st.header("🧪 System Tests")

    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### Test Controls")
        if st.button("Run Live Price Tests", type="primary"):
            with st.spinner("Running system tests..."):
                # Store results in session state
                st.session_state.test_results = test_live_price_updates()
                st.rerun()

        if st.button("Clear Test Results"):
            if 'test_results' in st.session_state:
                del st.session_state.test_results
            st.rerun()

    with col2:
        st.markdown("### Test Results")
        if 'test_results' in st.session_state:
            display_test_results(st.session_state.test_results)
        else:
            st.info("Click 'Run Live Price Tests' to start testing")


def test_live_price_updates():
    """
    Comprehensive test function to verify live price updates and backtest synchronization.
    """
    try:
        # Initialize test results with a complete structure
        results = {
            'success': False,
            'price_updates': {
                'status': False,
                'details': [],
                'errors': []
            },
            'backtest_updates': {
                'status': False,
                'details': [],
                'errors': []
            },
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 1. Test Price Update Functionality
        try:
            # Verify that ASX_100_STOCKS is not empty
            if not ASX_100_STOCKS:
                results['price_updates']['errors'].append("No stocks defined in ASX_100_STOCKS")
                return results

            # Attempt to retrieve data for a sample stock
            sample_stock = list(ASX_100_STOCKS.values())[0][0]  # Get first stock from first sector

            try:
                sample_data = get_stock_data(sample_stock, period=1)
                if sample_data is None or len(sample_data) == 0:
                    results['price_updates']['errors'].append(f"Failed to retrieve data for {sample_stock}")
                else:
                    results['price_updates']['status'] = True
                    results['price_updates']['details'].append(f"Successfully retrieved data for {sample_stock}")
                    results['price_updates']['details'].append(f"Data points: {len(sample_data)}")
                    results['price_updates']['details'].append(
                        f"Date range: {sample_data.index[0]} to {sample_data.index[-1]}")
            except Exception as data_error:
                results['price_updates']['errors'].append(f"Data retrieval error: {str(data_error)}")

        except Exception as price_update_error:
            results['price_updates']['errors'].append(f"Price update test failed: {str(price_update_error)}")

        # 2. Test Backtest Update Functionality
        try:
            # Perform a sample backtest
            try:
                sample_stock = list(ASX_100_STOCKS.values())[0][0]
                sample_data = get_stock_data(sample_stock, period=365, timeframe="Monthly")

                if sample_data is not None and len(sample_data) > 0:
                    _, swing_points = calculate_gann_swing(sample_data)
                    backtest_results = backtest_gann_swing_strategy(
                        sample_data,
                        swing_points,
                        initial_capital=10000,
                        position_size_pct=1
                    )

                    # Log the backtest result
                    log_backtest_result(
                        sample_stock,
                        "1 Year",
                        "Monthly",
                        10000,
                        0.5,
                        backtest_results
                    )

                    # Verify logging
                    logs = get_backtest_logs()
                    if any(log['stock'] == sample_stock for log in logs):
                        results['backtest_updates']['status'] = True
                        results['backtest_updates']['details'].append(
                            f"Successfully logged backtest for {sample_stock}")
                        results['backtest_updates']['details'].append(f"Total trades: {len(backtest_results.trades)}")
                    else:
                        results['backtest_updates']['errors'].append("Failed to log backtest results")
                else:
                    results['backtest_updates']['errors'].append("Insufficient data for backtest")

            except Exception as backtest_error:
                results['backtest_updates']['errors'].append(f"Backtest error: {str(backtest_error)}")

        except Exception as backtest_update_error:
            results['backtest_updates']['errors'].append(f"Backtest update test failed: {str(backtest_update_error)}")

        # Determine overall success
        results['success'] = (
                results['price_updates']['status'] and
                results['backtest_updates']['status']
        )

        return results

    except Exception as general_error:
        return {
            'success': False,
            'error': str(general_error),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def display_test_results(results):
    """Display the test results in a formatted way using Streamlit."""
    st.header("🧪 Live Price Test Results")

    # Overall status
    status_color = "green" if results.get('success', False) else "red"
    st.markdown(
        f"**Overall Status:** :{status_color}[{'✅ PASSED' if results.get('success', False) else '❌ FAILED'}]"
    )
    st.markdown(f"**Test Time:** {results.get('timestamp', 'N/A')}")

    # Error handling
    if 'error' in results:
        st.error(f"Test Error: {results['error']}")
        return

    # Helper function to safely get nested dictionary values
    def safe_get(dictionary, *keys, default=None):
        for key in keys:
            try:
                dictionary = dictionary[key]
            except (KeyError, TypeError):
                return default
        return dictionary

    # Price Updates Section
    st.subheader("Price Update Tests")
    price_updates = results.get('price_updates', {})
    price_status = safe_get(price_updates, 'status', default=False)
    st.markdown(
        f"Status: :{status_color}[{'✅ PASSED' if price_status else '❌ FAILED'}]"
    )

    price_details = safe_get(price_updates, 'details', default=[])
    if price_details:
        st.markdown("**Details:**")
        for detail in price_details:
            st.markdown(f"- {detail}")

    price_errors = safe_get(price_updates, 'errors', default=[])
    if price_errors:
        st.markdown("**Errors:**")
        for error in price_errors:
            st.error(error)

    # Backtest Updates Section
    st.subheader("Backtest Update Tests")
    backtest_updates = results.get('backtest_updates', {})
    backtest_status = safe_get(backtest_updates, 'status', default=False)
    st.markdown(
        f"Status: :{status_color}[{'✅ PASSED' if backtest_status else '❌ FAILED'}]"
    )

    backtest_details = safe_get(backtest_updates, 'details', default=[])
    if backtest_details:
        st.markdown("**Details:**")
        for detail in backtest_details:
            st.markdown(f"- {detail}")

    backtest_errors = safe_get(backtest_updates, 'errors', default=[])
    if backtest_errors:
        st.markdown("**Errors:**")
        for error in backtest_errors:
            st.error(error)
