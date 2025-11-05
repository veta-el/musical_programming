import threading
import numpy
import time

import pyaudio
import audioop
import wave

###Main functions
def bpm(): #to count bpm
    global bpm_flag
    global bpm_checker
    global ex
    while ex == 0: #Global exit - ex
        bpm_flag = '-'
        time.sleep (60/bpm_checker)
        bpm_flag = '+'
        time.sleep(0.05)

def edit (data, samplewidth, number_of_echo, time_between_echo, type_function):
    if type_function=='invers': #inversion
        data = audioop.reverse (data, 2)
        print ('Reverse is done')
        return data

    if type_function=='echo': #echo
        echo_data_fade = audioop.mul(data, samplewidth, (1-1/number_of_echo))
        echo_repeats = 1-(2*(1/number_of_echo))
        echo_data_string = numpy.fromstring (data, numpy.int32)

        zero_for_sound = [] #adding silence between echoes
        for i in range (time_between_echo):
            zero_for_sound.append (0)

        for i in range (number_of_echo):
            echo_data_fade_string = numpy.fromstring (echo_data_fade, numpy.int32)
            echo_data_fade_string = numpy.insert (echo_data_fade_string, 0, zero_for_sound)
            echo_data_string = numpy.append (echo_data_string, zero_for_sound)

            echo_data_string = (echo_data_string+echo_data_fade_string).astype(numpy.int32)
            echo_data_fade = echo_data_fade_string.tostring()
            echo_data_fade = audioop.mul(echo_data_fade, samplewidth, echo_repeats)
            echo_repeats = echo_repeats-1/number_of_echo

        data = echo_data_string.tostring()
        print ('Echo is done')
        return data

def pattern (): #getting pattern of sounds
    #setting the list of sounds to use in pattern
    obj = 0 #checker for finish of list of sounds to add in pattern
    names = [] #names of sounds
    while obj!='1':
        obj = input('Object name (1 to stop):')
        if obj!='1':
            names.append (obj)

    checker = '0' #checker for sound insertion
    between = [] #list of silence-spaces between sounds
    print ('1')
    time.sleep (0.5)
    print ('2')
    time.sleep (0.5)
    print ('3')
    time.sleep (0.5)
    print ('Start recording pattern (enter for sound, 1 for stopping)')

    while True:
        st = time.perf_counter() #start
        checker = input()
        fin = time.perf_counter() #finish
        between.append ((round(fin-st)*34))
        if checker=='1':
            break
    print ('Stop recording pattern')
    between.pop (0)
    
    wf = wave.open('Empty.wav', 'rb') #for spaces between sounds
    chunk = wf.getnframes()
    p = pyaudio.PyAudio()
    stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = wf.getframerate(),
                output = True)
    empty_data = wf.readframes(chunk)
    stream.close ()    
    p.terminate()

    pattern_name=input ('Name of pattern:') #name of file for saving the pattern
    pattern_file = wave.open(pattern_name+'.wav', 'wb')
    pattern_file.setnchannels(1)
    pattern_file.setsampwidth(p.get_sample_size(pyaudio.paInt16))
    pattern_file.setframerate(16000)

    choose = 0 #index for choosing sound from list of sounds for inserting
    for i in range(len(between)-1):
        if choose>(len(names)-1): #reset sound name index
            choose=0

        sound = wave.open(names[choose]+'.wav', 'rb')
        chunk=sound.getnframes()
        p = pyaudio.PyAudio()
        stream = p.open(format =
            p.get_format_from_width(sound.getsampwidth()),
            channels = sound.getnchannels(),
            rate = sound.getframerate(),
            output = True)
        data = sound.readframes(chunk)
        stream.close ()    
        p.terminate()

        pattern_file.writeframes(data)
        for l in range(between [i]):
            pattern_file.writeframes(empty_data)
        choose += 1

    if choose>(len(names)-1): #reset sound for final addition if needed
        choose=0

    sound = wave.open(names[choose]+'.wav', 'rb')
    chunk = sound.getnframes()
    p = pyaudio.PyAudio()
    stream = p.open(format =
        p.get_format_from_width(sound.getsampwidth()),
        channels = sound.getnchannels(),
        rate = sound.getframerate(),
        output = True)
    data = sound.readframes(chunk)

    pattern_file.writeframes(data)
    pattern_file.close()

    print ('Pattern is done')
    return pattern_name

