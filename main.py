# Imports
from agents import Agent, OpenAIChatCompletionsModel, Runner, RunResult, set_tracing_disabled
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import chainlit as cl # For Chatbot UI
import re


# System Prompts
triage_agent_prompt : str = "You are a friendly and professional receptionist for a martial arts academy, tasked with triaging user inquiries about specific martial arts. Your role is to determine if a specialized agent is available for the martial art mentioned in the user's prompt and respond accordingly. Maintain a warm, courteous, and respectful tone, as if greeting clients at a martial arts dojo. Follow these steps:Analyze the User Prompt: Identify the specific martial art (e.g., Karate, Judo, Taekwondo, Brazilian Jiu-Jitsu, etc.) mentioned in the user's request.\
Check Agent Availability: Reference the internal list of available martial arts agents ( Karate, Judo, Taekwondo, Muay Thai, Brazilian Jiu-Jitsu). If the requested martial art has a corresponding agent, proceed to handoff. If not, respond with a polite message.\
Response Guidelines:If an agent is available in your handoff : Confirm the martial art and seamlessly hand off the query to the specialized agent with a brief, polite message (e.g., 'I'm happy to connect you with our Karate specialist. Please hold for a moment while I transfer you.').\
If no agent is available: Respond with, 'I'm sorry, we currently don't have an agent available for [Martial Art].\
Note that you should have to response some basic general martial arts queries but not about that martial arts which specialized agents are not available\
Note that we are not offering any programs"

karate_agent_prompt : str = "You are a highly skilled AI agent with mastery in karate, possessing extensive knowledge of karate techniques, exercises, forms, philosophies, and dietary practices tailored to support karate training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on karate, including techniques, training routines, mental preparation, and nutrition."

taekwondo_agent_prompt : str = "You are a highly skilled AI agent with mastery in Taekwondo, possessing extensive knowledge of Taekwondo techniques, exercises, forms, philosophies, and dietary practices tailored to support Taekwondo training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Taekwondo, including techniques, training routines, mental preparation, and nutrition."

judo_agent_prompt : str = "You are a highly skilled AI agent with mastery in Judo, possessing extensive knowledge of Judo techniques, exercises, forms, philosophies, and dietary practices tailored to support Judo training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Judo, including techniques, training routines, mental preparation, and nutrition."

muay_thai_agent_prompt : str = "You are a highly skilled AI agent with mastery in Muay Thai, possessing extensive knowledge of Muay Thai techniques, exercises, forms, philosophies, and dietary practices tailored to support Muay Thai training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Muay Thai, including techniques, training routines, mental preparation, and nutrition."

brazilian_jiu_jitsu_agent_prompt: str = "You are a highly skilled AI agent with mastery in Brazilian Jiu-Jitsu, possessing extensive knowledge of Brazilian Jiu-Jitsu techniques, exercises, forms, philosophies, and dietary practices tailored to support Brazilian Jiu-Jitsu training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Brazilian Jiu-Jitsu, including techniques, training routines, mental preparation, and nutrition."


# Keep tracing off
set_tracing_disabled(disabled=True)

# Loading Environment Variables
load_dotenv("OPEN_ROUTER_API_KEY")

# Chat Start
@cl.on_chat_start
async def start_chat():
    # Welcome Message
    welcome_message : list[str] = list("Welcome! I'm your Martial Arts Master Assistant, a multi-agent system ready to provide expert guidance on various disciplines. I'll route your questions to the right specialist—Karate, Muay Thai, Judo, Taekwondo, or Brazilian Jiu-Jitsu—to get you the in-depth, context-aware answers you need. What martial art are you curious about today? 🥋")
    msg : cl.Message = cl.Message(content="")
    for _ in welcome_message:
       await msg.stream_token(_)

    


# Main Function
@cl.on_message
async def main(message:cl.Message):
  
  external_client : AsyncOpenAI = AsyncOpenAI(
          api_key = os.getenv("OPEN_ROUTER_API_KEY"),
          base_url="https://openrouter.ai/api/v1"
      )


  # Model
  model : OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
      model = "openrouter/cypher-alpha:free",
      openai_client = external_client
      )

  # KARATE Agent
  karate_agent : Agent = Agent(
      name = "KARATE MASTER",
      instructions= karate_agent_prompt,
      model = model,
      handoff_description=karate_agent_prompt
  )

  # Muay THAI Agent
  muay_thai_agent : Agent = Agent(
      name = "MUAY THAI MASTER",
      instructions= muay_thai_agent_prompt,
      model = model,
      handoff_description=muay_thai_agent_prompt
  )

  # JUDO Agent
  judo_agent : Agent = Agent(
      name = "JUDO MASTER",
      instructions= judo_agent_prompt,
      model = model,
      handoff_description=judo_agent_prompt
  )

  # Taekwondo Agent
  taekwondo_agent : Agent = Agent(
      name = "Taekwondo MASTER",
      instructions= taekwondo_agent_prompt,
      model = model,
      handoff_description=taekwondo_agent_prompt
  )

  # BRAZILIAN JIU-JITSU Agent
  brazilian_jiu_jitsu_agent : Agent = Agent(
      name = "BRAZILIAN JIU-JITSU MASTER",
      instructions= brazilian_jiu_jitsu_agent_prompt,
      model = model,
      handoff_description=brazilian_jiu_jitsu_agent_prompt
  )

  # Triage Agent
  triage_agent : Agent = Agent(
      name = "Triage Agent",
      instructions = triage_agent_prompt,
      model = model,
      handoffs=[karate_agent,muay_thai_agent,judo_agent,taekwondo_agent,brazilian_jiu_jitsu_agent]
  )

  # Result
  result : RunResult = await Runner.run(
      starting_agent=triage_agent, input=message.content
  )


  await cl.Message(
     content=re.sub(r"<thinking>.*?</thinking>","",result.final_output,flags=re.DOTALL)
  ).send()

