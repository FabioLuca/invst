.. warning::
    Use this project at your own risk. Authors are not responsible for losses
    due to the trading strategy, or issues due to account access.

Overview
================================================================================

.. contents::
    :depth: 3
    :backlinks: none
    :local:

Project goals
--------------------------------------------------------------------------------

This project goal is multiple, and split into different elements or steps:

#.  Fetch market data series (history)
#.  Analyze data for taking decisions (hold, buy, sell)
#.  Automatic execute an order into a broker
#.  Fetch account status

Fetch market data series (history)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first element is to provide an encapsulation for accessing trading values
history for a given ticker by using the AlphaVantage API. Although other
sources are possible, they were not completely implemented yet. The output for
a chosen ticker (stock) is a Pandas dataframe containing the open-high-low-close
values, also known as OHLC. More data is also available in the dataframe, as the
volume and adjusted close values, for example.

To work with the project an API key to AlphaVantage is necessary. Please follow
the instructions on their website to acquire one. One available, a file named
`api-cfg-access.json` need to be placed directly in the `cfg` folder. The
structure of the Json data follows the template below, where `<YOUR API KEY>`
needs to be replaced by the string provided as API key::

    {
        "api": {
            "fetching": {
                "AlphaVantage": {
                    "user_data": {
                        "APIKEY": "<YOUR API KEY>"
                    }
                }
            }
        }
    }


For this goal, the core implementation is done in the `data_access.py` file.

Analyze data for taking decisions (hold, buy, sell)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The analysis of the data in order to decide on an action to be taken is not
straight forward, since there are plural methodologies available, on many
levels of commplexity and success rate. See the section "Strategy Principles"
for more information.

The goal is not to expect very high success rate in the gains, but at least
have consistent improvements from a buy-hold strategy.

The very initial implementation is based on a simple MACD (Moving Average
Convergence Divergence) method. However the basic framework around is intended
to cover more general cases. The framework consists of:

#. **Pre-Process data**: Adequate or fix data sets before analysis.
#. **Apply individual methods**: Any possible method of analysis can be applied
   independent from each other. The target is that each one produces its own
   action recommendation (buy, sell or hold). Example of methods used on the
   analysis:

   * MACD (Moving Average Convergence Divergence)
   * RSI (Relative Strength Index)
   * Bollinger Bands

#. **Arbitration**: Evaluate all the previous recommendations and produces a
   final recommendation.

The basic design of this work is to always aggregate the new data into the
original Pandas dataframe, so results from analysis or any operations, are
always directly available, shall more complex operations be necessary.

In the framework, a metric (or many) is necessary to verify the success
obtained. As as additional steps towards analysis, each method will produce
a graphical report to evaluate and also debug the results.

Execute an order into a broker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is not implemented yet. As Comdirect API demands 2-factor
authentication, the possibility of algo-trading loses potential, so this steps
has lower priority.

Fetch account status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As a mean to provide capacity to manage the operation, the Comdirect account
status is tracked by fetching all the current balances and depots informations
(values, prices), which are provided as Pandas dataframes and can be stored as
Micrsoft Excel files, for example, as provided in `example.py`, or stored in
databases for further analysis (e.g. display evolution in chart).

In terms of implementation, all the Comdirect API related access and handling
is done by the `session.py`.

For access, similar to other cases above, the information must be provided in
the `api-cfg-access.json` (to be placed in the `cfg` folder). The structure
to be followed::

    {
        "api": {
            "trading": {
                "Comdirect": {
                    "user_data": {
                        "client_id": "<YOUR CLIENT ID>",
                        "client_secret": "<YOUR CLIENT SECRET>",
                        "account_number": "<YOUR ACCOUNT NUMBER>",
                        "pin": "<YOUR ACCOUNT PIN>"
                    }
                }
            }
        }
    }

The client ID and secret can be obtanined from the Comdirect website. Please
follow the instructions from their API documentation on how to obtain them.

Strategy principles
--------------------------------------------------------------------------------

To cover the principles, the starting point will be the OHLC (Open High Low
Close) data table for Amazon (AMZN) between 10.12.2021 and 09.11.2021:

