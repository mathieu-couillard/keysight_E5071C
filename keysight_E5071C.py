"""
June 2022
@author: Mathieu Couillard

Driver for Keysight K5071C Vector Network Analyzer
"""

import numpy as np
import pyvisa as visa

from time import sleep


def format_num(arg, units=1, limits=(-float('inf'),float('inf'))) -> str:
    if arg == None or arg == '?':
        return '?'
    else:
        # TODO: Make dictionary of units
        arg = float(arg)*units
        if arg%1 == 0:
            arg = int(arg)
        if limits[0]<=arg<=limits[1]:
            return ' ' + str(arg)
        else:
            raise Exception("OutOfRangeException: Value must be between {} and {}.".format(limits[0], limits[1]))
        
def format_from_dict(arg, arg_dict) -> str:
    if arg == None:
        arg = '?'
    arg = str(arg).lower()
    try:
        return arg_dict[arg]
    except:
        print("InvalidInputError: Argument must be : {}".format(list(arg_dict.keys())))
        return '?' # FIXME: There should be a better way to handle this error with querying the device.

class E5071C:
    def __init__(self, address, configs="", visa_backend=None, verbatim=False):
        if visa_backend==None:
            self._inst = visa.ResourceManager().open_resource(address)
        else:
            self._inst = visa.ResourceManager(visa_backend).open_resource(address)
        self.verbatim = verbatim
        identity = self.identify()
        print("Identity: {}".format(identity))
        if "E5071C" not in identity:
            Exception("WARNING: The device:{} is not a E5071C vector network analyzer."
                      "\nSome commands may not work.".format(address))

        self.verbatim = verbatim  # Print every command before sending

    ########################################
    # Selecting channel and trace
    ########################################
    def traces_number(self, num=None, chan=""):
        if num != None:
            num = " " + str(num)
        elif num == None:
            num = "?"
        return self._com(":CALC{}:PAR:COUN{}".format(chan, num))

    def displayed_channels(self, chans='?'):
        options = {'1': ' D1',
                   '12': ' D1_2',
                   '13': ' D1_3',
                   '123': ' D1_2_3',
                   '1234': ' D1_2_3_4',
                   '123456': ' D1_2_3_4_5_6',
                   '?': '?'
                   }
        chans = format_from_dict(chans, options)
        return self._com(":DISP:SPL{}".format(chans))

    def active_chan(self, chan=None):
        chan = format_num(chan)
        if chan == '?':
            return self._com(':SERV:CHAN:ACT?')
        else:
            return self._com(":DISP:WIND{}:ACT".format(chan))

    def active_trace(self, trace=None, chan=""):
        trace = format_num(trace)
        if trace == '?':
            return self._com(":SERV:CHAN{}:TRAC:ACT?".format(chan))
        else:
            return self._com(':CALC{}:PAR{}:SEL'.format(chan, trace))

    ########################################
    # Averaging
    ########################################

    def average_reset(self, chan=""):
        return self._com(":SENS{}:AVER:CLE".format(chan))

    def average_count(self, count=None, chan=""):
        count = format_num(count)
        return self._com(":SENS{}:AVER:COUN{}".format(chan, count))

    def average_state(self, state=None, chan=""):
        options = {'on': " on", '1': ' 1', 'true': ' on',
                   'off': ' off', '0': ' 0', 'false': ' 0',
                   '?': '?'
                   }
        state = format_from_dict(state, options)
        return self._com(":SENS{}:AVER:STAT{}".format(chan, state))

    ########################################
    # Frequency axis
    ########################################
    # TODO: Make argument to choose units from a dictionary and make the default GHz
    def freq_start(self, freq=None, chan=""):
        freq = format_num(freq, 1) 
        return self._com(":SENS{}:FREQ:STAR{}".format(chan, freq))

    def freq_stop(self, freq=None, chan=""):
        freq = format_num(freq, 1)
        return self._com(":SENS{}:FREQ:STOP{}".format(chan, freq))

    def freq_center(self, freq=None, chan=""):
        freq = format_num(freq, 1)
        return self._com(":SENS{}:FREQ:CENT{}".format(chan, freq))

    def freq_span(self, freq=None, chan=""):
        freq = format_num(freq, 1)
        return self._com(":SENS{}:FREQ:SPAN{}".format(chan, freq))

    def points(self, points=None, chan=""):
        points = format_num(points) 
        return self._com(":SENS{}:SWE:POIN{}".format(chan, points))

    def ifbw(self, bandwidth=None, chan=""):
        bandwidth = format_num(bandwidth)
        return self._com(":SENS{}:BAND:RES{}".format(chan, bandwidth))

    def bandwidth(self, bandwidth=None, chan=""):
        return self.ifbw(bandwidth, chan)

    ########################################
    # Response
    ########################################
    
    def format_trace(self, trace_format=None, chan=""):
        trace_formats = {'mlog': ' MLOG',
                         'phase': ' PHAS',
                         'lin_mag': ' MLIN',
                         'real': ' REAL',
                         'imag': " IMAG",
                         'extend_phase': ' UPH',
                         'uph': ' UPH',
                         'positive_phase': ' PPH',
                         'pph': ' PPH',
                         'polar_linear': ' PLIN',
                         'plin': ' PLIN',
                         'polar_log': ' PLOG',
                         'plog': ' PLOG',
                         'real_imag': ' POL',
                         '?': '?'}
        trace_format = format_from_dict(trace_format,trace_formats)
        return self._com(':CALC{}:SEL:FORM{}'.format(chan, trace_format))

    ########################################
    # Output
    ########################################

    def delay(self, delay=None, chan=""):
        delay = format_num(delay)
        return self._com(":CALC{}:CORR:EDEL:TIME{}".format(chan, delay))

    def phase_offset(self, phase=None, chan=""):
        phase = format_num(phase)
        return self._com(":CALC{}:CORR:OFFS:PHAS{}".format(chan, phase))

    def power(self, power=None, source=''):
        power = format_num(power)
        return self._com(':SOUR{}:POW{}'.format(source, power))

    def output(self, out=None):
        options = {'true': ' 1',
                   'on': ' 1',
                   '1': ' 1',
                   'false': ' 0',
                   'off': ' 0',
                   '0': ' 0',
                   '?': '?'
                   }
        out = format_from_dict(out, options)
        return self._com(":OUTP{}".format(out))

    def sweep_type(self, sweep_type=None, chan=""):
        sweep_types = {'linear': ' LIN',
                       'lin': ' LIN',
                       'log': ' LOG',
                       'segmented': ' SEG',
                       'power': ' POW',
                       '?': '?'
                       }
        sweep_type = format_from_dict(sweep_type, sweep_types)
        return self._com(':SENS{}:SWE:TYPE{}'.format(chan, sweep_type))

    def s_par(self, s_par=None, trace="", chan=""):
        options = {'s11': ' S11', 's12': ' S12', 's13': ' S13', 's14': ' S14',
                   's21': ' S21', 's22': ' S22', 's23': ' S23', 's24': ' S24',
                   's31': ' S31', 's32': ' S32', 's33': ' S33', 's34': ' S34',
                   's41': ' S41', 's42': ' S42', 's43': ' S43', 's44': ' S44',
                   '?': '?'
                   }
        s_par = format_from_dict(s_par,options)
        if s_par in options:
            return self._com(':CALC{}:PAR{}:DEF{}'.format(chan, trace, s_par))

    ########################################
    # Trigger
    ########################################
    def trigger_source(self, source=None):
        sources = {"internal": " INT",
                   "external": " EXT",
                   "manual": " MAN",
                   "bus": " BUS",
                   "?": "?"
                   }
        source = format_from_dict(source, sources)
        return self._com(":TRIG:SOUR{}".format(source))


    def trigger_initiate(self, state=None, chan=""):
        options = {"cont": ":CONT ON",
                   "hold": ":CONT OFF",
                   "single": "",
                   "?": "?"
                   }
        state = format_from_dict(state, options)
        return self._com('INIT{}{}'.format(chan, state))

    def trigger_now(self):
        if self.average_state() == 1:
            average_count = self.average_count()
        else:
            average_count = 1
            
        self._com(":TRIG:SING")
        sweep_time = float(self.get_sweep_time())
        sleep(int(average_count) * sweep_time)
        return 'Sent: :TRIG:SING \nMeasuremet complete {}'.format(self.operation_complete())


    def trigger_averaging(self, averaging=None):
        options = {"on": " ON", "1": " 1", "true": " 1",
                   "off": " OFF", "0": " 0", "false": " 0",
                   "?": "?"
                   }
        averaging = format_from_dict(averaging, options)
        return self._com(":TRIG:SEQ:AVER{}".format(averaging))

    ########################################
    # reading data
    ########################################

    def format_data(self, form=None):
        formats = {'ascii': ' ASC',
                   'asc': ' ASC',
                   'real': ' REAL',
                   'real32': ' REAL32',
                   '?': '?'
                   }
        form = format_from_dict(form, formats)
        return self._com(':FORMat:DATA{}'.format(form))

    def read_freq(self):
        self.format_data('real')
        data = self._com_binary(':CALC:SEL:DATA:XAXis?')
        self.format_data('ascii')
        return data

    def read_trace(self, trace=None):
        if trace==None:
            trace = '?'
        self.format_data('real')
        data = self._com_binary(':CALC:TRACe{}:DATA:FDATa?'.format(trace))
        self.format_data('ascii')

        return data[0::2], data[1::2]

    def read_all_traces(self):
        # read the x axis and all traces of the active channel
        traces = int(self.traces_number())
        points = int(self.points())
        
        data = np.empty((2*traces+1, points))
        self.format_data('real')

        data[0] = self._com_binary(':CALC:SEL:DATA:XAXis?')
        for trace in range(traces):
            raw_data = self._com_binary(':CALC:TRACe{}:DATA:FDATa?'.format(trace+1))
            data[2*trace + 1] = raw_data[0::2]
            data[2*trace + 2] = raw_data[1::2]

        self.format_data('ascii')
        return data


    def close(self):
        self._inst.close()

    def identify(self):
        return self._com("*IDN?")

    def idn(self):
        return self._com("*IDN?")

    def reset(self):
        return self._com('*RST')

    def rst(self):
        return self._com('*RST')
        
    def operation_complete(self):
        return self._com("*OPC?")

    def opc(self):
        return self.operation_complete()
 
    def get_sweep_time(self):
        return self._com("SENS:SWE:TIME?")

    
    ########################################
    # parameters
    ########################################
    def set_trigger(self, source='bus', averaging=0, initiate="single"):
        self.trigger_source(source)
        self.trigger_averaging(averaging)
        self.trigger_initiate(initiate)

    def set_averaging(self, state=None, count=0):
        state = str(state)
        self.average_state(state)
        self.average_count(count)

    def set_freq_axis(self, start="", stop="", center="", span="", point=1000, bandwidth=1000, sweep_type='lin'):
        if type(start) != str:
            self.freq_start(start)
        if type(stop) != str:
            self.freq_stop(stop)
        if type(center) != str:
            self.freq_center(center)
        if type(span) != str:
            self.freq_span(span)

        self.points(point)
        self.bandwidth(bandwidth)
        self.sweep_type(sweep_type)

    def set_response_axes(self, trace_formats, delay, phase_offset, s_par='S12'):
        if type(trace_formats) == str:
            trace_formats = [trace_formats]
        if s_par == str:
            s_par = [s_par] * len(trace_formats)
        self.delay(delay)
        self.phase_offset(phase_offset)
        self.traces_number(len(trace_formats))
        for i, trace_format in enumerate(trace_formats):
            self.active_trace(i + 1)
            self.s_par(s_par)
            self.format_trace(trace_format)

    def get_parameters(self, chan=""):

        # total_traces = self.traces_number(chan)

        parameters = {'freq_start': self.freq_start(),
                      'freq_stop': self.freq_stop(),
                      'freq_center': self.freq_center(),
                      'freq_span': self.freq_span(),
                      'points': self.points(),
                      'bandwidth': self.bandwidth(),
                      'format_trace': self.format_trace(),  # get this for each channel
                      's_par': self.s_par(),  # get this for each channel
                      'power': self.power,
                      'average_count': self.average_count(),
                      'average_state': self.average_state(),
                      'delay': self.delay(),
                      'phase_offset': self.phase_offset()
                      }
        return parameters

    def set_parameters(self, chan="", **kwargs):
        # TODO: test this and read get **kwargs from a config file
        parameters = {'freq_start': self.freq_start,
                      'freq_stop': self.freq_stop,
                      'freq_center': self.freq_center,
                      'freq_span': self.freq_span,
                      'points': self.points,
                      'bandwidth': self.bandwidth,
                      'format_trace': self.format_trace,  # set this for each channel
                      's_par': self.s_par,  # set this for each channel
                      'power': self.power,
                      'average_count': self.average_count,
                      'average_state': self.average_state,
                      'delay': self.delay,
                      'phase_offset': self.phase_offset
                      }

        # need to figure out how to format the trace specific parameters like format
        for i in kwargs.keys():
            try:
                parameters[i](kwargs[i])
            except KeyError:
                pass

    ##############################
    # send commands
    ##############################
    
    def _com(self, cmd):
        if self.verbatim:
            print(cmd)
        if cmd[-1] == '?':
            value = self._inst.query(cmd)
            try:
                return float(value)
            except:
                return value
            # try:
            #     return float(value)
            # except:
            #     return value
        else:
            self._inst.write(cmd)
            return "Sent: " + cmd

    def _com_binary(self, cmd):
        if self.verbatim:
            print(cmd)
        if cmd[-1] == '?':
            return self._inst.query_binary_values(cmd, datatype='d', is_big_endian=True)
        else:
            # TODO: Test this section
            self._inst.write_binary_values(cmd, datatype='d', is_big_endian=True)
            return "Waveform sent"