###Microphone functions
def mic_record (name, to_save, to_play, use_echo):
    global stop_mic
    global mic_index
    p = pyaudio.PyAudio() #set audio recorder
    stream = p.open(format = pyaudio.paInt16,
        channels = 1,
        rate = 16000,
        frames_per_buffer = 1024,
        input_device_index = mic_index, 
        input=True)

    if to_play:
        p2 = pyaudio.PyAudio() #set audio player
        stream2 = p2.open(format= pyaudio.paInt16,
                        channels = 1,
                        rate = 16000,
                        frames_per_buffer = 1024,
                        output = True)

    frames_mic=[]
    if to_save:
        wf_mic = wave.open(name, 'wb')
        wf_mic.setnchannels(1)
        wf_mic.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf_mic.setframerate(16000)

    while stop_mic != 1:
        data_mic = stream.read(1024)
        frames_mic.append(data_mic)
        if to_play:
            stream2.write (data_mic)
            if use_echo:
                time.sleep (0.1)
                stream2.write (data_mic)
                time.sleep (0.1)
                stream2.write (data_mic)
        if to_save:
            wf_mic.writeframes(data_mic)

    stream.stop_stream()
    stream.close()
    p.terminate()
    if to_save:
        wf_mic.close()
    if to_play:
        stream2.stop_stream()
        stream2.close()
        p2.terminate()
    return True

def mic (): #launch mic for saving in parallel
    global stop_mic
    name_mic = input('Name of audio:')
    filename = name_mic+'.wav' 
    print('1')
    time.sleep (0.5)
    print('2')
    time.sleep (0.5)
    print('3')
    time.sleep (0.5)
    print('Start recording')
    mic_thread = threading.Thread(target = mic_record, args=(filename, True, False, False, )) #set new thread
    mic_thread.start()
    stop_mic = int(input ('Stop (1 to stop):'))
    print('Stop recording')
    return name_mic