.. csv-table:: Example of data from Amazon
   :file: /docs/source/example_amazon.csv
   :widths: 60, 60, 60, 60, 60, 60
   :header-rows: 1
   :delim: ;

The strategies for investiment covered here are basically of 2 types:

#. Momentum analysis
#. Prediction based on neural networks

The two have different ways of working. The former is based on an "inertia" of
the market, relling mostly that the market tries to correct itself whenever
oversold or overbought. Like a physical system, the mostly a position is off
balance, the stronger the correction is expected.

The second method is based on RNN (recurrent neural netoworks). Based on
the history of price for a stock, which is supplied to a RNN for learning, new
data (future) is predicted.

A major difference is on the way data is handled by both of the methods. While
the first uses the history and suggests an outcome which tend to be valid for a
few days or weeks, due to the system inertia, the second will produce much more
shorter term predictions if applied to the actual price (e.g. closing price),
since it tries to replicate the feature performance. Of course the same method
can be equally applied to other values or indicators, such a moving average
(where the fast changing component is filtered out) or to a MACD histogram.

As an illustration of the different structure of the outcomes, the table below
shows a general outcome based on the data above for Amazon, for an analysis
ran on the 10.12.2021:

.. csv-table:: Example of results
   :file: /docs/source/example_result_amazon.csv
   :widths: 60, 60, 60, 60
   :header-rows: 1
   :delim: ;

Especially for the Neural-Network example above, the length of the data is
chosen just to illustrate its presence, and not the actual length. As observed
above, the last input data used to make the prediction has a length of 4.

Combining both methods is the ultimate goal, since there is a potential to
optmize the strategy combining the benefits of each other.


To do's and future work
--------------------------------------------------------------------------------

* Fetch the data from tickets besides AlphaVantage, as it only supports stocks.
  Adding other sources could support ETF's and crypto's for instance.
* Fetch data from API's which provide more up-to-data data, without bigger
  delays such as 1-day delay, since it can impact the algorithm decision.
* Improve the trading strategies.
* Complete the trading implementation, as the order placement is missing.
  Currently only the fetching of account and depot information is implemented.

Virtual Environment
--------------------------------------------------------------------------------

It is recommended to run the project with a Virtual Environment. To do so,
first make sure to have the package available in you computer::

    pip install virtualenv

This step should be common between Linux and Windows systems.

Once available (succesful install), a virtual environement can be created by
the following steps:

#.  Go to project root folder
#.  Run the command below, where `<name_of_virtualenv>` is to be replacd by the
    name desired, for example: `venv`. Note that the command for python might
    change depending on the installation::
     
        python3 -m venv <name_of_virtualenv>

    The commmand above should be similar between Linux and Windows systems.

After creation, the virtual environmnet can be started by the following
command. Keep in mind that the `<name_of_virtualenv>` is to be replaced by the
name definied on the previous step. for Linux::

    source <name_of_virtualenv>/bin/activate

For Windows systems::

    <name_of_virtualenv>/Scripts/activate

Once started, in the terminal it will be indicated that a virtual environment
is running by a tag `(<name_of_virtualenv>)`.

After started the virtual environement, the necessary packages for this project
can be installed by the command::

    pip install -r src/Requirements.txt

Later, the environmenet can be deactivate when necessary by the command::

    deactivate

Accessing the documentation
--------------------------------------------------------------------------------

The documentation can be generated by using Sphinx. In order to do so, first
acrivate the virtual environement, and then from the project `docs` folder use
the command below. This is valid for Linux or Windows when using its terminal::

    make html

In case of Windows with Powershell, the proper command is::

    .\make.bat html

The resulting documentation (`index.html`) is available in the folder
`docs/build/html`.

Unit testing
--------------------------------------------------------------------------------

Unit test cases are available in the `tests` folder. The tests are based in the
`pytest` package. To run all the tests, after activating the virtual
environement, use the command::

    pytest tests/

In case to run individual test files, for example `test_access.py`, then use
the command::

    pytest tests/test_access.py