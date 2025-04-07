import pyaudio
import librosa

import numpy as np
from scipy.fftpack import fft, ifft
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import wave
import time
import os
import sys
import contextlib

@contextlib.contextmanager
def suppress_stderr():
    """A context manager that redirects stderr to devnull"""
    stderr = sys.stderr
    devnull = open(os.devnull, 'w')
    sys.stderr = devnull
    try:
        yield
    finally:
        sys.stderr = stderr
        devnull.close()

class AudioDevices:
    def __init__(self):
        # Initialize PyAudio with stderr suppressed to hide ALSA error messages
        with suppress_stderr():
            self.p = pyaudio.PyAudio()
        
        # Get Devices
        self.devices = self.get_all_devices()
        self.inputs = self.getAudioDevices('input')
        self.outputs = self.getAudioDevices('output')
        
        # Currently Set Devices
        self.mic_input = None
        self.mic_output = None
        self.speaker = None
        
        # Print Info
        self.print_info()
        
    def get_all_devices(self):
        """Get all audio devices using PyAudio"""
        devices = []
        for i in range(self.p.get_device_count()):
            device_info = self.p.get_device_info_by_index(i)
            devices.append(device_info)
        return devices

    def getAudioDevices(self, device_type):
        """
        Retrieves a dictionary of audio devices filtered by type (input/output).
        Includes the default device and devices containing 'CABLE Input' or 'CABLE Output' in their names.

        Args:
            device_type (str): 'input' or 'output' to specify the type of device.

        Returns:
            dict: A dictionary with device names as keys and their indices as values.
        """
        if device_type not in ['input', 'output']:
            raise ValueError("Invalid device_type. Must be 'input' or 'output'.")

        # Initialize a dictionary for filtered devices
        filtered_devices = {}

        # Get the default device for the specified type
        default_host_api_info = self.p.get_default_host_api_info()
        default_device_index = default_host_api_info['defaultInputDevice'] if device_type == 'input' else default_host_api_info['defaultOutputDevice']
        
        if default_device_index >= 0:  # -1 means no default device
            default_device_info = self.p.get_device_info_by_index(default_device_index)
            default_device_name = default_device_info['name']
            filtered_devices[default_device_name] = default_device_index

        # Add devices containing "CABLE Input" or "CABLE Output" in their names
        for device in self.devices:
            device_name = device['name']
            index = device['index']
            max_channels = device['maxInputChannels'] if device_type == 'input' else device['maxOutputChannels']
            
            if max_channels > 0:  # Device supports this direction
                if device_type == 'input' and "CABLE Input" in device_name:
                    filtered_devices[device_name] = index
                elif device_type == 'output' and ("CABLE Input" in device_name):
                    filtered_devices[device_name] = index
        
        # Remove the Following if they are in the list:
        # - "CABLE Input (VB-Audio Virtual C"
        # - "CABLE Output (VB-Audio Virtual "
        # - "CABLE Output (VB-Audio Point)"
        # filtered_devices = {k: v for k, v in filtered_devices.items() if k not in ["CABLE Input (VB-Audio Virtual C", "CABLE Output (VB-Audio Virtual ", "CABLE Output (VB-Audio Point)"]}

        return filtered_devices
    
    def refresh_devices(self):
        self.p.terminate()
        # Initialize with stderr suppressed
        with suppress_stderr():
            self.p = pyaudio.PyAudio()
        self.devices = self.get_all_devices()
        self.outputs = self.getAudioDevices('output')
        self.inputs = self.getAudioDevices('input')
        self.print_info()
    
    def get_device_index(self, device_name):
        for device in self.devices:
            if device['name'] == device_name:
                return device['index']
        return None

    def print_info(self):
        print("\n\033[94m-- Audio Devices --\033[0m")
        print(f'Total Number of Devices: {len(self.devices)}')
        print(f'Total Number of Output Devices: {len(self.outputs)} ({", ".join(self.outputs.keys())})')
        print(f'Total Number of Input Devices: {len(self.inputs)} ({", ".join(self.inputs.keys())})')

