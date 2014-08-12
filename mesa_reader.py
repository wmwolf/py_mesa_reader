import os

import numpy as np


class KeyError(Exception):
    
    def __init__(self, msg):
        Exception.__init__(self, msg)


class ProfileError(Exception):
    
    def __init__(self, msg):
        Exception.__init__(self, msg)


class HistoryError(Exception):
    
    def __init__(self, msg):
        Exception.__init__(self, msg)


class ModelNumberError(Exception):
    
    def __init__(self, msg):
        Exception.__init__(self, msg)


class BadPathError(Exception):
    
    def __init__(self, msg):
        Exception.__init__(self, msg)


class MesaData:
    
    '''Structure containing data from a Mesa output file.
    
    Reads a profile or history output file from mesa. Assumes a file with
    the following structure:
    
    line 1: header names
    
    line 2: header data
    
    line 3: blank
    
    line 4: main data names
    
    line 5: main data values
    
    This structure can be altered by using the class methods
    MesaData.set_header_rows and MesaData.set_data_rows.
    
    Parameters
    ----------
    file_name : string, optional
                File name to be read in. Default is 'LOGS/history.data',
                which works for scripts in a standard work directory with a
                standard logs directory for accessing the history data.

    
    Attributes
    ----------
    file_name    : string
                   Path to file from which the data is read.
    bulk_data    : numpy recarray
                   The main data (line 6 and below) in record array format.
                   Primarily accessed via the `data` method.
    bulk_names   : list
                   List of all available data column names that are valid
                   inputs for `data`. Essentially the column names in line
                   4 of `file_name`.
    header_data  : dict
                   Header data (line 2 of `file_name`) in dict format
    header_names : list
                   List of all available header dolumn names that are valid
                   inputs for `header`. Essentially the column names in line
                   1 of `file_name`.
    '''
    
    
    header_names_line = 2
    bulk_names_line = 6
    
    @classmethod
    def set_header_name_line(class_, name_line=2):
        class_.header_names_line = name_line
        
    @classmethod
    def set_data_rows(class_, name_line=6):
        class_.bulk_names_line = name_line
    
    def __init__(self, file_name='./LOGS/history.data'):
        '''Make a MesaData object from a Mesa output file.
        
        Reads a profile or history output file from mesa. Assumes a file with
        the following structure:
        
        line 1: header names
        
        line 2: header data
        
        line 3: blank
        
        line 4: main data names
        
        line 5: main data values
        
        This structure can be altered by using the class methods
        MesaData.set_header_rows and MesaData.set_data_rows.
        
        Parameters
        ----------
        file_name : string, optional
                    File name to be read in. Default is 'LOGS/history.data'
                    which works for
        '''
        self.file_name = file_name
        self.read_data()
    
    def read_data(self):
        '''Update data by re-reading from the original file name.
        
        This re-reads the data from the originally-provided file name. Mostly
        useful if the data file has been changed since it was first read in or
        if the class methods MesaData.set_header_rows or MesaData.set_data_rows
        have been used to alter how the data have been read in.
        
        Parameters
        ----------
        None
        '''
        self.bulk_data = np.genfromtxt(self.file_name,
            skip_header=MesaData.bulk_names_line - 1, names=True, dtype=None)
        self.bulk_names = self.bulk_data.dtype.names
        with open(self.file_name) as f:
            for i, line in enumerate(f):
                if i == MesaData.header_names_line - 1:
                    self.header_names = line.split()
                elif i == MesaData.header_names_line:
                    header_data = [eval(datum) for datum in line.split()]
                elif i > MesaData.header_names_line:
                    break
        self.header_data = dict(zip(self.header_names, header_data))
        self.remove_backups()
    
    def data(self, key):
        '''Accesses the data and returns a numpy array with the appropriate data
        
        Accepts a string key, like star_age (for history files) or logRho (for
        profile files) and returns the corresponding numpy array of data for
        that data type. Can also just use the shorthand methods that have the
        same name of the key.
        
        Parameters
        ----------
        key : string
              Name of data. Must match a main data title in the source file.
        
        Returns
        -------
        numpy.array
            Array of values for data corresponding to key at various time steps
            (history) or grid points (profile).
        
        Raises
        ------
        KeyError
            If `key` is an invalid key (i.e. not in `self.bulk_names`)
        
        Examples
        --------
        You can either call `data` explicitly with `key` as an argument, or get
        the same result by calling it implicitly by treating `key` as an
        attribute.
        
        >>> m = MesaData()
        >>> x = m.data('star_age')
        >>> y = m.star_age
        >>> x == y
        True
        
        In this case, x and y are the same because the non-existent method
        MesaData.star_age will direct to to the corresponding MesaData.data
        call.
        
        '''
        if not self.in_data(key):
            raise KeyError("'" + str(key) + "' is not a valid data type.")
        return self.bulk_data[key]
    
    def header(self, key):
        '''Accesses the header, returning a scalar the appropriate data
        
        Accepts a string key, like version_number and returns the corresponding
        datum for that key. Can also just use the shorthand
        methods that have the same name of the key.
        
        Parameters
        ----------
        key : string
              Name of data. Must match a main data title in the source file.
        
        Returns
        -------
        int/string/float
            Returns whatever value is below the corresponding key in the header
            lines of the source file.
        
        Raises
        ------
        KeyError
            If `key` is an invalid key (i.e. not in `self.header_names`)
        
        Examples
        --------
        Can call `header` explicitly with `key` as argument or implicitly,
        treating `key` as an attribute.
        
        In this case, x and y are the same because the non-existent method
        MesaData.version_number will first see if it can call
        MesaData.data('version_number'). Then, realizing that this doesn't make
        sense, it will instead call MesaData.header('version_number')
        
        >>> m = MesaData()
        >>> x = m.data('version_number')
        >>> y = m.version_number
        >>> x == y
        True
        '''
        
        if not self.in_header(key):
            raise KeyError("'" + str(key) + "' is not a valid header name.")
        return self.header_data[key]
    
    def is_history(self):
        '''Determine if the source file is a history file
        
        Checks if 'model_number' is a valid key for self.data. If it is, return
        True. Otherwise return False. This is used in determining whether or not
        to cleanse the file of backups and restarts in the MesaData.read_data.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        bool
            True if file is a history file, otherwise False
        '''
        return ('model_number' in self.bulk_names)
    
    def in_header(self, key):
        '''Determine if `key` is an available header data category.
        
        Checks if string `key` is a valid argument of MesaData.header. Returns
        True if it is, otherwise False
        
        Parameters
        ----------
        key : string
              Candidate string for accessing header data. This is what you want
              to be able to use as an argument of MesaData.header.
        
        Returns
        -------
        bool
            True if `key` is a valid input to MesaData.header, otherwise False.
        
        Notes
        -----
        This is automatically called by MesaData.header, so the average user
        shouldn't need to call it.
        '''
        return key in self.header_names
    
    def in_data(self, key):
        '''Determine if `key` is an available main data category.
        
        Checks if string `key` is a valid argument of MesaData.data. Returns
        True if it is, otherwise False
        
        Parameters
        ----------
        key : string
              Candidate string for accessing main data. This is what you want
              to be able to use as an argument of MesaData.data.
        
        Returns
        -------
        bool
            True if `key` is a valid input to MesaData.data, otherwise False.
        
        Notes
        -----
        This is automatically called by MesaData.data, so the average user
        shouldn't need to call it.
        '''
        return key in self.bulk_names
    
    def data_at_model_number(self, key, m_num):
        '''Return main data at a specific model number (for history files).
        
        Finds the index i where MesaData.data('model_number')[i] == m_num. Then
        returns MesaData.data(key)[i]. Essentially lets you use model numbers
        to index data.
        
        Parameters
        ----------
        key : string
              Name of data. Must match a main data title in the source file.
        
        m_num : int
                Model number where you want to sample the data
        
        Returns
        -------
        float/int
            Value of MesaData.data(`key`) at the same index where
            MesaData.data('model_number') == `m_num`
        
        See Also
        --------
        index_of_model_number : returns the index for sampling, not the value
        '''
        return self.data(key)[self.index_of_model_number(m_num)]
    
    def index_of_model_number(self, m_num):
        '''Return index where MesaData.data('model_number') is `m_num`.
        
        Returns the index i where MesaData.data('model_number')[i] == m_num.
        
        Parameters
        ----------
        m_num : int
                Model number where you want to sample data
        
        Returns
        -------
        int
            The index where MesaData.data('model_number') == `m_num`
        
        Raises
        ------
        HistoryError
            If trying to access a non-history file
        
        ModelNumberError
            If zero or more than one model numbers matching `m_num` are found.
        
        See Also
        --------
        data_at_model_number : returns the datum of a specific key a model no.
        '''
        if not self.is_history():
            raise HistoryError("Can't get data at model number " +
                               "because this isn't a history file")
        index = np.where(self.data('model_number') == m_num)[0]
        if len(index) > 1:
            raise ModelNumberError("Found more than one entry where model " +
                                   "number is " + str(m_num) + " in " +
                                   self.file_name + ". Report this.")
        elif len(index) == 0:
            raise ModelNumberError("Couldn't find any entries with model " +
                                   "number " + str(m_num) + ".")
        elif len(index) == 1:
            return index[0]
    
    def remove_backups(self, dbg=False):
        '''Cleases a history file of backups and restarts
        
        If the file is a history file, goes through and ensure that the
        model_number data are monotonically increasing. It removes rows of data
        from all categories if there are earlier ones later in the file.
        
        Parameters
        ----------
        dbg : bool, optional
              If True, will output how many lines are cleansed. Default is False
        
        Returns
        -------
        None
        '''
        if not self.is_history():
            return None
        if dbg:
            print("Scrubbing history...")
        to_remove = []
        for i in range(len(self.data('model_number')) - 1):
            smallest_future = np.min(self.data('model_number')[i + 1:])
            if self.data('model_number')[i] >= smallest_future:
                to_remove.append(i)
        if len(to_remove) == 0:
            if dbg:
                print("Already clean!")
            return None
        if dbg:
            print("Removing {} lines.".format(len(to_remove)))
        self.bulk_data = np.delete(self.bulk_data, to_remove)
    
    def __getattr__(self, method_name):
        if self.in_data(method_name):
            return self.data(method_name)
        elif self.in_header(method_name):
            return self.header(method_name)
        else:
            raise AttributeError(method_name)
    
    def _file_len(fname):
        with open(fname) as f:
            for i, l in enumerate(f):
                pass
        return i + 1