###Main play function
def play (name_of_object, thread_name, form, type_form_sec_between, sec_between_repeats, counter_sec_start, counter_sec_step, counter_vol_start, counter_vol_step, waiting_bpm, volume, k, b, a, c, step, k_sec, b_sec, a_sec, c_sec, step_sec, time_between_echo, number_of_echo_main, type_function, edit_needed, speed, part):
    #name_of_object - name of the audiofile to play
    #thread_name - thread/track number (1-10)
    #form - type (in number) of formula of volume
    #type_form_sec_between - for formula of seconds between repeats
    #sec_between_repeats, counter_sec_start, counter_sec_step - amount of seconds between repeats and their 'timecode' and step
    #counter_vol_start, counter_vol_step - params for volume changing
    #waiting_bpm - to connect with bpm or not
    #volume - value for changing, or False no changing
    #k, b, a, c; k_sec, b_sec, a_sec, c_sec - values for formula
    #step, step_sec - steps
    #time_between_echo
    #number_of_echo_main
    #type_function - invers or echo
    #edit_needed - for edit
    #speed
    #part - part from start (of audiofile)
    global bpm_flag

    wf = wave.open(name_of_object+'.wav', 'rb') #open the audio sample/audio
    chunk = int((wf.getnframes()/part)) #duration
    p = pyaudio.PyAudio()
    stream = p.open(format =
                p.get_format_from_width(wf.getsampwidth()),
                channels = wf.getnchannels(),
                rate = int(wf.getframerate()/speed), #speed
                output = True)
    data = wf.readframes(chunk)

    if edit_needed==True: #for edit
        if type_function=='invers':
            data = edit (data, wf.getsampwidth(), number_of_echo_main, time_between_echo, type_function)
        if type_function=='echo':
            data=edit (data, wf.getsampwidth(), number_of_echo_main, time_between_echo, type_function)

    if not volume: #volume changing
        volume = 1
    else:
        data = audioop.mul(data, wf.getsampwidth(), volume) #volume

    while bpm_flag!='+': #wait for bpm moment
        time.sleep(0.025)
       
    for i in range (1, (number_of_repeats+1)): #amount of repeats
        if waiting_bpm == True: #to connect with bpm
            while bpm_flag!='+':
                time.sleep(0.025)

        if eval ('stopper'+thread_name+'==False'): #if current thread/track can be used
            if type_form_sec_between == 1: #for formula of seconds between repeats
                sec_between_repeats = k_sec*counter_sec_start+b_sec
                counter_sec_start = counter_sec_start+counter_sec_step
            if type_form_sec_between == 2:
                sec_between_repeats=a_sec*(counter_sec_start**2)+b_sec*counter_sec_start+c_sec
                counter_sec_start=counter_sec_start+counter_sec_step
            if type_form_sec_between == 3:
                x=counter_sec_start
                j=0
                while j!=(step_sec-1):
                    x=x*counter_sec_start
                    j=j+1
                sec_between_repeats=x
                counter_sec_start=counter_sec_start+counter_sec_step
            if type_form_sec_between == 4:
                sec_between_repeats=a_sec**counter_sec_start
                counter_sec_start=counter_sec_start+counter_sec_step
            if type_form_sec_between == 5:
                sec_between_repeats=counter_sec_start**(0.5)
                counter_sec_start=counter_sec_start+counter_sec_step

            if form == 1: #for formula of volume
                data=audioop.mul(data, wf.getsampwidth(), (k*counter_vol_start+b))
                counter_vol_start=counter_vol_start+counter_vol_step
                stream.write (data)
                time.sleep (abs(sec_between_repeats)) #time between repeats
                continue
            if form == 2:
                data=audioop.mul(data, wf.getsampwidth(), (a*(counter_vol_start**2)+b*counter_vol_start+c))
                counter_vol_start=counter_vol_start+counter_vol_step
                stream.write (data)
                time.sleep (abs(sec_between_repeats)) #time between repeats
                continue
            if form == 3:
                x=counter_vol_start
                j=0
                while j!=(step-1):
                    x=x*counter_vol_start
                    j=j+1
                data=audioop.mul(data, wf.getsampwidth(), (x))
                counter_vol_start=counter_vol_start+counter_vol_step
                stream.write (data)
                time.sleep (abs(sec_between_repeats)) #time between repeats
                continue
            if form == 4:
                data=audioop.mul(data, wf.getsampwidth(), (a**counter_vol_start))
                counter_vol_start=counter_vol_start+counter_vol_step
                stream.write (data)
                time.sleep (abs(sec_between_repeats)) #time between repeats
                continue
            if form == 5:
                data=audioop.mul(data, wf.getsampwidth(), (counter_vol_start**(0.5)))
                counter_vol_start=counter_vol_start+counter_vol_step
                stream.write (data)
                time.sleep (abs(sec_between_repeats)) #time between repeats
                continue
            else: #if no more changing needed - play
                stream.write (data)
                time.sleep (abs(sec_between_repeats)) #time between repeats
                continue
        else:
            stream.close ()    
            p.terminate()
            break
    stream.close ()    
    p.terminate()

###Stop function
def stop (self):
    return True

###Standard values to define
functions_map={'play':play,
               'stop':stop,
               'pattern':pattern}

#stoppers
stopper1=False
stopper2=False
stopper3=False
stopper4=False
stopper5=False
stopper6=False
stopper7=False
stopper8=False
stopper9=False
stopper10=False

#len of sounds in all tracks
current_sound_len1=[0]
current_sound_len2=[0]
current_sound_len3=[0]
current_sound_len4=[0]
current_sound_len5=[0]
current_sound_len6=[0]
current_sound_len7=[0]
current_sound_len8=[0]
current_sound_len9=[0]
current_sound_len10=[0]

#values for formula
k=0 
b=0
a=0 
c=0
step=0
k_sec=0
b_sec=0
a_sec=0
c_sec=0
step_sec=0

#echo params
time_between_echo=3000
number_of_echo_main=5

#exit flag
ex=0

#bpm flag
bpm_flag='-'

#bpm
bpm_checker=60


###
#Set mic
p = pyaudio.PyAudio()
for i in range(p.get_device_count()):
    print(i, p.get_device_info_by_index(i)['name']) #To show the number of mic
try:
    mic_index=int(input ('Mic index: '))
