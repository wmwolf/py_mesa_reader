.. PyMesaReader documentation master file, created by
   sphinx-quickstart on Tue Jun  7 13:39:11 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MesaData
========================================

.. toctree::
   :maxdepth: 2

The ``MesaData`` class is the workhorse of interacting with MESA output. A MesaData object gives easy access to the data stored in a history (``history.data``) or profile (``profileXX.data``) file.

The most common use case for these is to get at a particular column of data, like all of the values of the effective temperature of a star (in the case of a history file) or the density at each point in a particular model (in the case of a profile file).

.. autoclass:: mesa_reader.MesaData
  :members:

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