if __name__ == "__main__":
    ################
    # Create object/Connect to device.
    ################
    rm = visa.ResourceManager('@py')
    ip = '192.168.0.100'
    vna = E5071C("TCPIP::{}::INSTR".format(ip))
    ################
    # Set up parameters related to frequency scan.
    ################
    vna.freq_start(6.17)
    vna.freq_stop(6.25)
    vna.points(1001)
    vna.bandwidth(1000)
    vna.sweep_type('lin')
    ################
    # Set up trace related commands. Channel related commands are similar.
    ################
    vna.traces_number(2)
    vna.active_trace(1)
    vna.s_par('S33')
    print(vna.format_trace('mlog'))
    vna.delay(1)
    vna.phase_offset(15)
    print(vna.active_trace(2))
    vna.s_par('S33')
    vna.delay(1)
    vna.phase_offset(15)
    print(vna.format_trace('phase'))
    # print(vna.active_trace(3))
    # vna.s_par('S12')
    # vna.delay(1)
    # vna.phase_offset(180)
    # print(vna.format_trace('Plog'))
    ################
    # Set up averaging parameters. Don't forget to set the "vna.trigger_averaging(True)" when using averaging
    ################
    print(vna.average_state(False))
    print(vna.average_count(0))
    ################
    # Set up averaging parameters.
    ################
    print(vna.trigger_source('bus'))
    print(vna.trigger_averaging(0))
    print(vna.trigger_initiate('single'))
    print(vna.trigger_now())
    ################
    # Read the data on the screen
    ################
    # print(vna.read_freq())
    # print(vna.read_trace(1)[0])
    # print(vna.read_trace(2)[0])
    # data = vna.read_trace(3)
    # print(data[0])
    # print(data[1])
    data = vna.read_all_traces()  # This command gets values for x axis and the primary and secondary data for all the traces.
