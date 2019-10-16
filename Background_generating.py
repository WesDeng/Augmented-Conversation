import time
import signal
import sys
import re

import random
from pydub import AudioSegment

carmen = AudioSegment.from_mp3('Carmen.mp3')[:16000].fade_out(4000)
carmen.export('carmen_.mp3', format = 'mp3')
party = AudioSegment.from_mp3('Jagger.mp3')[60500:76000].fade_out(4000)
party.export('party_.mp3', format = 'mp3')
relax = AudioSegment.from_mp3('Relax.mp3')[:15000].fade_out(4000)
relax.export('relax_.mp3', format = 'mp3')
sad = AudioSegment.from_mp3('Mad.mp3')[6200: 24000].fade_out(4000)
sad.export('sad_.mp3', format = 'mp3')
