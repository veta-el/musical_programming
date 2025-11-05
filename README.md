# musical_programming
Musical programming

This project is an experiment to create a CMD-DAW (digital audio workstation), something in between a music programming language and a DAW program with an interface. Suitable for live sessions.

# threads and exec/eval are often used, be careful!!!

Features:
1. 10 tracks
2. For audiofiles are used: format = pyaudio.paInt16, channels = 1, rate = 16000
3. Empty.wav should NOT be deleted - it is used as the basis inside some functions.

Functions:
1. bpm - you can set the desired bpm or change it during session
2. edit - a function to change existing user samples, options:

inversion - just inversion of audio

speed - speeds up or slows down audio by n times

echo - adds an echo effect, select the number of echoes and the time between echoes

3. mic_record - recording from a microphone with real-time playback and/or saving to a separate file (you can add an echo)
4. pattern - creating a musical pattern from selected samples, where you can "tap out" the rhythm. You can just save it, or you can immediately use it in your work.
5. play - the main function for playing samples. Places the selected sample on the selected track (not occupied) and repeats the specified number of times after the selected interval or by tying to the bpm. What accepts as input:
	
object name - the name of the sample/the path to the sample without extension 
  
thread number - track number (1-10)
  
part from start - which part of the sample to use
  
number of repeats - number of repaets of the sample
  
seconds between repeats - number of seconds between repeats (one of the formulas can be used to dynamically change the number or be linked to bpm)
  
volume - volume (can also be dynamically changed by formula)
  
6. stop - stop the selected track
7. exit - exit

   
You can find out more about each function in the help command.

Automation:
Implemented for volume and repeats of the audio sample. This happens by changing the parameters according to one of the formulas:

y = kx + b

y = ax^2 + bx + c

y = x^power

y = a^x

y = x^1/2


The program runs in a loop, each time offering a choice of the desired function to perform.
