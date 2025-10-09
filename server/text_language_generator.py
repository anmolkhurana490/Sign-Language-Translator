from google import genai
from collections import deque
import time

from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client()

# generator = pipeline(task='text-generation', model="meta-llama/Llama-3.2-3B-Instruct")

def generator(prompt, max_new_tokens=50):
    try:
      response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
      )
      return response.text
    
    except Exception as e:
      print(f"Error in text generation: {e}")
      return ""

def generate_text(gloss_input, last_text=''):
    instruct = 'You are a gloss-to-English converter. Output only the sentence using only given gloss tokens. No need to complete it with additional words. No explanations.'
    prompt = f'{instruct}\nGloss: {gloss_input}\nSentence:'

    max_tokens = len(gloss_input.split()) + len(prompt.split())

    start = time.time()
    output = generator(prompt, max_new_tokens=max_tokens)
    # output = gloss_input
    
    end = time.time()
    print(f"Time taken for generation: {end - start} seconds")

    if prompt in output:
        output = output.replace(prompt, '').strip()
    if '(' in output:
        output = output.split('(')[0].strip()
    else:
        output = output.strip()

    output = output.replace('_', ' ').strip()
    return output.split('\n')[0]

WINDOW_SIZE = 8
MIN_TRIGGER = 4
MAX_CONSUME = 6
SILENCE_TIMEOUT = 3
CONF_THRESHOLD = 0.7

# Buffer Manager Class
class GlossBuffer:
  def __init__(self):
    self.buffer = deque(maxlen=WINDOW_SIZE)
    self.last_gloss_time = 0

  def append_gloss(self, gloss):
    curr_time = time.time()
    self.update_buffer(curr_time)

    if gloss not in self.get_buffer():
      self.buffer.append((gloss, curr_time))

    self.last_gloss_time = curr_time

  def update_buffer(self, curr_time):
    curr_time = time.time()
    if curr_time - self.last_gloss_time > SILENCE_TIMEOUT:
      self.buffer.clear()

    while len(self.buffer) > 0 and self.buffer[0][1] < curr_time - SILENCE_TIMEOUT:
      self.buffer.popleft()

  def get_buffer(self):
    return [t for t,c in self.buffer]

  def get_gloss_text(self):
    gloss_list = self.get_buffer()

    if len(gloss_list) < MIN_TRIGGER:
      return ''

    # removing older glosses
    if len(gloss_list) > MAX_CONSUME:
      gloss_list = gloss_list[:MAX_CONSUME]

    return ' '.join(gloss_list)
  

import random

def generate_continue_text(gloss_buffer, text_buffer):
  gloss_text = gloss_buffer.get_gloss_text()

  if gloss_text != '':
    text_list = list(text_buffer)
    gen_text = generate_text(gloss_text, ' '.join(text_list))

    if gen_text and gen_text.strip() != '':
      text_buffer.extend(gen_text.split())
      return gen_text
    
  return ''

def create_text_buffer(max_size=50):
    return deque(maxlen=max_size)

if __name__ == "__main__":
    text = "HELLO HOW YOU/YOUR FEEL TODAY I/ME THINK FUTURE CAREER PLAN YOU/YOUR LIKE/LOVE BOOK_READ OR MOVIE/FILM"
    gloss_buffer = GlossBuffer()

    text_buffer = create_text_buffer()

    for word in text.split():
      gloss_buffer.append_gloss(word)
      generate_continue_text(gloss_buffer, text_buffer)