.. PyMesaReader documentation master file, created by
   sphinx-quickstart on Tue Jun  7 13:39:11 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MesaLogDir
========================================

.. toctree::
   :maxdepth: 2

The ``MesaLogDir`` class is an broader class that roughly represents an entire MESA run by providing access to all of its profiles and its history. If a ``MesaData`` instance represents a single history or profile file and a ``MesaProfileIndex`` instance represents a single profile index file, a ``MesaLogDir`` instance represents an entire logs directory.

The most common use cases for ``MesaLogDir`` instances is for unified access to history and profiles for the same run, as well as for situations where one might want to relate the history and profiles (for example, selecting profiles that fit some criterion in the star's history).

.. autoclass:: mesa_reader.MesaLogDir
  :members:

.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`

