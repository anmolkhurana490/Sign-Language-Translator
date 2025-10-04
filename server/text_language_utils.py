from transformers import pipeline

# from huggingface_hub import login
# login(os.getenv("hf_token"))

# generator = pipeline(task='text-generation', model="meta-llama/Llama-3.2-3B-Instruct")
generator = pipeline(task='text-generation', model="saved_models/meta-llama")

def generate_text(gloss_input, last_text=''):
    instruct = 'You are a gloss-to-English converter. Output only the sentence using only the gloss token. No need to complete it with additional words. No explanations.'
    prompt = f'{instruct}\nGloss: {gloss_input}\nSentence:'

    max_tokens = len(gloss_input.split()) + len(prompt.split())

    output = generator(prompt, max_new_tokens=max_tokens, pad_token_id=generator.tokenizer.eos_token_id)[0]['generated_text']

    if prompt in output:
        output = output.replace(prompt, '').strip()
    if '(' in output:
        output = output.split('(')[0].strip()
    else:
        output = output.strip()

    output = output.replace('_', ' ').strip()
    return output.split('\n')[0]

input_texts = """HELLO HOW YOU/YOUR FEEL TODAY
I/ME THINK FUTURE CAREER PLAN
YOU/YOUR LIKE/LOVE BOOK_READ OR MOVIE/FILM
FRIEND/COMPANION INVITE PARTY WEEKEND
I/ME/MINE/MY WANT/NEED TRAVEL VISIT NEW CITY
YESTERDAY RAIN WEATHER BAD STILL I/ME/MINE/MY GO SCHOOL
TOMORROW I/ME PLAN STUDY EXAM PREPARE
FAMILY SUPPORT/HELP ME DECISION CAREER
YOU/YOUR CAN PLAY GAME SPORTS WITH FRIEND/COMPANION
TIME NOW GO SLEEP BECAUSE TOMORROW EARLY WAKE"""

for sentence in input_texts.split('\n')[:3]:
    print(sentence + ' -> ' + generate_text(sentence))