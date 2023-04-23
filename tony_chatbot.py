
from tensorflow import keras
import nltk
import pickle
import json
import numpy as np
from keras.models import Sequential
from keras.layers import Dense,Dropout,Activation
import random
import datetime
import webbrowser
import requests
import billboard
import time
from pygame import mixer
import COVID19Py
import pyjokes
import random
import wikipedia
from textblob import TextBlob
import speech_recognition as sr
import pyttsx3
import pywhatkit 
import pyautogui
import sys
import os


engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def speak_va(transcribed_query):
    engine.say(transcribed_query)
    engine.runAndWait()

from nltk.stem import WordNetLemmatizer
lemmatizer=WordNetLemmatizer()

words=[]
classes=[]
documents=[]
ignore=['?','!',',',"'s"]

data_file=open('intents.json').read()
intents=json.loads(data_file)

for intent in intents['intents']:
    for pattern in intent['patterns']:
        w=nltk.word_tokenize(pattern)
        words.extend(w)
        documents.append((w,intent['tag']))
        
        if intent['tag'] not in classes:
            classes.append(intent['tag'])
            
words=[lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore]
words=sorted(list(set(words)))
classes=sorted(list(set(classes)))
pickle.dump(words,open('words.pkl','wb'))
pickle.dump(classes,open('classes.pkl','wb'))

#training data
training=[]
output_empty=[0]*len(classes)

for doc in documents:
    bag=[]
    pattern=doc[0]
    pattern=[ lemmatizer.lemmatize(word.lower()) for word in pattern ]
    
    for word in words:
        if word in pattern:
            bag.append(1)
        else:
            bag.append(0)
    output_row=list(output_empty)
    output_row[classes.index(doc[1])]=1
    
    training.append([bag,output_row])
    
random.shuffle(training)
training=np.array(training)  
X_train=list(training[:,0])
y_train=list(training[:,1])  

#Model
model=Sequential()
model.add(Dense(128,activation='relu',input_shape=(len(X_train[0]),)))
model.add(Dropout(0.5))
model.add(Dense(64,activation='relu'))
model.add(Dense(64,activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(y_train[0]),activation='softmax'))

adam=keras.optimizers.Adam(0.001)
model.compile(optimizer=adam,loss='categorical_crossentropy',metrics=['accuracy'])
#model.fit(np.array(X_train),np.array(y_train),epochs=200,batch_size=10,verbose=1)
weights=model.fit(np.array(X_train),np.array(y_train),epochs=200,batch_size=10,verbose=1)    
model.save('mymodel.h5',weights)

