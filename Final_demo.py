from __future__ import division

import re
import sys
import os

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio #for recording audio!
import pygame  #for playing audio
import random
from six.moves import queue

from gtts import gTTS
import os
import time
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import NeoPixel


num_pixels = 37  # Number (37) of pixels driven from Crickit NeoPixel terminal

# The following line sets up a NeoPixel strip on Seesaw pin 20 for Feather
pixels = NeoPixel(crickit.seesaw, 20, num_pixels)
#pixels_b = NeoPixel(crickit.seesaw, 20, 34)
crickit.servo_2.angle = 0

# Define the basic color.
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 100, 100)
PURPLE = (180, 0, 255)
OFF = (0,0,0)
WHITE = (255,255,255)
A = (120, 200, 130)
B = (240, 90, 0)
C = (20, 50, 240)

# Audio recording parameters, set for our USB mic.
RATE = 48000 #if you change mics - be sure to change this :) 44100
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

    # Scene_1
    #if re.search("sad",transcript, re.I):
        #scene_1()

    # Scene_2
    if re.search("relax",transcript, re.I):
        scene_2()

    # Scene_3
    if re.search("(ridiculous)|(bad)", transcript, re.I):
        scene_3()

    # Scene_4
    if re.search("party", transcript, re.I):
        scene_4()
        
    if re.search("eigenvalue", transcript, re.I):
        pixels.fill(OFF)


    #if re.search("exciting", transcript, re.I):

# Sad
def scene_1():

    Speaker_Action('scene_1.mp3')
    
    pixels.fill(OFF)

    for i in range(0, num_pixels):
        if i < 34 and i%2 == 0:
            pixels[i] = YELLOW
            pixels.brightness = 0.1
            pixels.show()
            
    time.sleep(16)
    
    for i in range(0, num_pixels):
        if i < 34:
            pixels[i] = WHITE
    #Motor
    #Motor_Action('scene_1')

# Relax: relax
def scene_2():
    # Breathing.
    
    crickit.servo_2.angle = 180
    
    
    pixels.fill(OFF)

    Speaker_Action('scene_2.mp3')


    for i in range(0, num_pixels):
        if i < 34 and i%2 == 0:
            pixels[i] = BLUE
            
    time.sleep(15)

    
    for i in range(0, num_pixels):
        if i < 34:
            pixels[i] = WHITE
    
    #crickit.servo_2.angle = 30
    #time.sleep(1)
    #crickit.servo_2.angle = 180
    #time.sleep(1)
    #crickit.servo_2.angle = 30
    #time.sleep(1)
    #crickit.servo_2.angle = 180

# Conflict: Ridiculous
def scene_3():

    Speaker_Action('scene_3.mp3')
    # Light
    
    #fill_b(RED)
    #pixels.fill(OFF)
    time.sleep(1)
    pixels.fill(RED) # 1 hit
    time.sleep(0.06)
    pixels.fill(OFF)
    time.sleep(0.8)
    pixels.fill(RED) # 2 hit
    pixels.fill(OFF)
    time.sleep(0.86)
    pixels.fill(RED) # 3 hit
    pixels.fill(OFF)
    time.sleep(0.86)
    for i in range (0, 3):
        pixels[34], pixels[35], pixels[36] = YELLOW, BLUE, GREEN
        time.sleep(0.16)
        pixels.fill(OFF)
    
    pixels.fill(RED)
    pixels.fill(OFF)
    time.sleep(0.88)
    pixels.fill(RED) # 1 hit
    pixels.fill(OFF)
    time.sleep(0.88)
    pixels.fill(RED) # 2 hit
    pixels.fill(OFF)
    time.sleep(0.6)
    for i in range (0, 3):
        pixels[34], pixels[35], pixels[36] = YELLOW, BLUE, GREEN
        time.sleep(0.16)
        pixels[34], pixels[35], pixels[36] = OFF, OFF, OFF
    
    pixels.fill(RED)
    pixels.fill(OFF)
    time.sleep(1)
    pixels.fill(RED) # 1 hit
    pixels.fill(OFF)
    time.sleep(0.89)
    pixels.fill(RED) # 2 hit
    pixels.fill(OFF)
    time.sleep(0.89)

    for i in range (0, 3):
        pixels[34], pixels[35], pixels[36] = YELLOW, BLUE, GREEN
        time.sleep(0.16)
        pixels[34], pixels[35], pixels[36] = OFF, OFF, OFF
    
    time.sleep(0.01)
    pixels.fill(RED)
    pixels.fill(OFF)
    time.sleep(0.89)
    pixels.fill(RED) # 1 hit
    pixels.fill(OFF)
    time.sleep(0.89)
    pixels.fill(RED) # 2 hit
    pixels.fill(OFF)
    time.sleep(0.6)
    
    
    
    for i in range (0, 3):
        pixels[34], pixels[35], pixels[36] = YELLOW, BLUE, GREEN
        time.sleep(0.16)
        pixels.fill(OFF)
        
    for i in range(0, num_pixels):
        if i < 34:
            pixels[i] = WHITE
    
        
    

