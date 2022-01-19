.. warning::
    Use this project at your own risk. Authors are not responsible for losses
    due to the trading strategy adopted, or issues due to account access.
    Comdirect will block an account if 2-factor authentication is not properly
    responded.

Overview
================================================================================

.. contents::
    :depth: 3
    :backlinks: none
    :local:

Project goals
--------------------------------------------------------------------------------

This project goal is to automate the operation of trading in the market, such as
stocks or ETF's (Exchange Traded Fund). In principle the same approach can be
adopted and extended to Cryptocurrencies, where the limitation is on the 
trading platformed used, if it permits such operations or not.

The goal is not to operate as high-frequency trading, but like a regular trader.
The aimed advantages for the project is then on the potential of analysing a
bigger amount of data (different stocks or products) in a shorter time; apply 
consistent mathematical and physical models, due to the major amount of data
and tools available.

This project is split into a few major elements or steps:

1. Fetch market data series (history)
2. Analyze data for taking decisions (hold, buy, sell)
3. Automatic execute an order into a broker
4. Fetch account status

In addition, there are 2 other steps which are part of the project, and
secondary in the complete project:

1. Request user aggreement per Whatsapp
2. Present a final report of performance to the user

The flowchart below illustrates the relation between the steps and also to the
core component behind them:

.. image:: _static/images/flowchart.png
    :width: 400
    :align: center
    :alt: Core flowchart

Fetch market data series (history)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first element is to provide an encapsulation for accessing trading values
history for a given ticker by using the `Alpha Vantage API
<https://www.alphavantage.co/>`_ or `Yahoo Finance API
<https://www.yahoofinanceapi.com/>`_ . Both API access are not complete
implemented, but only the necessary parts for this project. Additional
sources are also possible, and could be included in the future.

A note about the API's is regarding their continuity. Eventually the providers
might stop doing it, or might change their business model, moving fully or
partly to paid services, as happened for example to Alpha Vantage access to the
`Adjusted Close` value. In such cases, the user needs to migrate into a paid
service or pursue a different provider.

To mitigate the changes when a new provider is assigned or included, the output
from the abstraction layer (interface) is similar as much as possible. Mandatory
data of course will be equivalent, but some additional ones, such as `Dividends
payments`, could possibly not be available on certain providers.

The operation is commononized so all the requests are meant for a single symbol
per time. For the API implementation, the requests are always to the maximum
amount of data available, so all the historical data supported by the API is 
used.

The output from a chosen ticker (stock) is a Pandas dataframe containing the
open-high-low-close values, also known as OHLC. More data is also available in
the dataframe, as the volume and adjusted close values, for example. The name of
the columns in the dataframe are:

1. ``Date``
2. ``Open``
3. ``High``
4. ``Low``
5. ``Close``
6. ``Close Final``: Meaning the adjusted close value.
7. ``Volume``
8. ``Dividend Amount``: Possibly not available information, but also not
   necessary the project application.
9. ``Split Coefficient``: Possibly not available information, but also not
   necessary the project application.

The API's applied in the project will need authentication. For that, an account
must be created. Please follow the instructions from the chosen provider on
their respective website to acquire one. Once available, a file named
``api-cfg-access.json`` need to be placed directly in the ``cfg\user`` folder.
The structure of the JSON data follows the template below, where
`<YOUR API KEY>` needs to be replaced by the string provided as API key::

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

For Yahoo Finance::

    {
        "api": {
            "fetching": {
                "YahooFinance": {
                    "user_data": {
                        "APIKEY": "<YOUR API KEY>"
                    }
                }
            }
        }
    }

Both can be defined at the same time in the dictionary. Attention must be taken
that the value for the key `api / fetching / selection` in the ``api-cfg.json``
file (also in the ``cfg`` folder) determines which provider to use. So for
example, if Yahoo Finance is the desired one, the following entry is necessary::

    {
        "api": {
            "fetching": {
                "selection": "YahooFinance"
            }
        }
    }

For this data fetching goal, the core implementation is done in the
``data_access.py`` module.

Analyze data for taking decisions (hold, buy, sell)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The analysis of the data in order to decide on an action to be taken is not
straight forward, since there are plural methodologies available, on many
levels of commplexity and success rate. See the section "Strategy Principles"
for more information.

The goal is not to expect very high success rate in the gains, which would mean
that the algorithm is always correct in decision and timing, having a "perfect"
strategy. In this scenario, one would have all the ups from a ticker, and none
of the lows from it. Rather, the goal is to have a result between this "perfect"
strategy and a buy-hold one, where one purchases a stock and holds it for a
longer time spam.

