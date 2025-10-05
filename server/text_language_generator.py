from openai import OpenAI
from collections import deque
import time

from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=os.getenv('OPENROUTER_API_KEY'),
)

# generator = pipeline(task='text-generation', model="meta-llama/Llama-3.2-3B-Instruct")

def generator(prompt, max_new_tokens=50):
    response = client.chat.completions.create(
      model="meta-llama/Llama-3.2-3B-Instruct",
      messages = [
        {
          "role": "user",
          "content": prompt
        }
      ],
      max_tokens=max_new_tokens,
      temperature=0.7,
    )

    return response.choices[0].message.content

def generate_text(gloss_input, last_text=''):
    instruct = 'You are a gloss-to-English converter. Output only the sentence using only the gloss token. No need to complete it with additional words. No explanations.'
    prompt = f'{instruct}\nGloss: {gloss_input}\nSentence:'

    max_tokens = len(gloss_input.split()) + len(prompt.split())

    output = generator(prompt, max_new_tokens=max_tokens)

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

def generate_continue_text(gloss_buffer, text_buffer, text=''):
  # gloss prediction simulation from given text
  for gloss_input in text.split():
    time.sleep(0.5)

    gloss_input = gloss_input.split('_')[0]
    gloss_buffer.append_gloss(gloss_input)

    if random.random() < CONF_THRESHOLD:
      continue

    gloss_text = gloss_buffer.get_gloss_text()

    if gloss_text != '':
      text_list = list(text_buffer)
      gen_text = generate_text(gloss_text, ' '.join(text_list))
      text_buffer.extend(gen_text.split())
      print(gen_text)

def create_text_buffer(max_size=50):
    return deque(maxlen=max_size)

if __name__ == "__main__":
    text = "HELLO HOW YOU/YOUR FEEL TODAY I/ME THINK FUTURE CAREER PLAN YOU/YOUR LIKE/LOVE BOOK_READ OR MOVIE/FILM"
    gloss_buffer = GlossBuffer()
    text_buffer = create_text_buffer()

    generate_continue_text(gloss_buffer, text_buffer, text)