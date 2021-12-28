.. invst-access documentation master file, created by
   sphinx-quickstart on Thu Nov 18 22:29:00 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to INVST documentation!
================================================================================

Page contents
--------------------------------------------------------------------------------
.. toctree::
   :maxdepth: 1
   :name: mastertoc

   modules
   
.. General
.. =======

.. include:: ../../README.rst

Use examples
--------------------------------------------------------------------------------

example.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: example
   :members:
   :undoc-members:
   :show-inheritance:

Automation
--------------------------------------------------------------------------------

As a general note when running the automation scripts, to be able to
successfu execute them, due to importing and relative path management, the
following command is to be used from the project root folder::

   python -m automation.<Script name>

For the `<Script name>` the .py extension shall not be used.

comdirect_status_report.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: automation.comdirect_status_report
   :members:
   :undoc-members:
   :show-inheritance:
   :exclude-members:
      create_page,
      convert_hex_to_rgba,
      create_chart_account_aggregated_values,
      create_chart_depots_current_values,
      create_chart_depots_relative_values,
      create_combined_dataframes,
      create_filtered_depots_dataframe,
      create_historical_aggregated_dataframe,
      define_timespam,
      update_output,
      create_line_chart,

comdirect_status_update.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: automation.comdirect_status_update
   :members:
   :undoc-members:
   :show-inheritance:

run_analysis.py
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: automation.run_analysis
   :members:
   :undoc-members:
   :show-inheritance:

Indices and tables
--------------------------------------------------------------------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


