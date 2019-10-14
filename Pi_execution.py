from __future__ import division

import re
import sys
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio #for recording audio!
import pygame  #for playing audio
from six.moves import queue

from gtts import gTTS
import os
import time
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import NeoPixel

num_pixels = 10  # Number of pixels driven from Crickit NeoPixel terminal

# The following line sets up a NeoPixel strip on Seesaw pin 20 for Feather
pixels = NeoPixel(crickit.seesaw, 20, num_pixels)

# Audio recording parameters, set for our USB mic.
RATE = 44100 #if you change mics - be sure to change this :)
CHUNK = int(RATE / 10)  # 100ms

credential_path = "/home/pi/DET_wesley.json" #replace with your file name!
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=credential_path

client = speech.SpeechClient()

pygame.init()
pygame.mixer.init()
#MicrophoneStream() is brought in from Google Cloud Platform
class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)


def listen_print_loop(responses):
    """Iterates through server responses and prints them.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
#            sys.stdout.write(transcript + overwrite_chars + '\r')
#            sys.stdout.flush()
            num_chars_printed = len(transcript)

        else:
            print(transcript + overwrite_chars)
            #if there's a voice activitated quit - quit!
            if re.search(r'\b(exit|quit)\b', transcript, re.I):
                print('Exiting..')
                break
            else:
                decide_action(transcript)
#            print(transcript)
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            num_chars_printed = 0

def decide_action(transcript):

    #here we're using some simple code on the final transcript from
    #GCP to figure out what to do, how to respond.

    if re.search("hey",transcript, re.I):
        Speaker_Action('greeting_1')
        LED_Action('speaking')

    if re.search("stressful",transcript, re.I):
        t2s = gTTS("You got this! Here's something for you!", lang ='en')
        t2s.save('stressful.mp3')
        Speaker_Action('stressful.mp3')
        # Something to pause.
        Speaker_Action('believer.mp3')

    if re.search("what's up", transcript, re.I):
        Speaker_Action('greeting_1')
        LED_Action('speaking')

    if re.search("exciting", transcript, re.I):
        t2s = gTTS("", lang ='en')
        t2s.save('exciting.mp3')
        Speaker_Action('exciting.mp3')
        # Something to pause.
        Speaker_Action('believer.mp3')

def scene_1():

    # Sound
    Speaker_Action('chopin.mp3')
    # Light
    LED_Action('scene_1')
    # Motor
    Motor_Action('scene_1')


def scene_2():
    # Sound
    Speaker_Action('believer.mp3')
    # Light
    LED_Action('scene_2')
    # Motor
    Motor_Action('scene_2')


def Speaker_Action(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)




def LED_Action(scene):

    ss = crickit.seesaw

    RED = (255, 0, 0)
    YELLOW = (255, 150, 0)
    GREEN = (0, 255, 0)
    CYAN = (0, 255, 255)
    BLUE = (0, 0, 255)
    PURPLE = (180, 0, 255)
    OFF = (0,0,0)

    print("LED initialize off")
    pixels.fill(OFF)

    if scene == 'speaking':
        pixels[0].fill(OFF)
        for i in range(5):
            pixels[1].fill(BLUE)
            time.sleep(0.1)
            pixels.show()

    elif scene == 'chopin':
        pixels[1].fill(OFF)
        pixels[0].fill(CYAN)

    elif scene == 'believer':
        pixels[1].fill(OFF)
        for i in range(5):
            pixels[1].fill(YELLOW)
            time.sleep(0.1)
            pixels.show()

def Motor_Action(scene):

    if bears == 'bears':
        crickit.servo_1.angle = 0      # right
        time.sleep(1)
    elif bears == 'cardinal':
        crickit.servo_1.angle = 180
        time.sleep(1)


def main():

    #Get conversations set up.
    t2s = gTTS('Hey there, how are you doing this morning?', lang ='en')
    t2s.save('greeting_1.mp3')
    t2s = gTTS("Good morning! I see that your calendar is free. What you up to toady?", lang='en')
    t2s.save('greeting_2.mp3')

    language_code = 'en-US'  # a BCP-47 language tag

    #set up a client
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)

    #this section is where the action happens:
    #a microphone stream is set up, requests are generated based on
    #how the audiofile is chunked, and they are sent to GCP using
    #the streaming_recognize() function for analysis. responses
    #contains the info you get back from the API.
    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


if __name__ == '__main__':
    main()