class AudioRouting:
    def __init__(self, audio_devices, audio_values):
        # Existing initialization code
        self.audio_devices = audio_devices
        self.audio_values = audio_values
        self.stream = None
        self.running = False
        
        # PyAudio-specific attributes
        self.p = self.audio_devices.p  # Use the existing PyAudio instance
        self.stream_callback = None
        self.buffer = None
        
        # Add new attributes for spectral analysis
        self.fft_data = None
        self.fig = None
        self.ax = None
        self.line = None
        self.animation = None
        self.spectrum_enabled = False
        
        # First Instance
        self.first_instance = True
        
    # Add a method to start the spectrum analyzer
    def start_spectrum_analyzer(self):
        if not self.running:
            print("Cannot start spectrum analyzer: Audio routing not running")
            return
            
        self.spectrum_enabled = True
        self.fig, self.ax = plt.figure(figsize=(10, 6)), plt.axes(xlim=(0, 5000), ylim=(0, 1))
        self.ax.set_title('Real-time Audio Spectrum')
        self.ax.set_xlabel('Frequency (Hz)')
        self.ax.set_ylabel('Amplitude')
        self.line, = self.ax.plot([], [], lw=2)
        
        def init():
            self.line.set_data([], [])
            return self.line,
            
        def animate(i):
            if self.fft_data is not None:
                self.line.set_data(self.fft_data[0], self.fft_data[1])
            return self.line,
            
        self.animation = FuncAnimation(self.fig, animate, init_func=init, 
                                      interval=50, blit=True)
        plt.show(block=False)
        
    def stop_spectrum_analyzer(self):
        if self.animation:
            self.animation.event_source.stop()
            plt.close(self.fig)
        self.spectrum_enabled = False

    def start_route(self, speaker, mic_input, mic_output):
        # If Already Running, Return
        if self.running:
            return
        
        # Get the Device Indices for the Devices if they are indices
        if isinstance(speaker, int):
            speaker_info = self.p.get_device_info_by_index(speaker)
        else:
            # Find the device by name
            speaker_info = None
            for i in range(self.p.get_device_count()):
                info = self.p.get_device_info_by_index(i)
                if info['name'] == speaker:
                    speaker_info = info
                    break
            if not speaker_info:
                print(f"Could not find speaker device: {speaker}")
                return
        
        # Do the same for input and output
        if isinstance(mic_input, int):
            mic_input_info = self.p.get_device_info_by_index(mic_input)
        else:
            mic_input_info = None
            for i in range(self.p.get_device_count()):
                info = self.p.get_device_info_by_index(i)
                if info['name'] == mic_input:
                    mic_input_info = info
                    break
            if not mic_input_info:
                print(f"Could not find input device: {mic_input}")
                return
        
        if isinstance(mic_output, int):
            mic_output_info = self.p.get_device_info_by_index(mic_output)
        else:
            mic_output_info = None
            for i in range(self.p.get_device_count()):
                info = self.p.get_device_info_by_index(i)
                if info['name'] == mic_output:
                    mic_output_info = info
                    break
            if not mic_output_info:
                print(f"Could not find output device: {mic_output}")
                return
        
        # Set the Devices
        self.audio_devices.mic_input = mic_input_info
        self.audio_devices.mic_output = mic_output_info
        self.audio_devices.speaker = speaker_info
        
        # Use the Lower Channel Count to Ensure Compatibility
        channel_count = min(int(mic_input_info['maxInputChannels']), int(mic_output_info['maxOutputChannels']))
        channel_count = max(1, channel_count)  # Ensure at least mono
        
        # Use a common Sample Rate
        sample_rate = int(mic_input_info['defaultSampleRate'])
        
        # Configure format
        format_type = pyaudio.paFloat32  # Using float32 for better quality and compatibility with DSP
        
        # Print the Indices
        self.print_routing_info(mic_input_info['index'], mic_output_info['index'], channel_count, sample_rate)
        
        # Create a buffer to store audio data
        self.buffer_size = 1024  # standard buffer size
        
        try:
            # Define the callback function for streaming
            def pyaudio_callback(in_data, frame_count, time_info, status):
                # Convert buffer to numpy array
                indata = np.frombuffer(in_data, dtype=np.float32).reshape(-1, channel_count)
                
                # Create output buffer
                outdata = np.zeros((frame_count, channel_count), dtype=np.float32)
                
                # Process audio using our existing method
                self.process_audio(indata, outdata, frame_count, time_info, status)
                
                # Convert numpy array back to bytes
                return (outdata.tobytes(), pyaudio.paContinue)
            
            # Store the callback function
            self.stream_callback = pyaudio_callback
            
            # Start the Stream with stderr suppressed
            with suppress_stderr():
                self.stream = self.p.open(
                    format=format_type,
                    channels=channel_count,
                    rate=sample_rate,
                    input=True,
                    output=True,
                    input_device_index=mic_input_info['index'],
                    output_device_index=mic_output_info['index'],
                    frames_per_buffer=self.buffer_size,
                    stream_callback=pyaudio_callback
                )
            
            self.running = True
        except Exception as e:
            print(f"Error starting stream: {e}")
        
    def stop_route(self):
        # Reset the Devices
        self.audio_devices.mic_input = None
        self.audio_devices.mic_output = None
        self.audio_devices.speaker = None
        self.stop_spectrum_analyzer()
        
        if self.stream:
            print(f"\033[91mStopping Audio Routing...\033[0m")
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            self.running = False
    
    def get_device_index(self, device_name):
        return self.audio_devices.get_device_index(device_name)
    
    def print_routing_info(self, input_index, mic_output_index, channel_count, sample_rate):
        print(f"\n\033[91m-- Audio Routing Starting... --\033[0m")
        print(f"Input Index: {input_index}")
        print(f"Mic Output Index: {mic_output_index}")
        print(f"Channel Count: {channel_count}")
        print(f"Sample Rate: {sample_rate}")







    def process_audio(self, indata, outdata, frames, time_info, status):
        """
        Audio callback function that processes input audio data and routes it to output.
        Now includes spectral analysis and reconstruction.
        """
        if status:
            print(f"Status: {status}")
        
        original_audio = indata.copy()
        
        # Perform FFT if spectrum analyzer is enabled
        if self.audio_values.get_spectrum():
            # Get sample rate from the input device
            sample_rate = int(self.audio_devices.mic_input['defaultSampleRate'])
            
            # Compute FFT (use only first channel if stereo)
            audio_data = indata[:, 0] if indata.ndim > 1 else indata
            
            # Store the complete FFT result (including phase information)
            self.complete_fft_result = fft(audio_data)
            
            # For visualization purposes only
            fft_result = self.complete_fft_result.copy()
            n = len(audio_data)
            freq_bins = np.fft.fftfreq(n, 1/sample_rate)
            
            # Get the positive frequencies (for visualization)
            positive_mask = freq_bins > 0
            freq_bins_positive = freq_bins[positive_mask]
            fft_magnitude = np.abs(fft_result[positive_mask]) / n  # Normalize
            
            # Apply noise threshold to the magnitude for visualization
            noise_threshold = self.audio_values.get_noise_threshold()
            fft_magnitude[fft_magnitude < noise_threshold] = 0
            
            # Store the FFT data for plotting
            self.fft_data = (freq_bins_positive, fft_magnitude)
        
        # Reconstruct audio from FFT data if needed
        if hasattr(self, 'complete_fft_result'):
            # Apply noise threshold to the complete FFT result if desired
            if self.audio_values.get_spectrum():
                # Apply noise threshold to the complete FFT result
                noise_threshold = self.audio_values.get_noise_threshold()
                n = len(self.complete_fft_result)
                # Create mask using normalized magnitudes
                mask = np.abs(self.complete_fft_result) / n < noise_threshold
                filtered_fft = self.complete_fft_result.copy()
                filtered_fft[mask] = 0
                
                # Ensure the DC component (0 Hz) is preserved
                if len(filtered_fft) > 0:
                    filtered_fft[0] = self.complete_fft_result[0]
                
                # Ensure conjugate symmetry for real input
                if n % 2 == 0:  # If even number of samples
                    filtered_fft[n//2] = self.complete_fft_result[n//2]
                
                # Use inverse FFT to reconstruct the audio
                reconstructed_audio = ifft(filtered_fft).real
                
                # Handle stereo if needed
                if indata.ndim > 1:
                    reconstructed_audio = np.column_stack([reconstructed_audio] * indata.shape[1])
                
                indata = reconstructed_audio
        
        # Apply volume adjustment
        indata *= self.audio_values.get_volume() / 100.0
        
        # Route audio to output
        outdata[:] = indata


class AudioValues:
    def __init__(self):
        self.volume = 100
        self.noise_threshold = 0
        self.spectrum_enabled = True
    
    def set_spectrum(self, enabled):
        self.spectrum_enabled = enabled
    
    def get_spectrum(self):
        return self.spectrum_enabled
    
    def set_noise_threshold(self, noise_threshold):
        self.noise_threshold = noise_threshold
    
    def get_noise_threshold(self):
        return self.noise_threshold
    
    def set_volume(self, volume):
        self.volume = volume
    
    def get_volume(self):
        return self.volume