except ValueError:
    print ('Wrong input')

#Set BPM
try:
    bpm_checker=int(input ('BPM: '))
except ValueError:
    print ('Wrong input')
bpm_thread=threading.Thread(target=bpm, args=())
bpm_thread.start()


#Main cycle
while True:
    function_name=input ('Function name: ')
    stop_mic=1
    w_bpm=False
    #work with functions
    if function_name=='exit':
        ex=1
        break
    if function_name=='bpm':
        bpm_checker=int(input ('BPM:'))
        continue
    if function_name=='help':
        print ()
        print ('play - to play the sound (object name, thread number (1-10), part from start (of object), number of repeats, seconds between repeats (can be used with formula or be connected with BPM), volume (can be used with formula)) \n bpm - to change BPM \n mic - to record mic (online or offline (record without playing the mic), save or not, use echo or not) \n pattern - to record the pattern (can be chosen several sounds, use enter to put the sound, result can be used in play function or not) \n edit - to edit the sound (types of edit - (invers, speed, echo), result can be used in play function or not) \n stop - to stop chosen thread (before stopping the object name should be chosen, but it is not important for function) \n exit - to exit')
        print ()
        continue

    if function_name=='mic':
        online_or_offline=input('1) Online or 2) Offline: ')
        if online_or_offline=='1':
            save_or_not_sound=input('1) Save or 2) Not: ')
            if (save_or_not_sound != '1') or (save_or_not_sound != '2'):
                print ('Wrong input')
                continue
            if save_or_not_sound=='1':
                current_name=input('Name for object: ')
            use_echo=int(input('1) Echo (no echo in record) or 2) Not: '))
            print('1')
            time.sleep (0.5)
            print('2')
            time.sleep (0.5)
            print('3')
            time.sleep (0.5)
            print('Start recording')
            stop_mic=0
            if save_or_not_sound=='1':
                mic_thread_online_save=threading.Thread(target=mic_online_save, args=(current_name, use_echo, ))
                mic_thread_online_save.start()
                while stop_mic!=1:
                    stop_mic=int(input ('Stop (1 to stop):'))
                print ('Stop recording')
                continue
            if save_or_not_sound=='2':
                mic_thread_online=threading.Thread(target=mic_online, args=(use_echo, ))
                mic_thread_online.start()
                while stop_mic!=1:
                    stop_mic=int(input ('Stop (1 to stop):'))
                print ('Stop recording')
                continue
        if online_or_offline=='2':
            stop_mic=0
            object_name=mic()
            continue
        else:
            print ('Wrong input')
            continue

    using_pattern=0
    if function_name=='pattern':
        result_pattern=pattern ()
        using_pattern=input ('1)Use 2)Do not use: ') #use it in play or not
        if using_pattern=='1':
            object_name=result_pattern
            function_name='play'
        else:
            continue
    
    if using_pattern!='1':
        object_name=input ('Object name: ')

    #prepare values for edit and/or play
    edit_needed=False
    type_function='0'
    type_form=0
    type_form_sec_between=0
    counter_sec_step=0
    counter_sec_start=0
    counter_vol_step=0
    counter_vol_start=0
    speed=1
    number_of_echo_main=1
    online_or_offline=2

    #edit func
    if function_name=='edit':
        type_function=input('Type of edit: ')
        if type_function=='invers':
            save_or_not=input('1) Save or 2) Not:') #not to save - use in play function
            if save_or_not=='1':
                #open file
                wf_main = wave.open(object_name+'.wav', 'rb')
                chunk_main=int((wf_main.getnframes()))
                p_main= pyaudio.PyAudio()
                stream_main = p_main.open(format =
                    p_main.get_format_from_width(wf_main.getsampwidth()),
                    channels = wf_main.getnchannels(),
                    rate = wf_main.getframerate(),
                    output = True)
                data_main = wf_main.readframes(chunk_main)

                new_data=edit(data_main, 0, number_of_echo_main, time_between_echo, type_function)
                stream_main.close ()    
                p_main.terminate()

                #save
                new_name=input('New name: ')
                new_file = wave.open(new_name+'.wav', 'wb')
                new_file.setnchannels(1)
                new_file.setsampwidth(p_main.get_sample_size(pyaudio.paInt16))
                new_file.setframerate(16000)
                new_file.writeframes(new_data)
                new_file.close()
                continue
            if save_or_not!='1':
                edit_needed=True
                function_name='play'
        if type_function=='speed':
            save_or_not=input('1) Save or 2) Not:')
            if save_or_not=='1':
                speed=float(input('How much: '))
                #open file
                wf_main = wave.open(object_name+'.wav', 'rb')
                chunk_main=int((wf_main.getnframes()))
                p_main= pyaudio.PyAudio()
                stream_main = p_main.open(format =
                    p_main.get_format_from_width(wf_main.getsampwidth()),
                    channels = wf_main.getnchannels(),
                    rate = wf_main.getframerate(),
                    output = True)
                data_main = wf_main.readframes(chunk_main)

                #save with set speed
                new_name=input('New name:')
                new_file = wave.open(new_name+'.wav', 'wb')
                new_file.setnchannels(1)
                new_file.setsampwidth(p_main.get_sample_size(pyaudio.paInt32))
                new_file.setframerate(int(wf_main.getframerate()/speed))
                new_file.writeframes(data_main)
                new_file.close()
                stream_main.close()    
                p_main.terminate()
                continue
            if save_or_not!='1':
                edit_needed=True
                speed=float(input('How much: '))
                function_name='play'
        if type_function=='echo':
            save_or_not=input('1) Save or 2) Not:')
            if save_or_not=='1':
                number_of_echo_main=int(input('Number of echo: '))
                time_between_echo=int(input('Time between echo (starting with 3000): '))
                #open file
                wf_main = wave.open(object_name+'.wav', 'rb')
                chunk_main=int((wf_main.getnframes()))
                p_main= pyaudio.PyAudio()
                stream_main = p_main.open(format =
                    p_main.get_format_from_width(wf_main.getsampwidth()),
                    channels = wf_main.getnchannels(),
                    rate = wf_main.getframerate(),
                    output = True)
                data_main = wf_main.readframes(chunk_main)

                data_main=edit (data_main, wf_main.getsampwidth(), number_of_echo_main, time_between_echo, type_function)

                #save
                new_name=input('New name: ')
                new_file = wave.open(new_name+'.wav', 'wb')
                new_file.setnchannels(1)
                new_file.setsampwidth(p_main.get_sample_size(pyaudio.paInt32))
                new_file.setframerate(wf_main.getframerate())
                new_file.writeframes(data_main)
                new_file.close()
                stream_main.close()    
                p_main.terminate()
                continue
            if save_or_not!='1':
                edit_needed=True
                number_of_echo_main=int(input('Number of echo: '))
                time_between_echo=int(input('Time between echo (starting with 3000): '))
                function_name='play'

    #set thread-track
    thread_name=input ('Thread number: ')

    if function_name!='stop':
        #set some values
        try:
            part=int(input ('Part from start:')) #part of sound
        except ValueError:
            print ('Wrong input')
            continue
        try:
            number_of_repeats=int(input ('Number of repeats: '))
        except ValueError:
            print ('Wrong input')
            continue

        sec_between_repeats=input ('Seconds between repeats (f for formula, b for BPM): ')

        if sec_between_repeats!='f' and sec_between_repeats!='b':
            sec_between_repeats=int(sec_between_repeats)
        if sec_between_repeats=='f':
            try: #select type of formula
                type_form_sec_between=int(input (' 1) y = kx + b \n 2) y = ax^2 + bx + c \n 3) y = x^power \n 4) y = a^x \n 5) y=x^1/2 \n Number:'))
            except ValueError:
                print ('Wrong input')
                continue
            if type_form_sec_between==1:
                try:
                    k_sec=float(input ('k:'))
                except ValueError:
                    print ('Wrong input')
                    continue
                try:
                    b_sec=float(input ('b:'))
                except ValueError:
                    print ('Wrong input')
                    continue
            if type_form_sec_between==2:
                try:
                    a_sec=float(input ('a:'))
                except ValueError:
                    print ('Wrong input')
                    continue
                try:
                    b_sec=float(input ('b:'))
                except ValueError:
                    print ('Wrong input')
                    continue
                try:
                    c_sec=float(input ('c:'))
                except ValueError:
                    print ('Wrong input')
                    continue
            if type_form_sec_between==3:
                try:
                    step_sec=int(input ('Power: '))
                except ValueError:
                    print ('Wrong input')
                    continue
            if type_form_sec_between==4:
                try:
                    a_sec=float(input ('a: '))
                except ValueError:
                    print ('Wrong input')
                    continue
            try:
                counter_sec_start=float(input ('Start point: '))
            except ValueError:
                print ('Wrong input')
                continue
            try:
                counter_sec_step=float(input ('Step: '))
            except ValueError:
                print ('Wrong input')
                continue
        if sec_between_repeats=='f':
            sec_between_repeats=1
        if sec_between_repeats=='b':
            sec_between_repeats=0
            w_bpm=True

        volume=input ('Volume (f for formula): ')
        #Read file of sample
        try:
            current_sound = wave.open(object_name+'.wav', 'rb')
        except FileNotFoundError:
            print ('Wrong name of object')
            continue
        
        exec ('current_sound_len'+thread_name+'.insert(1, ((current_sound.getnframes()/(current_sound.getframerate()/speed))+sec_between_repeats))') #to find the time to wait to re-use the thread

        #Work with volume
        if volume!='f':
            try:
                volume=float(volume)
            except ValueError:
                print ('Wrong input')
                continue
        if volume=='f':
            try:
                type_form=int(input (' 1) y = kx + b \n 2) y = ax^2 + bx + c \n 3) y = x^power \n 4) y = a^x \n 5) y=x^1/2 \n Number: '))
            except ValueError:
                print ('Wrong input')
                continue
            if type_form==1:
                try:
                    k=float(input ('k:'))
                except ValueError:
                    print ('Wrong input')
                    continue
                try:
                    b=float(input ('b: '))
                except ValueError:
                    print ('Wrong input')
                    continue
            if type_form==2:
                try:
                    a=float(input ('a: '))
                except ValueError:
                    print ('Wrong input')
                    continue
                try:
                    b=float(input ('b: '))
                except ValueError:
                    print ('Wrong input')
                    continue
                try:
                    c=float(input ('c: '))
                except ValueError:
                    print ('Wrong input')
                    continue
            if type_form==3:
                try:
                    step=int(input ('Power: '))
                except ValueError:
                    print ('Wrong input')
                    continue
            if type_form==4:
                try:
                    a=float(input ('a:'))
                except:
                    print ('Wrong input')
                    continue
            try:
                counter_vol_start=float(input ('Start point: '))
            except ValueError:
                print ('Wrong input')
                continue
            try:
                counter_vol_step=float(input ('Step: '))
            except ValueError:
                print ('Wrong input')
                continue
            
    #Get function
    try:
        function=functions_map[function_name]
    except BaseException:
        print ('Wrong function')
        continue
    
    if function_name=='stop':
        exec('stopper'+thread_name+'=True')
        continue
    else: #Execute all thread operations
        exec('stopper'+thread_name+'=True')
        exec('time.sleep(current_sound_len'+thread_name+'[0])') #to re-use thread
        exec('stopper'+thread_name+'=False')
        exec('current_sound_len'+thread_name+'.pop (0)')
        thread=threading.Thread(target=function, args=(object_name, thread_name, type_form, type_form_sec_between, sec_between_repeats, counter_sec_start, counter_sec_step, counter_vol_start, counter_vol_step, w_bpm, volume, k, b, a, c, step, k_sec, b_sec, a_sec, c_sec, step_sec, time_between_echo, number_of_echo_main, type_function, edit_needed, speed, part))
        thread.start()
        print ('Thread '+thread_name+' works: sound: '+object_name+' , number of repeats: '+str(number_of_repeats)+' , sec. between repeats (1 can be formula, 0 can be BPM): '+str(sec_between_repeats)+' , volume: '+str(volume))
        print ()
        print ()
        print ()
        exec('stopper'+thread_name+'=False')

#Stop and exit
stopper1=True
stopper2=True
stopper3=True
stopper4=True
stopper5=True
stopper6=True
stopper7=True
stopper8=True
stopper9=True
stopper10=True
ex=1
stop_mic=1
bpm_thread.join()
print ('Exit is done')