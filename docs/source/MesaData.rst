.. PyMesaReader documentation master file, created by
   sphinx-quickstart on Fri Jun  9 12:08:38 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

MesaData
=================================================
`MesaData` is a class that encodes the data in a single history or profile
file. It is instantiated by providing a path to the file to be accessed or 
indirectly via `MesaLogDir`. Whenever possible, columns from the header or
body of these files are directly accessible as attributes and always via the
`data` or `header` methods.

.. toctree::
   :maxdepth: 3

.. autoclass:: mesa_reader.MesaData
   :members:




.. Indices and tables
.. ==================
..
.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