After analysis from the individual methods, such as, MACD (Moving Average
Convergence Divergence), Bollinger Bands and RSI (Relative Strength
Index), the initial implementation is based on the MACD alone. However the
basic framework around is intended to cover more general cases. The framework
consists of:

1. **Pre-Process data**: Adequate or fix data sets before analysis.
2. **Apply individual methods**: Any possible method of analysis can be applied
   independent from each other. The target is that each one produces its own
   action recommendation (buy, sell or hold). Example of methods used on the
   analysis:

   * MACD (Moving Average Convergence Divergence)
   * RSI (Relative Strength Index)
   * Bollinger Bands

   At this point, predictions can be used. For example, the MACD analysis is
   supported by RNN (LSTM) prediction for the MACD histrogram signal.

3. **Arbitration**: Evaluate all the previous recommendations and produces a
   final recommendation.

The basic design of this work is to always aggregate the new data into the
original Pandas dataframe, so results from analysis or any operations, are
always directly available, shall more complex operations be necessary.

In the framework, a metric (or many) is necessary to verify the success
obtained. As as additional steps towards analysis, each method will produce
a graphical report to evaluate and also debug the results.

Execute an order into a broker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This step is not implemented yet.

Fetch account status
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As a mean to provide capacity to manage the operation, the Comdirect account
status is tracked by fetching all the current balances and depots informations
(values, prices), which are provided as Pandas dataframes and can be stored as
Micrsoft Excel files, for example, as provided in ``example.py``, or stored in
databases for further analysis (e.g. display evolution in chart).

In terms of implementation, all the `Comdirect API
<https://www.comdirect.de/cms/kontakt-zugaenge-api.html>`_ related access and
handling is done by the ``session.py``.

For access, similar to other cases above, the information must be provided in
the ``api-cfg-access.json`` (to be placed in the ``cfg`` folder). The structure
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

1. Momentum analysis
2. Prediction based on neural networks

The two have different ways of working. The former is based on an "inertia" of
the market, relying mostly that the market tries to correct itself whenever
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

As another demonstration of the data organization, see the figure below. The
image presents the way the data is handled: first the methods will add their
signals to the structure, second the predictions are done to extrapolate the
data into the future.

.. image:: _static/images/strategy_data.png
    :width: 600
    :align: center
    :alt: Data structure

To do's and future work
--------------------------------------------------------------------------------

* Fetch the data from tickers besides AlphaVantage, as it only supports stocks.
  Adding other sources could support ETF's and crypto's for instance.
* Fetch data from API's which provide more up-to-data data, without bigger
  delays such as 1-day delay, since it can impact the algorithm decision.
* Improve the trading strategies.
* Optmize parameters in the RNN, since it is still based on the vanilla version.
* Complete the trading implementation, as the order placement is missing.
  Currently only the fetching of account and depot information is implemented.

Setup and operations
--------------------------------------------------------------------------------

User configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

As mentioned above, some files are necessary for operation of the project. The
final structure of files must follow the below description::

    <Project folder>
    ├── ...Other files...
    ├── cfg
    │   ├── local
    │   │   └─ local.json
    │   ├── user
    │   │   └─ api-cfg-access.json
    │   ├─ api-cfg.json
    │   └─ parameters.json

Virtual Environment
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

It is recommended to run the project with a Virtual Environment. To do so,
first make sure to have the package available in you computer::

    pip install virtualenv

This step should be common between Linux and Windows systems.

Once available (succesful install), a virtual environement can be created by
the following steps:

1.  Go to project root folder
2.  Run the command below, where `<name_of_virtualenv>` is to be replacd by the
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

    pip install -r requirements.txt

Later, the environmenet can be deactivate when necessary by the command::

    deactivate

Accessing the documentation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The documentation can be generated by using Sphinx. In order to do so, first
acrivate the virtual environement, and then from the project `docs` folder use
the command below. This is valid for Linux or Windows when using its terminal::

    make html

In case of Windows with Powershell, the proper command is::

    .\make.bat html

The resulting documentation (`index.html`) is available in the folder
`docs/build/html`.

Docker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To support cloud operation, for example, Google Cloud, the project is
containerized in Docker for supporting deployment.

To build the Docker image, the following command can be used::

    docker build --tag invst-docker .

The to run the image::

    docker run invst-docker

To list the running containers::

    docker ps

From this list, the container name can be checked. To terminate the running
ones::

    docker stop [CONTAINER_NAME]

Unit testing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Unit test cases are available in the `tests` folder. The tests are based in the
`pytest` package. To run all the tests, after activating the virtual
environement, use the command::

    pytest tests/

In case to run individual test files, for example `test_access.py`, then use
the command::

    pytest tests/test_access.py