from keras.models import load_model
model = load_model('mymodel.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
classes = pickle.load(open('classes.pkl','rb'))


#Predict
def clean_up(sentence):
    sentence_words=nltk.word_tokenize(sentence)
    sentence_words=[ lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words

def create_bow(sentence,words):
    sentence_words=clean_up(sentence)
    bag=list(np.zeros(len(words)))
    
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
    return np.array(bag)

def predict_class(sentence,model):
    p=create_bow(sentence,words)
    res=model.predict(np.array([p]))[0]
    threshold=0.8
    results=[[i,r] for i,r in enumerate(res) if r>threshold]
    results.sort(key=lambda x: x[1],reverse=True)
    return_list=[]
    
    for result in results:
        return_list.append({'intent':classes[result[0]],'prob':str(result[1])})
    return return_list

def get_response(return_list,intents_json):
    
    if len(return_list)==0:
        tag='noanswer'
    else:    
        tag=return_list[0]['intent']
    if tag=='datetime':        
        print(time.strftime("%A"))
        speak_va(time.strftime("%A"))
        print (time.strftime("%d %B %Y"))
        speak_va (time.strftime("%d %B %Y"))
        print (time.strftime("%H:%M:%S"))
        speak_va (time.strftime("%H:%M:%S"))

    if tag=='wiki':
        query=input('Enter query...')
        result=wikipedia.summary(query,sentences=2)
        print(result)
        speak_va(result)

    if tag=='weather':
        api_key='987f44e8c16780be8c85e25a409ed07b'
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        print("Enter city name : ")
        city_name = input()
        complete_url = base_url + "appid=" + api_key + "&q=" + city_name
        response = requests.get(complete_url) 
        x=response.json()
        print('Present temp.: ',round(x['main']['temp']-273,2),'celcius ')
        print('Feels Like:: ',round(x['main']['feels_like']-273,2),'celcius ')
        print(x['weather'][0]['main'])
        speak_va(x['weather'][0]['main'])
        
    if tag=='news':
        main_url = " http://newsapi.org/v2/top-headlines?country=in&apiKey=bc88c2e1ddd440d1be2cb0788d027ae2"
        open_news_page = requests.get(main_url).json()
        article = open_news_page["articles"]
        results = [] 
          
        for ar in article: 
            results.append([ar["title"],ar["url"]]) 
          
        for i in range(10): 
            print(i + 1, results[i][0])
            print(results[i][1],'\n')
    
    if tag=='song':
        chart=billboard.ChartData('hot-100')
        print('The top 10 songs at the moment are:')
        for i in range(10):
            song=chart[i]
            print(song.title,'- ',song.artist)

    if tag=='options':
        print(" I am a general purpose chatbot. My capabilities are\n 1. I can chat with you. Try asking me for jokes or riddles! \n ")
        print("2. Ask me the date and time \n 3. I can wikipedia search for you. Use format wiki: your query \n") 
        print("4. I can get the present weather for any city. Use format weather: city name \n") 
        print("5. I can get you the top 10 trending news in India. Use keywords 'Latest News' \n 6. I can get you the top 10 trending songs globally. Type 'songs' \n ")
        print("7. I can set a timer for you. Enter 'set a timer: minutes to timer' \n8. I can get the present Covid stats for any country. Use 'covid 19: world' or 'covid 19: country name' \n") 
        print("9.“create note” to make a note\n 10. “add a new todo” to add a item to todo list\n 11.	It can wikipedia search for you. Use format wiki: your query\n") 
        print("12.	Ask “tell me a joke” it will read out a joke\n 13.	Tell “take screenshot” it will take a screenshot and save it in same place wherethe code is saved\n") 
        print("14.	Say “play justin beiber” it'll play justin beiber songs in youtube\n 15.If you wanna search say “search elephants” it'll search elephants in  google of your default browser\n ")
        print("16.	If you say other than these it'll search for what you say in google and shows it in command prompt itself\n 17.	Say “open instagram” to open insta or any website “open site_name”\n ")
        print("18.	Say “what is programming wikipedia”  to search in Wikipedia \nFor suggestions to help me improve, send an email to BotHut@iiitk.ac.in . Thank you!!  ")

    if tag=='goodbye':
        bye=random.choice(exit_resp)
        print(bye)
        speak_va(bye)
        sys.exit(0)
       
        
    list_of_intents= intents_json['intents']    
    for i in list_of_intents:
        if tag==i['tag'] :
            result= random.choice(i['responses'])
    return result

def response(text):
    return_list=predict_class(text,model)
    return get_response(return_list,intents)

note=["new note", "create an note","Take a note","writedown a note","make a note","create a note"]
todo=["add a new todo", "add a new todo to my list","add todo","add to do","add a todo","add a to do","new todo","new to do"]
show_todos=["show my todo","what are my todo","show todo","show to do","show todo list","show to do list"]
todo_list = ['Go Shopping', 'Clean Room']
timer=["timer","set a timer","set the timer","timer please","set an timer"]
exit_resp=["See you!","Have a nice day","Bye! Come back again soon.","Sad to see you go :(", "Talk to you later", "Goodbye!"]
covid=["covid 19","covid19","covid","Covid","COVID","Covid 19","Covid19"]
user=["what is my name","Do you know me","My name","Who am I"]

def create_note():
  recognizer = sr.Recognizer()
  speak_va("What do you want to write as note?")
  done = False
  while not done:
        try:
            with sr.Microphone() as source:
                
                recognizer.pause_threshold = 0.7
                voice = recognizer.listen(source)

                note = recognizer.recognize_google(voice).lower()


                speak_va("Choose a file name")
                

                recognizer.pause_threshold = 0.7
                voice = recognizer.listen(source)

                filename = recognizer.recognize_google(voice).lower()

            with open(filename, 'w') as f:
                f.write(note)
                done = True
                speak_va(f"created the note")
                
        except sr.UnknownValueError:
                recognizer=sr.Recognizer()
                speak_va("I did not get it")
                

def add_todo():
    recognizer = sr.Recognizer()
    speak_va("What do you want add")
    done = False

    while not done:
        try:

            with sr.Microphone() as source:
                recognizer.pause_threshold = 0.7
                voice = recognizer.listen(source)

                item = recognizer.recognize_google(voice).lower()

                todo_list.append(item)
                done = True

                speak_va(item+" was added to the list!")
                 

        except sr.UnknownValueError:
            speak_va("I'm sorry, can you repeat it again!")
             
def show_todos():

    speak_va("list is")
    for item in todo_list:
        print(item+"\n")
        speak_va(item)

def Timer():
    mixer.init()
    x=input('Minutes to timer..')
    time.sleep(float(x)*60)
    mixer.music.load('WWEBell.mp3')
    mixer.music.play()

def COVID():
    covid19=COVID19Py.COVID19(data_source='jhu')
    country=input('Enter Location(country name)...')
    C=TextBlob(country).correct()
    if(country != C):
        print("Do you mean: "+str(C))
        country=str(C)
    
    if country.lower()=='world':
        latest_world=covid19.getLatest()
        print('Confirmed:',latest_world['confirmed'],' Deaths:',latest_world['deaths'])
    
    else:
            
        latest=covid19.getLocations()
        
        latest_conf=[]
        latest_deaths=[]
        for i in range(len(latest)):
            
            if latest[i]['country'].lower()== country.lower():
                latest_conf.append(latest[i]['latest']['confirmed'])
                latest_deaths.append(latest[i]['latest']['deaths'])
        latest_conf=np.array(latest_conf)
        latest_deaths=np.array(latest_deaths)
        print('Confirmed: ',np.sum(latest_conf),'Deaths: ',np.sum(latest_deaths))

f=0
while(True):
    if f==0:
        f=1
        print("Tony here may I know your name please")
        speak_va("Tony here may I know your name please")
        name=input()
        print("Hi "+ name.lower())
        speak_va("Hi "+ name.lower())
    else:
        x=input()
    
        if x.lower() in ['mic','microphone']:
            recognizer = sr.Recognizer()
            with sr.Microphone() as source:
                print('Mic is on....')
                recognizer.pause_threshold = 0.7
                voice = recognizer.listen(source)
                try:
                    query = recognizer.recognize_google(voice).lower()
                    print('this is the query that was made....', query)
                
                except Exception as ex:
                    print('An exception occurred', ex)
            x=query
        
        
        if 'open' in x: 
            x = x.replace('open', '')
            x = x.replace(' ', '')
            print('https://www.'+x+'.com/')
            webbrowser.open('https://www.'+x+'.com/')
            speak_va(f"{x} opened.")
        elif 'wikipedia' in x:
            speak_va("Searching on Wikipedia")
            x = x.replace('wikipedia', ' ')
            result = wikipedia.summary(x, sentences=2)
            print(result)
            speak_va(result)
        elif 'joke' in x:
            random_joke = pyjokes.get_joke()
            print(random_joke)
            speak_va(random_joke)
        elif 'screenshot' in x:
            image = pyautogui.screenshot()
            y='screenshot'
            image.save('screenshot.png')
            speak_va('Screenshot taken.')
        elif 'search' in x:
            x = x.replace('search', ' ')
            search_url = f"https://www.google.com/search?q={x}"
            webbrowser.open(search_url)
            speak_va(f"here are the results for the search term: {x}")
        elif x in note:
            create_note()
        elif x in todo:
            add_todo()
        elif x in timer:
            Timer()
        elif x in user:
            print("You are {name} right")
        elif "play" in x:
            x = x.replace('play', ' ')
            pywhatkit.playonyt(x)
        elif x in covid:
            COVID()
        else:
            X=TextBlob(x).correct()
            if(x != X):
                print("Do you mean: "+str(X))
                x=str(X)
            
            y=response(x)
            if(y!="noanswer"):
                print(y)    
                speak_va(y)       
            else:
                pywhatkit.info(x,lines=2)
                print("here are the results for the search term: {x}")

