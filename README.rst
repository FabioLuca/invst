.. warning::
    Use this project at your own risk. Authors are not responsible for losses
    due to the trading strategy, or issues due to account access.

Overview
--------

This project goal is multiple, and split into different elements:

#.  Fetch market data series (history)
#.  Analyze data for taking decisions (hold, buy, sell)
#.  Execute an order into a broker
#.  Fetch account status

Fetch market data series (history)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The first element is to provide an encapsulation for accessing trading values
history for a given ticker by using the AlphaVantage API. Although other
sources are possible, they were not completely implemented here. The output for
a chosen ticker (stock) is a Pandas dataframe containing the open-high-low-close
values, also known as OHLC. More data is also available in the dataframe, as the
volume and adjusted close values.

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
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The analysis of the data in order to decide on an action to be taken is not
straight forward, since there are plural methodologies available, on many
levels of commplexity.

The initial implementation is based on a simple MACD (Moving Average
Convergence Divergence) method. However the basic framework around is intended
to cover more general cases. The framework consists of:

#. **Pre-Process data**: Adequate or fix data sets before analysis
#. **Apply individual methods**: Any possible method of analysis can be applied
   independent from each other. The target is that each one produces its own
   action recommendation (buy, sell or hold).
#. **Arbitration**: Evaluate all the previous recommendations and produces a
   final recommendation.

As as additional steps towards analysis, each method will produce a graphical
report to evaluate and also debug the results.

Execute an order into a broker
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fetch account status
^^^^^^^^^^^^^^^^^^^^

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

To do's and future work
-----------------------

* Fetch the data from tickets besides AlphaVantage, as it only supports stocks.
  Adding other sources could support ETF's and crypto's for instance.
* Fetch data from API's which provide more up-to-data data, without bigger
  delays such as 1-day delay, since it can impact the algorithm decision.
* Complete the trading implementation, as the order placement is missing.
  Currently only the fetching of account and depot information is implemented.

Virtual Environment
-------------------

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
---------------------------

The documentation can be generated by using Sphinx. In order to do so, first
acrivate the virtual environement, and then from the project `docs` folder use
the command below. This is valid for Linux or Windows when using its terminal::

    make html

In case of Windows with Powershell, the proper command is::

    .\make.bat html

The resulting documentation (`index.html`) is available in the folder
`docs/build/html`.

Unit testing
------------

Unit test cases are available in the `tests` folder. The tests are based in the
`pytest` package. To run all the tests, after activating the virtual
environement, use the command::

    pytest tests/

In case to run individual test files, for example `test_access.py`, then use
the command::

    pytest tests/test_access.py
