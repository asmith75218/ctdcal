#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:package: ctdcal.parsers.parse_911ctd
:file: ctdcal.parsers.parse_911ctd.py
:author: Allen Smith
:brief: Parse raw hex files for Sea-Bird 911 CTD instruments.
"""
# TODO: replace print statements with logging
# TODO: add missing modules to project requirements
#
import re
from pathlib import Path
from binascii import unhexlify
from struct import unpack

import pandas as pd

from ctdcal.parsers.common import ParserCommon, NEWLINE, NMEA_TIME_BASE


class Parser(ParserCommon):
    """
    Extension of base parser class to parse a hex SBE9plus cast file.
    """
    def __init__(self, infile):
        super().__init__(infile)
        self.config = None

    def configure(self, config_file):
        """
        Fetch metadata from the cast configuration file, which is required
        to properly parse lines of raw hex data, and store in a pandas
        series object.

        :param config_file: JSON cast configuration file
        :return: None
        """
        s = pd.read_json(config_file, orient='index', typ='series')
        s['cc_sensors'] = [d['SensorID'] for d in s['cc_sensors']]

        # Let's add columns with the number of freq and volt channels
        # we DO have, instead of just how many we DON'T have...
        s['freq_num'] = 5 - int(s['cc_frequency_channels_sup'])
        s['volt_num'] = 8 - int(s['cc_voltage_channels_sup'])

        # Finally, let's convert as many strings to numbers as we can
        # now, so we're not stuck doing it each time later...
        self.config = s.apply(pd.to_numeric, errors='ignore')

    def parse_raw(self):
        """
        Extract lines of data from a raw hex file, separate into individual
        components and store in a pandas dataframe object.

        :return: None
        """
        # Get column names...
        columns = self._configure_columns()

        # Hex-string regex pattern
        # ! must be built on the fly since the hex-string format is variable
        # ! depending on the instrument/cast configuration.
        pattern = (r'([0-9A-F]{6})' * self.config['freq_num'] +             # freq channels
                   r'([0-9A-F]{3})' * self.config['volt_num'] +             # voltage channels
                   r'([0-9A-F]{6})' * self.config['cc_has_surfacepar'] +    # surface par
                   r'([0-9A-F]{6})' * self.config['cc_has_nmea_latlon'] +   # nmea lat
                   r'([0-9A-F]{6})' * self.config['cc_has_nmea_latlon'] +   # nmea lon
                   r'([0-9A-F]{2})' * self.config['cc_has_nmea_latlon'] +   # nmea sign/status
                   r'([0-9A-F]{6})' * self.config['cc_has_nmea_depth'] +    # nmea depth
                   r'([0-9A-F]{8})' * self.config['cc_has_nmea_time'] +     # nmea time
                   r'([0-9A-F]{3})' +                                       # pressure temp
                   r'([0-9A-F]{1})' +                                       # status
                   r'([0-9A-F]{2})' +                                       # modulo
                   r'([0-9A-F]{8})' * self.config['cc_has_time'] +          # sys time
                   NEWLINE)
        pattern = re.compile(pattern, re.DOTALL)

        data = []
        print('Matching patterns...')
        for i, line in enumerate(self.raw):
            match = re.match(pattern, line)
            if match:
                row = []
                for ii, value in enumerate(match.groups()):
                    if columns[ii] == 'systime':
                        # ctd time in reverse byte order
                        systime = unpack('I', unhexlify(value))[0]
                        row.append(systime)
                    elif columns[ii] == 'nmea_time':
                        # convert seconds since 1/1/2000 to epoch time
                        #
                        # According to Sea-Bird Sea Save docs, this timestamp will be in
                        # seconds since 2000. Addition of the base value below will
                        # convert to seconds since 1970.
                        # TODO: I don't have example data with a NMEA timestamp so this
                        #     needs to be tested
                        # NMEA time in reverse byte order
                        nmea_time = unpack('I', unhexlify(value))[0] + NMEA_TIME_BASE
                        row.append(nmea_time)
                    elif columns[ii] == 'spar':
                        # surface par
                        #
                        # According to Sea Bird SBE11 docs, first byte and
                        # half of second byte (first 3 hex char) are unused.
                        # TODO: I don't have example data with a surface par so this
                        #     needs to be tested
                        row.append(int(value[3:], 16))
                    else:
                        # Decode everything else as an integer
                        row.append(int(value, 16))
                data.append(row)
            elif not line.startswith('*'):
                # Line is not part of a header and does not match the
                # pattern (likely a corrupt row)...
                print('%s: Line %s does not match expected format.' % (self.infile, i + 1))

        # Store results as a dataframe...
        print('Building table...')
        self.data = pd.DataFrame(data, columns=columns)

    def _configure_columns(self):
        """
        Helper function to build an ordered list of column names using
        the instrument configuration metadata.

        :return: list
        """
        # Frequency channels:
        frequencies_configured = 5 - int(self.config['cc_frequency_channels_sup'])
        columns = ['freq%s' % i for i in range(frequencies_configured)]
        # Voltage channels:
        voltages_configured = 8 - int(self.config['cc_voltage_channels_sup'])
        columns = columns + ['v%s' % i for i in range(voltages_configured)]
        # Surface PAR:
        if int(self.config['cc_has_surfacepar']):
            columns.append('spar')
        # NMEA lat/lon:
        if int(self.config['cc_has_nmea_latlon']):
            columns.append('nmea_lat')
            columns.append('nmea_lon')
            columns.append('nmea_signs_status')
        # NMEA depth:
        if int(self.config['cc_has_nmea_depth']):
            columns.append('nmea_depth')
        # NMEA time:
        if int(self.config['cc_has_nmea_time']):
            columns.append('nmea_time')
        # Pressure temperature, status and modulo:
        columns = columns + ['p_temp', 'status', 'modulo']
        # System time:
        if int(self.config['cc_has_time']):
            columns.append('systime')

        return columns

    def cnv_to_csv(self, outdir, cast_no):
        """
        Save converted data to a compressed csv file.

        Compression level set at 1 (minimum compression) for fastest
        processing speed. Compression is still significant (~80%)

        :param outdir: output directory
        :param cast_no: str
        :return: None
        """
        outfile = Path(outdir, '%s_cnv.zip' % cast_no)
        self.data.to_csv(str(outfile), compression={'method': 'zip', 'compresslevel': 1})


def parse_all_raw(indir, cfgdir, outdir, ext='hex'):
    """
    Function to parse all hex raw data files in a directory and save as
    compressed csv files for future processing.

    :param indir: path of input directory
    :param cfgdir: path of configuration file
    :param outdir: path of output directory
    :param ext: str, filename extension. Defaults to 'hex'.
    :return: None
    """
    p = Path(indir)
    cast_files = [fname for fname in sorted(list(p.glob('*.%s' % ext)))]
    for cast_file in cast_files:
        cast_no = cast_file.stem
        cfgfile = Path(cfgdir, '%s_config.json' % cast_no)
        print("Loading cast %s raw data..." % cast_no)
        parser = Parser(cast_file)
        parser.load_ascii()
        parser.configure(cfgfile)
        parser.parse_raw()
        print("Saving cast %s converted data..." % cast_no)
        parser.cnv_to_csv(outdir, cast_no)