# Party
def scene_4():
    Speaker_Action('scene_4.mp3')
    for i in range(0,60):
        pixels.fill((random.randint(20,255),random.randint(20,255),random.randint(20,255)))
        time.sleep(0.1)
        pixels.fill(OFF)
    
    for i in range(0, num_pixels):
        if i < 34:
            pixels[i] = random.choice([PURPLE, GREEN, CYAN, YELLOW, BLUE, RED, WHITE, (240, 90, 0), (120, 200, 130), (10, 20, 230)])
    
    for i in range (0, 50):
        Y = random.choice([(240, 90, 0), (120, 200, 130), (10, 20, 230)])
        B = random.choice([YELLOW, BLUE, RED])
        G = random.choice([PURPLE, GREEN, CYAN])
        pixels[34], pixels[35], pixels[36] = Y, B, G #Need to be random.
        time.sleep(0.2)
        pixels[34], pixels[35], pixels[36] = OFF, OFF, OFF
    
    for i in range(0, num_pixels):
        if i < 34:
            pixels[i] = WHITE
    


def Speaker_Action(file):
    pygame.mixer.init()
    pygame.mixer.music.load(file)
    pygame.mixer.music.play()
    #while pygame.mixer.music.get_busy():
           # pygame.time.Clock().tick(10)

def Moter_Action(scene):
    if scene == 'scene_2':
        # motor.servo.2
        crickit.servo_2.angle = 180 # Need to change.
        #time.sleep(0.5)
        #crickit.servo_2.angle = 20
        time.sleep(12)
        crickit.servo_2.angle = 0


# Lighting effect.


def Chasing(color = BLUE, gap = 0.03):
    for i in range(0, num_pixels):
        pixels[i] = color
        time.sleep(gap)
        pixels.show()

def Party():
    Speaker_Action('scene_4.mp3')
    for i in range(0,80):
        pixels.fill((random.randint(1,255),random.randint(1,255),random.randint(1,255)))
        time.sleep(0.1)
        pixels.fill(OFF)

def fill_b(color):
    for i in range(0, num_pixels):
        if i < 34:
            pixels[i] = color



def main():
    language_code = 'en-US'  # a BCP-47 language tag
    print("LED initialize white")
    
    #crickit.servo_2.angle = 5

    #INIT = (255, 255, 255)
    #pixels.fill(WHITE)
    for i in range(0, num_pixels):
        if i < 34:
            pixels[i] = WHITE

    #set up a client
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=RATE,
        language_code=language_code)

    streaming_config = types.StreamingRecognitionConfig(
        config=config,
        interim_results=True)


    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (types.StreamingRecognizeRequest(audio_content=content)
                    for content in audio_generator)

        responses = client.streaming_recognize(streaming_config, requests)

        # Now, put the transcription responses to use.
        listen_print_loop(responses)


if __name__ == '__main__':
    main()