class MesaProfileIndex:
    
    '''Structure containing data from the profile index from MESA output.
    
    Reads in data from profile index file from MESA, allowing a mapping from
    profile number to model number and vice versa. Mostly accessed via the
    MesaLogDir class.
    
    Parameters
    ----------
    file_name : string, optional
                Path to the profile index file to be read in. Default is
                'LOGS/profiles.index', which should work when the working
                directory is a standard work directory and the logs directory is
                of the default name.
    
    Attributes
    ----------
    file_name             : string
                            path to the profile index file
    index_data            : dict
                            dictionary containing all index data in numpy
                            arrays.
    model_number_string   : string
                            header name of the model number column in
                            `file_name`
    profile_number_string : string
                            header name of the profile number column in
                            `file_name`
    profile_numbers       : numpy_array
                            List of all available profile numbers in order of
                            their corresponding model numbers (i.e. time-order).
    model_numbers         : numpy_array
                            Sorted list of all available model numbers.
    '''
    
    index_start_line = 2
    index_end = None
    index_names = ['model_numbers', 'priorities', 'profile_numbers']
    
    @classmethod
    def set_index_rows(class_, index_start=2, index_end=None):
        class_.index_start_line = index_start
        class_.index_end_line = index_end
        return index_start, index_end
    
    @classmethod
    def set_index_names(class_, name_arr):
        class_.index_names = name_arr
        return name_arr
        
    def __init__(self, file_name='./LOGS/profiles.index'):
        self.file_name = file_name
        self.read_index()
    
    def read_index(self):
        '''Read (or re-read) data from `self.file_name`.
        
        Read the file into an numpy array, sorting the table in order of
        increasing model numbers and establishes the `profile_numbers` and
        `model_numbers` attributes. Converts data and names into a dictionary.
        Called automatically at instantiation, but may be called again to
        refresh data.
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None'''
        self.index_data = np.genfromtxt(self.file_name,
            skip_header=MesaProfileIndex.index_start_line - 1, dtype=None)
        self.model_number_string = MesaProfileIndex.index_names[0]
        self.profile_number_string = MesaProfileIndex.index_names[-1]
        self.index_data = self.index_data[np.argsort(self.index_data[:,0])]
        self.index_data = dict(zip(MesaProfileIndex.index_names, self.index_data.T))
        self.profile_numbers = self.data(self.profile_number_string)
        self.model_numbers = self.data(self.model_number_string)
    
    def data(self, key):
        '''Access index data and return array of column corresponding to `key`.
        
        Parameters
        ----------
        key : string
              Name of column to be returned. Likely choices are 'model_numbers',
              'profile_numbers', or 'priorities'.
        
        Returns
        -------
        numpy_array
            Array containing the data requested.
        
        Raises
        ------
        KeyError
            If input key is not a valid column header name.
        '''
        
        if key not in self.index_names:
            raise KeyError("'" + str(key) + "' is not a column in " +
                           self.file_name)
        return np.array(self.index_data[key])
    
    def have_profile_with_model_number(self, model_number):
        '''Determines if given `model_number` has a matching profile number.
        
        Attributes
        ----------
        model_number : int
                       model number to be checked for available profile number
        
        Returns
        -------
        bool
            True if `model_number` has a corresponding profile number. False
            otherwise.'''
        return (model_number in self.data(self.model_number_string))
    
    def have_profile_with_profile_number(self, profile_number):
        '''Determines if given `profile_number` is a valid profile number.
        
        Attributes
        ----------
        profile_number : int
                         profile number to be verified
        
        Returns
        -------
        bool
            True if `profile_number` has a corresponding entry in the index.
            False otherwise.'''
        return (profile_number in self.data(self.profile_number_string))
    
    def profile_with_model_number(self, model_number):
        '''Converts a model number to a profile number if possible.
        
        If `model_number` has a corresponding profile number in the index,
        returns it. Otherwise throws an error.
        
        Attributes
        ----------
        model_number : int
                       model number to be converted into a profile number
        
        Returns
        -------
        int
            profile number corresponding to `model_number`
        
        Raises
        ------
        ProfileError
            If no profile number can be found that corresponds to `model_number`
        '''
        if not (self.have_profile_with_model_number(model_number)):
            raise ProfileError("No profile with model number " +
                               str(model_number) + ".")
        indices = np.where(self.data(self.model_number_string) == model_number)
        return np.take(self.data(self.profile_number_string), indices[0])[0]
    
    def __getattr__(self, method_name):
        if method_name in self.index_data.keys():
            return self.data(method_name)
        else:
            raise AttributeError(method_name)


