# keysight_E5071C
Python driver for for Keysight E5071C vector network analyzer

# Disclaimer
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Requirements
numpy  
pyvisa  
visa backend (e.g.: ivi, pyvisa-py, R&S ...)

# Installation

```
git clone https://github.com/mathieu-couillard/keysight_E5071C.git
cd keysight_E5071C
pip install .
cd ..
rm -fr keysight_E5071C
```

# Usage
This driver provides most commands to scan a frequency range and collect traces on any of channels. Commands can change settings individually or change many parameters related to a specific feature (e.g.: set_trigger(), set_averaging(), set_freq_axis(), set_response_axes()) which takes the paramters as arguments, or any arbitrary set of parameters using the set_paramters() which takes as dictionary as an argument(Look at this function to find the dictionary keys).

You can print every command sent using the verbatim=True when instantiating.

Methods with write and query will default to the query when no argument is given.

```
vna.freq_center() # get center frequency
vna.freq_center(5e9) # set center frequency to 5 GHz
```

Two ways to use the code are shown, one shorter:
```
################
# Create object/Connect to device.
################
rm = visa.ResourceManager('@py')
addr = '192.168.0.117'
vna = E5071C(addr)

vna.set_freq_axis(start=1, stop=2, point=1001, bandwidth=1000, sweep_type='lin')
vna.set_set_response_axes(trace_formates=['mlog', 'phase', 'plot'], delay=1, phase_offset=180, Spar='S12')
vna.set_averaging(state='off', count=0)
vna.set_trigger(source='bus', averaging=0, initiate=True)

vna.trigger_now()
data = vna.read()
print(data)
```

Another longer, where each parameter is individually set:
```
################
# Create object/Connect to device.
################
rm = visa.ResourceManager('@py')
addr = '192.168.0.117'
vna = E5071C(addr)
################
# Set up parameters related to frequency scan.
################
vna.freq_start(1) # 1GHz
vna.freq_stop(2) #2GHz
vna.points(1001)
vna.bandwidth(1000)
vna.sweep_type('lin')
################
# Set up trace related commands. Channel related commands are similar.
################
vna.traces_number(3)
vna.active_trace(1)
vna.Format('mlog')
vna.Spar('S12')
vna.delay(1)
vna.phase_offset(180)
vna.active_trace(2)
vna.Format('phase')
vna.Spar('S12')
vna.active_trace(3)
vna.Format('Plog')
vna.Spar('S12')
vna.delay(1)
vna.phase_offset(180)
################
# Set up averaging parameters. Don't forget to set the "vna.trigger_averaging(True)" when using averaging
################
vna.average_state(False)
vna.average_count(0)
################
# Set up averaging parameters.
################
print(vna.trigger_source('bus'))
print(vna.trigger_averaging(False))
print(vna.trigger_initiate(True))
################
# Read the data on the screen
################
print(vna.trigger_now())
print(vna.freq_read())
print(vna.trace_read(1)[0])
print(vna.trace_read(2)[0])
data = vna.trace_read(3)
print(data[0])
print(data[1])
```
