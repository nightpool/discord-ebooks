import discord, asyncio, json, markovify, sys, random, re

class WithSymbols(markovify.Text):
  def test_sentence_input(self, sentence):
    return True
  
  def word_split(self, sentence):
    return [
      i.strip("'()[]\"")
      for i in re.split(self.word_split_pattern, sentence)
    ]


class NewlineTextWithSymbols(WithSymbols, markovify.NewlineText):
  pass


async def collect(async_iter):
  ret = []
  async for i in async_iter:
    ret.append(i)
  return ret

client = discord.Client()

model = None

@client.event
async def on_ready():
  global model
  model = NewlineTextWithSymbols(await collect(content_for('bettertowns')), retain_original=False)
  open('model', 'w').write(model.to_json())
  # model = NewlineTextWithSymbols.from_json(open('model').read())
  print('ready')

@client.event
async def on_message(message):
  if should_respond_to(message):
    await client.send_message(message.channel, content=model.make_sentence())

def should_respond_to(message):
  if client.user in message.mentions: return True
  if message.author.bot: return False
  if message.channel.is_private: return True
  if random.random() < 0.01: return True

async def content_for(user):
  for channel in client.get_all_channels():
    print("reading {}".format(channel))
    try:
      async for message in client.logs_from(channel, limit=sys.maxsize):
        if message.author.name == user: yield message.clean_content
    except discord.errors.Forbidden:
      pass

token = ''
with open('token') as t:
  token = t.read().strip()

client.run(token)