class MesaLogDir:
    
    '''Structure providing access to both history and profile output from MESA
    
    Provides access for accessing the history and profile data of a MESA run
    by linking profiles to the history through model numbers.
    
    Parameters
    ----------
    log_path         : string, optional
                       Path to the logs directory, default is 'LOGS'
    profile_prefix   : string, optional
                       Prefix before profile number in profile file names,
                       default is 'profile'
    profile_suffix   : string, optional
                       Suffix after profile number and period for profile file
                       names, default is 'data'
    history_file     : string, optional
                       Name of the history file in the logs directory, default
                       is 'history.data'
    index_file       : string, optional
                       Name of the profiles index file in the logs directory,
                       default is 'profiles.index'
    memoize_profiles : bool, optional
                       Determines whether or not profiles will be "memo-ized",
                       default is True. If memoized, once a profile is called
                       into existence, it is saved so that it need not be read
                       in again. Good for quick, clean, repeated access of a
                       profile, but bad for reading in many profiles for
                       one-time uses as it will hog memory.
    
    Attributes
    -----------
    log_path         : string
                       Path to the logs directory; used (re-)reading data in
    profile_prefix   : string
                       Prefix before profile number in profile file names
    profile_suffix   : string
                       Suffix after profile number and period for profile file
                       names
    history_file     : string
                       Base name (not path) of the history file in the logs
                       directory
    index_file       : string
                       Base name (not path) of the profiles index file in the
                       logs directory
    memoize_profiles : bool
                       Determines whether or not profiles will be "memo-ized".
                       Setting this after initialization will not delete
                       profiles from memory. It will simply start/stop memoizing
                       them. To clear out memoized profiles, re-read the data
                       with `self.read_logs()`
    history_path     : string
                       Path to the history data file
    index_path       : string
                       Path to the profile index file
    history          : MesaData
                       MesaData object containing history information from
                       `self.history_path`
    history_data     : MesaData
                       Alias for `self.history`
    profiles         : MesaProfileIndex
                       MesaProfileIndex from profiles in `self.index_path`
    profile_numbers  : numpy_array
                       Result of calling `self.profiles.profile_numbers`. Just
                       the profile numbers of the simulation in order of
                       corresponding model numbers.
    model_numbers    : numpy_array
                       Result of calling `self.profiles.model_numbers`. Just
                       the model numbers of the simulations that have
                       corresponding profiles in ascending order.
    
    profile_dict     : dictionary
                       Stores MesaData objects from profiles. Keys to this
                       dictionary are profile numbers, so presumably
                       `self.profile_dict(5)` would yield the MesaData object
                       obtained from the file `profile5.data` (assuming
                       reasonable defaults) if such a profile was ever accessed.
                       Will remain empty if memoization is shut off.
    '''
    
    def __init__(self, log_path='LOGS', profile_prefix='profile',
                 profile_suffix='data', history_file='history.data',
                 index_file='profiles.index', memoize_profiles=True):
        self.log_path = log_path
        self.profile_prefix = profile_prefix
        self.profile_suffix = profile_suffix
        self.history_file = history_file
        self.index_file = index_file
        
        # Check if log_path and files are dir/files.
        if not os.path.isdir(self.log_path):
            raise BadPathError(self.log_path + ' is not a valid directory.')
        
        self.history_path = os.path.join(self.log_path, self.history_file)
        if not os.path.isfile(self.history_path):
            raise BadPathError(self.history_file + ' not found in ' +
                               self.log_path + '.')
        
        self.index_path = os.path.join(self.log_path, self.index_file)
        if not os.path.isfile(self.index_path):
            raise BadPathError(self.index_file + ' not found in ' +
                               self.log_path + '.')
        
        self.memoize_profiles = memoize_profiles
        self.read_logs()
    
    def read_logs(self):
        '''Read (or re-read) data from the history and profile index.
        
        Reads in `self.history_path` and `self.index_file` for use in getting
        history data and profile information. This is automatically called at
        instantiation, but can be recalled by the user if for some reason the
        data needs to be refreshed (for instance, after changing some of the
        reader methods to read in specially-formatted output.)
        
        Parameters
        ----------
        None
        
        Returns
        -------
        None
        
        Note
        ----
        This, if called after initialization, will empty `self.profile_dict`,
        erasing all memo-ized profiles.
        '''
        
        self.history = MesaData(self.history_path)
        self.history_data = self.history
        self.profiles = MesaProfileIndex(self.index_path)
        self.profile_numbers = self.profiles.profile_numbers
        self.model_numbers = self.profiles.model_numbers
        self.profile_dict = dict()
    
    def have_profile_with_model_number(self, m_num):
        '''Checks to see if a model number has a corresponding profile number.
        
        Parameters
        ----------
        m_num : int
                model number to be checked
        
        Returns
        -------
        bool
            True if the model number is in `self.model_numbers`, otherwise
            False.
        
        '''
        return self.profiles.have_profile_with_model_number(m_num)
    
    def have_profile_with_profile_number(self, p_num):
        '''Checks to see if a given number is a valid profile number.
        
        Parameters
        ----------
        p_num : int
                profile number to be checked
        
        Returns
        -------
        bool
            True if profile number is in `self.profile_numbers`, otherwise
            False.'''
        return self.profiles.have_profile_with_profile_number(p_num)
    
    def profile_with_model_number(self, m_num):
        '''Converts a model number to a corresponding profile number
        
        Parameters
        ----------
        m_num : int
                model number to be converted
        
        Returns
        -------
        int
            profile number that corresponds to `m_num`.
        '''
        return self.profiles.profile_with_model_number(m_num)
    
    def profile_data(self, model_number=-1, profile_number=-1):
        '''Generate or retrieve MesaData from a model or profile number.
        
        If both a model number and a profile number is given, the model number
        takes precedence. If neither are given, the default is to return a
        MesaData object of the last profile (biggest model number). In either
        case, this generates (if it doesn't already exist) or retrieves (if it
        has already been generated and memoized) a MesaData object from the
        corresponding profile data.
        
        Parameters
        ----------
        model_number   : int, optional
                         model number for the profile MesaData object desired.
                         Default is -1, corresponding to the last model number.
        profile_number : int, optional
                         profile number for the profile MesaData object desired.
                         Default is -1, corresponding to the last model number.
                         If both `model_number` and `profile_number` are given,
                         `profile_number` is ignored.
        
        Returns
        -------
        MesaData
                 Data for profile with desired model/profile number.
        '''
        to_use = -1
        if model_number == -1:
            if profile_number == -1:
                to_use = self.profile_numbers[-1]
            else:
                to_use = profile_number
        else:
            to_use = self.profile_with_model_number(model_number)
        
        if to_use in self.profile_dict:
            return self.profile_dict[to_use]
        
        file_name = os.path.join(self.log_path,
                                 (self.profile_prefix +
                                  str(to_use) + '.' + self.profile_suffix))
        p = MesaData(file_name)
        if self.memoize_profiles:
            self.profile_dict[to_use] = p
        return p
    
    def select_models(self, f, *keys):
        '''Yields model numbers for profiles that satisfy a given criteria.
        
        Given a function `f` of various time-domain (history) variables,
        `*keys` (i.e., categories in `self.history.bulk_names`), filters
        `self.model_numbers` and returns all model numbers that satisfy the
        criteria.
        
        Parameters
        ----------
        f    : function
               A function of the same number of parameters as strings given
               for `keys` that returns a boolean. Should evaluate to `True`
               when condition is met and `False` otherwise.
        keys : strings
               Name of data categories from `self.history.bulk_names` whose
               values are to be used in the arguments to `f`, in the same order
               that they appear as arguments in `f`.
        
        Returns
        -------
        numpy_array
                    Array of model numbers that have corresponding profiles
                    where the condition given by `f` is `True`.
        
        Raises
        ------
        KeyError
            If any of the `keys` are invalid history keys.
        
        Examples
        --------
        >>> l = MesaLogDir()
        >>> def is_old_and_bright(age, log_lum):
        >>>     return age > 1e9 and log_lum > 3
        >>> m_nums = l.select_models(is_old_and_bright, 'star_age', 'log_L' )
        
        Here, `m_nums` will contain all model numbers that have profiles where
        the age is greater than a billion years and the luminosity is greater
        than 1000 Lsun, provided that 'star_age' and 'log_L' are in
        `self.history.bulk_names`.'''
        
        for key in keys:
            if not self.history.in_data(key):
                raise KeyError("'" + str(key) + "' is not a valid data type.")
        inputs = {}
        for m_num in self.model_numbers:
            this_input = []
            for key in keys:
                this_input.append(
                    self.history.data_at_model_number(key, m_num))
            inputs[m_num] = this_input
        mask = np.array([f(*inputs[m_num]) for m_num in self.model_numbers])
        return self.model_numbers[mask]
