
.. _Appendix Footprint :

Appendix Footprint
##################


Steps:
******

To generate a binary footprint for your board use that sequence of actions:

assume your code SHA number is 7a3b253

#. checkout code base

$ git checkout 7a3b253

#. check west version

Verify that your version of west is v0.7.3 or higher

$ west --version

Build an application using the command:

#. build footprint application

$ west build -b <your_board_name> tests/benchmarks/footprints/


#. view the ROM results output run.

$ west build -t rom_report

The result will be a list of all compiled objects and their ROM usage in a tabular form with bytes per symbol and the percentage it uses.

#. view the RAM results output run.

$ west build -t ram_report

The result will be a list of all compiled objects and their RAM usage in a tabular form with bytes per symbol and the percentage it uses.
