import numpy as np
from os import path
from astropy.io import ascii

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
    data_reader = ascii.get_reader(Reader=ascii.Basic)
    data_reader.header.splitter.delimiter = ' '
    data_reader.data.splitter.delimiter = ' '
    data_reader.header.start_line = 4
    data_reader.data.start_line = 5
    data_reader.data.end_line = None
    data_reader.header.comment = r'\s*#'
    data_reader.data.comment = r'\s*#'

    hdr_reader = ascii.get_reader(Reader=ascii.Basic)
    hdr_reader.header.splitter.delimiter = ' '
    hdr_reader.data.splitter.delimiter = ' '
    hdr_reader.header.start_line = 1
    hdr_reader.data.start_line = 2
    hdr_reader.data.end_line = 3
    hdr_reader.header.comment = r'\s*#'
    hdr_reader.data.comment = r'\s*#'

    @classmethod
    def set_header_rows(klass, name_start = 1, data_start = 2, data_end = 3):
        klass.hdr_reader.header.start_line = name_start
        klass.hdr_reader.data.start_line = data_start
        klass.hdr_reader.data.end_line = data_end

    @classmethod
    def set_data_rows(klass, name_start = 4, data_start = 5, data_end = None):
        klass.data_reader.header.start_line = name_start
        klass.data_reader.data.start_line = data_start
        klass.data_reader.data.end_line = data_end

    def __init__(self, file_name = './LOGS/history.data'):
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
        
        This re-reades the data from the originally-provided file name. Mostly
        useful if the data file has been changed since it was first read in or
        if the class methods MesaData.set_header_rows or MesaData.set_data_rows
        have been used to alter how the data have been read in.
        
        Parameters
        ----------
        None
        '''
        self.bulk_data = self.data_reader.read(self.file_name)
        self.bulk_names = self.bulk_data.colnames
        self.header_data = self.hdr_reader.read(self.file_name)
        self.header_names = self.header_data.colnames
        self.remove_backups()

    def data(self, key):
        '''Accesses the data and returns a numpy array with the appropriate data
        
        Accepts a string key, like star_age (for history files) or logRho (for
        profile files) and returns the corresponding numpy array of data for
        that data type. Can also just use the shorthand methods that have the 
        same name of the key. For instance
        
        m = MesaData()
        
        x = m.data('star_age')
        y = m.star_age
        
        x == y # => True
        
        In this case, x and y are the same because the non-existent method
        MesaData.star_age will direct to to the corresponding MesaData.data
        call.
        
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
        '''
        if not self.in_data(key):
            raise KeyError("'" + str(key) + "' is not a valid data type.")
        return np.array(self.bulk_data[key])

    def header(self, key):
        '''Accesses the header, returning a scalar the appropriate data
        
        Accepts a string key, like version_number and returns the corresponding
        datum for that key. Can also just use the shorthand
        methods that have the same name of the key. For instance
        
        m = MesaData()
        
        x = m.data('version_number')
        y = m.version_number
        
        x == y # => True
        
        In this case, x and y are the same because the non-existent method
        MesaData.version_number will first see if it can call
        MesaData.data('version_number'). Then, realizing that this doesn't make
        sense, it will instead call MesaData.header('version_number')
        
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
        '''
        
        if not self.in_header(key):
            raise KeyError("'" + str(key) + "' is not a valid header name.")
        return self.header_data[key][0]

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
        index_of_model_number : returns the index for smapling, not the value
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

    def remove_backups(self, dbg = False):
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
            print "Scrubbing history..."
        to_remove = []
        for i in range(len(self.data('model_number'))-1):
            smallest_future = np.min(self.data('model_number')[i+1:])
            if self.data('model_number')[i] >= smallest_future:
                to_remove.append(i)
        if len(to_remove) == 0:
            if dbg:
                print "Already clean!"
            return None
        if dbg:
            print "Removing {} lines.".format(len(to_remove))
        self.bulk_data.remove_rows(to_remove)

    def __getattr__(self, method_name):
        if self.in_data(method_name):
            return self.data(method_name)
        elif self.in_header(method_name):
            return self.header(method_name)
        else:
            raise AttributeError, method_name

class MesaProfileIndex:
    index_reader = ascii.get_reader(Reader=ascii.NoHeader)
    index_reader.data.splitter.delimiter = ' '
    index_reader.data.start_line = 1
    index_reader.data.end_line = None
    index_reader.data.comment = r'\s*#'
    index_names = ['model_numbers', 'priorities', 'profile_numbers']
    index_reader.names = index_names

    @classmethod
    def set_index_rows(klass, index_start = 1, index_end = None):
        klass.index_reader.data.start_line = index_start
        klass.index_reader.data.end_line = index_end
        return index_start, index_end

    @classmethod
    def set_index_names(klass, name_arr):
        klass.index_names = name_arr
        klass.index_reader.names = klass.index_names
        return name_arr

    def __init__(self, file_name = './LOGS/profiles.index'):
        self.file_name = file_name
        self.read_index()

    def read_index(self):
        self.index_data = MesaProfileIndex.index_reader.read(self.file_name)
        self.model_number_string = MesaProfileIndex.index_names[0]
        self.profile_number_string = MesaProfileIndex.index_names[-1]
        self.index_data.sort(self.model_number_string)
        self.profile_numbers = self.data(self.profile_number_string)
        self.model_numbers = self.data(self.model_number_string)

    def data(self, key):
        if not key in self.index_names:
            raise KeyError("'" + str(key) + "' is not a column in " +
                           self.file_name)
        return np.array(self.index_data[key])

    def have_profile_with_model_number(self, model_number):
        return (model_number in self.data(self.model_number_string))

    def have_profile_with_profile_number(self, profile_number):
        return (profile_number in self.data(self.profile_number_string))

    def profile_with_model_number(self, model_number):
        if not (self.have_profile_with_model_number(model_number)):
            raise ProfileError("No profile with model number " +
                               str(model_number) + ".")
        indices = np.where(self.data(self.model_number_string) == model_number)
        return np.take(self.data(self.profile_number_string), indices[0])[0]

    def __getattr__(self, method_name):
        if method_name in self.index_data.colnames:
            return self.data(method_name)
        else:
            raise AttributeError, method_name

class MesaLogDir:

    def __init__(self, log_path = 'LOGS', profile_prefix = 'profile',
                 profile_suffix = 'data', history_file = 'history.data',
                 index_file = 'profiles.index'):
        self.log_path = log_path
        self.profile_prefix = profile_prefix
        self.profile_suffix = profile_suffix
        self.history_file = history_file
        self.index_file = index_file

        # Check if log_path and files are dir/files.
        if not path.isdir(self.log_path):
            raise BadPathError(self.log_path + ' is not a valid directory.')
        if not path.isfile(self.log_path + '/' + self.history_file):
            raise BadPathError(self.history_file + ' not found in ' +
                               self.log_path + '.')
        if not path.isfile(self.log_path + '/' + self.index_file):
            raise BadPathError(self.index_file + ' not found in ' +
                               self.log_path + '.')

        self.history_path = self.log_path + '/' + self.history_file
        self.index_path = self.log_path + '/' + self.index_file
        self.read_logs()

    def read_logs(self):
        self.history = MesaData(self.history_path)
        self.history_data = self.history
        self.profiles = MesaProfileIndex(self.index_path)
        self.profile_numbers = self.profiles.profile_numbers
        self.model_numbers = self.profiles.model_numbers
        self.profile_dict = dict()

    def have_profile_with_model_number(self, m_num):
        return self.profiles.have_profile_with_model_number(m_num)

    def have_profile_with_profile_number(self, m_num):
        return self.profiles.have_profile_with_profile_number(m_num)

    def profile_with_model_number(self, model_number):
        return self.profiles.profile_with_model_number(model_number)

    def profile_data(self, model_number = -1, profile_number = -1):
        to_use = -1
        if model_number == -1:
            if profile_number == -1:
                to_use = self.profile_numbers[-1]
            else:
                to_use = profile_number
        else:
            to_use = self.profile_with_model_number(model_number)
        if not to_use in self.profile_dict:
            file_name = (self.log_path + '/' + self.profile_prefix
                         + str(to_use) + '.' + self.profile_suffix)
            self.profile_dict[to_use] = MesaData(file_name)

        return self.profile_dict[to_use]

    def select_models(self, f, *keys):
        for key in keys:
            if not self.history.in_data(key):
                raise KeyError("'" + str(key) + "' is not a valid data type.")
        p_indices = [self.history.index_of_model_number(m)
                    for m in self.model_numbers]
        arrays = [np.take(self.history.data(key), p_indices) for key in keys]
        return np.take(self.model_numbers, np.where(f(*arrays))[0])
