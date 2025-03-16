import os
from config import settings


css = '''
<style>
.chat-msg {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-msg.user {
    background-color: #2b313e
}
.chat-msg.bot {
    background-color: #475063
}
.chat-msg .avatar {
  width: 20%;
}
.chat-msg .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-msg .msg {
  width: 100%;
  padding: 0 1.5rem;
  color: #fff;
}
'''
def get_bot_template(message, type):
    bot_template = f'''
    <div class="chat-msg bot">
        <div class="avatar">
            <img src="{type+".png"}" alt="bot" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
        </div>
        <div class="msg">{message}</div>
    </div>
    '''
    return bot_template

def get_user_template(message, type):
    user_template = f'''
    <div class="chat-msg user">
        <div class="avatar">
            <img src="{type+".png"}" alt="user" /></a>
        </div>    
        <div class="msg">{message}</div>
    </div>
    '''
    return user_template

def get_audio_template(base64_audio):
    return f'''
    <audio src="data:audio/mp3;base64,{base64_audio}" autoplay>
        Your browser does not support the audio element.
    </audio>
    <style>
        audio {{
            display: none;
        }}
    </style>
    '''

def get_form_template():
    return f'''
    <form action="/submit" method="post">
        <label for="name">Name:</label><br>
        <input type="text" id="name" name="name" required><br><br>

        <label for="company">Company:</label><br>
        <input type="text" id="company" name="company" required><br><br>

        <label for="forecasting">Estimated Forecasting (in dollars):</label><br>
        <input type="number" id="forecasting" name="forecasting" step="0.01" required><br><br>

        <input type="submit" value="Submit">
    </form>
    '''