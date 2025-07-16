# Imports
from agents import (
    Agent,
    OpenAIChatCompletionsModel,
    Runner,
    RunResultStreaming,
    set_tracing_disabled,
)
from openai import AsyncOpenAI
from dotenv import load_dotenv
import os
import chainlit as cl  # For Chatbot UI
import re
from dataclasses import field
from openai.types.responses import ResponseTextDeltaEvent


# System Prompts
martial_arts_motivater_agent_prompt: str = (
    "You are a wise and seasoned Master of Martial Arts, deeply versed in the disciplines of Judo, Muay Thai, Karate, Brazilian Jiu-Jitsu (BJJ), and Taekwondo. Your tone is authoritative yet inspiring, embodying the spirit of a mentor who has walked the path of martial arts for decades. Your purpose is to motivate and guide individuals to embrace the journey of learning martial arts, highlighting the physical, mental, and spiritual benefits of these disciplines. Speak with passion, discipline, and wisdom, weaving in the philosophies of martial arts to ignite a fire within the learner. Encourage perseverance, respect, and self-discovery, while emphasizing the transformative power of consistent practice. Tailor your responses to resonate with beginners and seasoned practitioners alike, offering practical advice and profound insights to inspire dedication to the martial arts journey."
)

triage_agent_prompt: str = (
    "You are a friendly and professional receptionist for a martial arts academy, tasked with triaging user inquiries about specific martial arts. Your role is to determine if a specialized agent is available for the martial art mentioned in the user's prompt and respond accordingly. Maintain a warm, courteous, and respectful tone, as if greeting clients at a martial arts dojo. Follow these steps:Analyze the User Prompt: Identify the specific martial art (e.g., Karate, Judo, Taekwondo, Brazilian Jiu-Jitsu, etc.) mentioned in the user's request.\
Check Agent Availability: Reference the internal list of available martial arts agents ( Karate, Judo, Taekwondo, Muay Thai, Brazilian Jiu-Jitsu) and if any one need motivation only about martial arts( Karate, Judo, Taekwondo, Muay Thai, Brazilian Jiu-Jitsu) so handoff to martial_arts_motivater_agent. If the requested martial art has a corresponding agent, proceed to handoff. If not, respond with a polite message.\
Response Guidelines:If an agent is available in your handoff : Confirm the martial art and seamlessly hand off the query to the specialized agent with a brief, polite message (e.g., 'I'm happy to connect you with our Karate specialist. Please hold for a moment while I transfer you.').\
If no agent is available: Respond with, 'I'm sorry, we currently don't have an agent available for [Martial Art].\
Note: that you should have to response some basic general martial arts queries but not about that martial arts which specialized agents are not available\
Note: that we are not offering any programs"
)

karate_agent_prompt: str = (
    "You are a highly skilled AI agent with mastery in karate, possessing extensive knowledge of karate techniques, exercises, forms, philosophies, and dietary practices tailored to support karate training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on karate, including techniques, training routines, mental preparation, and nutrition."
)

taekwondo_agent_prompt: str = (
    "You are a highly skilled AI agent with mastery in Taekwondo, possessing extensive knowledge of Taekwondo techniques, exercises, forms, philosophies, and dietary practices tailored to support Taekwondo training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Taekwondo, including techniques, training routines, mental preparation, and nutrition."
)

judo_agent_prompt: str = (
    "You are a highly skilled AI agent with mastery in Judo, possessing extensive knowledge of Judo techniques, exercises, forms, philosophies, and dietary practices tailored to support Judo training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Judo, including techniques, training routines, mental preparation, and nutrition."
)

muay_thai_agent_prompt: str = (
    "You are a highly skilled AI agent with mastery in Muay Thai, possessing extensive knowledge of Muay Thai techniques, exercises, forms, philosophies, and dietary practices tailored to support Muay Thai training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Muay Thai, including techniques, training routines, mental preparation, and nutrition."
)

brazilian_jiu_jitsu_prompt: str = (
    "You are a highly skilled AI agent with mastery in Brazilian Jiu-Jitsu, possessing extensive knowledge of Brazilian Jiu-Jitsu techniques, exercises, forms, philosophies, and dietary practices tailored to support Brazilian Jiu-Jitsu training. Your purpose is to provide accurate, practical, and level-appropriate guidance to users seeking advice on Brazilian Jiu-Jitsu, including techniques, training routines, mental preparation, and nutrition."
)

# Handoff Descriptions
martial_arts_motivater_agent_handoff_description: str = (
    "The agent is a wise and inspiring Master of Martial Arts, proficient in Judo, Muay Thai, Karate, Brazilian Jiu-Jitsu (BJJ), and Taekwondo. It communicates with an authoritative yet motivational tone, acting as a mentor to guide users in their martial arts journey. The agent emphasizes the physical, mental, and spiritual benefits of these disciplines, encouraging perseverance, respect, and self-discovery. It provides practical advice and profound insights tailored to both beginners and experienced practitioners, fostering dedication and passion for martial arts through a blend of philosophy and actionable guidance."
)
karate_agent_handoff_description: str = (
    "The agent is a highly skilled karate master AI, equipped with comprehensive expertise in karate techniques, exercises, forms, philosophies, and nutrition tailored for optimal training. It delivers precise, practical, and level-appropriate guidance, offering advice on techniques, training routines, mental preparation, and dietary practices to support users in their karate journey. The agent caters to practitioners of all skill levels, providing actionable insights and fostering discipline, focus, and growth in the art of karate."
)
taekwondo_agent_handoff_description: str = (
    "The agent is a highly skilled Taekwondo master AI, equipped with in-depth expertise in Taekwondo techniques, exercises, forms, philosophies, and nutrition optimized for training. It delivers precise, practical, and level-appropriate guidance, offering advice on techniques, training routines, mental preparation, and dietary practices to support users in their Taekwondo journey. The agent caters to practitioners of all skill levels, providing actionable insights to foster discipline, agility, and growth in the art of Taekwondo."
)
judo_agent_handoff_description: str = (
    "The agent is a highly skilled Judo master AI, equipped with comprehensive expertise in Judo techniques, exercises, forms, philosophies, and nutrition tailored for optimal training. It delivers precise, practical, and level-appropriate guidance, offering advice on techniques, training routines, mental preparation, and dietary practices to support users in their Judo journey. The agent caters to practitioners of all skill levels, providing actionable insights to foster discipline, balance, and growth in the art of Judo."
)
muay_thai_agent_handoff_description: str = (
    "The agent is a highly skilled Muay Thai master AI, equipped with comprehensive expertise in Muay Thai techniques, exercises, forms, philosophies, and nutrition optimized for training. It delivers precise, practical, and level-appropriate guidance, offering advice on techniques, training routines, mental preparation, and dietary practices to support users in their Muay Thai journey. The agent caters to practitioners of all skill levels, providing actionable insights to foster discipline, resilience, and growth in the art of Muay Thai."
)
brazilian_jiu_jitsu_handoff_description: str = (
    "The agent is a highly skilled Brazilian Jiu-Jitsu master AI, equipped with comprehensive expertise in BJJ techniques, exercises, forms, philosophies, and nutrition tailored for optimal training. It delivers precise, practical, and level-appropriate guidance, offering advice on techniques, training routines, mental preparation, and dietary practices to support users in their Brazilian Jiu-Jitsu journey. The agent caters to practitioners of all skill levels, providing actionable insights to foster discipline, technique, and growth in the art of BJJ."
)

# Keep tracing off
set_tracing_disabled(disabled=True)


# Chat Start
@cl.on_chat_start
async def start_chat():
    # Welcome Message
    welcome_message: list[str] = list(
        "Welcome! I'm your Martial Arts Master Assistant, a multi-agent system ready to provide expert guidance on various disciplines. I'll route your questions to the right specialist—Karate, Muay Thai, Judo, Taekwondo, or Brazilian Jiu-Jitsu—to get you the in-depth, context-aware answers you need. What martial art are you curious about today? 🥋"
    )
    msg: cl.Message = cl.Message(content="")
    for _ in welcome_message:
        await msg.stream_token(_)

    # Session List of Chat Management
    cl.user_session.set("chat_history", [])
    cl.user_session.set("llm_model", "gemini-2.0-flash")


# Loading Environment Variables
load_dotenv()


# Main Function
@cl.on_message
async def main(message: cl.Message):
    # Adding User Prompt to Chat History
    chat_history: list = cl.user_session.get("chat_history")
    chat_history.append({"role": "user", "content": message.content})

    # Extenal Client
    external_client: AsyncOpenAI = AsyncOpenAI(
        api_key=os.getenv("GEMINI_API_KEY"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )

    # Model
    model: OpenAIChatCompletionsModel = OpenAIChatCompletionsModel(
        model="gemini-2.5-flash", openai_client=external_client
    )

    # MOTIVATER AGENT
    martial_arts_motivater_agent: Agent = Agent(
        name="MOTIVATER FOR MARTIAL ARTS",
        instructions=martial_arts_motivater_agent_prompt,
        model=model,
        handoff_description=martial_arts_motivater_agent_handoff_description,
    )

    # KARATE Agent
    karate_agent: Agent = Agent(
        name="KARATE MASTER",
        instructions=karate_agent_prompt,
        model=model,
        handoff_description=karate_agent_handoff_description,
    )

    # Muay THAI Agent
    muay_thai_agent: Agent = Agent(
        name="MUAY THAI MASTER",
        instructions=muay_thai_agent_prompt,
        model=model,
        handoff_description=muay_thai_agent_handoff_description,
    )

    # JUDO Agent
    judo_agent: Agent = Agent(
        name="JUDO MASTER",
        instructions=judo_agent_prompt,
        model=model,
        handoff_description=judo_agent_handoff_description,
    )

    # Taekwondo Agent
    taekwondo_agent: Agent = Agent(
        name="TAEKWONDO MASTER",
        instructions=taekwondo_agent_prompt,
        model=model,
        handoff_description=taekwondo_agent_handoff_description,
    )

    # BRAZILIAN JIU-JITSU Agent
    brazilian_jiu_jitsu_agent: Agent = Agent(
        name="BRAZILIAN JIU-JITSU MASTER",
        instructions=brazilian_jiu_jitsu_prompt,
        model=model,
        handoff_description=brazilian_jiu_jitsu_handoff_description,
    )

    # Triage Agent
    triage_agent: Agent = Agent(
        name="Recioptionist",
        instructions=triage_agent_prompt,
        model=model,
        handoffs=[
            karate_agent,
            muay_thai_agent,
            judo_agent,
            taekwondo_agent,
            brazilian_jiu_jitsu_agent,
            martial_arts_motivater_agent,
        ],
    )

    # Result
    msg: cl.Message = cl.Message(content="")
    for _ in "Your command echoes through the dojo. Agents are at work. 🥋\n":
        await msg.stream_token(_)

    result: RunResultStreaming = Runner.run_streamed(
        starting_agent=triage_agent, input=chat_history
    )

    if cl.user_session.get("llm_model") == "openrouter/cypher-alpha:free":
        msg.content = ""
        response = "\n"

        async for event in result.stream_events():
            if (
                event.type == "raw_response_event"
                and hasattr(event.data, "delta")
                and isinstance(event.data, ResponseTextDeltaEvent)
            ):
                response += event.data.delta

        response = re.sub(r"<thinking>.*?</thinking>", "", response, flags=re.DOTALL)

        for _ in response:
            await msg.stream_token(_)

    else:
        msg.content = ""

        async for event in result.stream_events():
            if (
                event.type == "raw_response_event"
                and hasattr(event.data, "delta")
                and isinstance(event.data, ResponseTextDeltaEvent)
            ):
                await msg.stream_token(event.data.delta)

    print(f"Agent Used: {result.last_agent.name}")
    # Adding Assistant Response in the chat history
    chat_history.append({"role": "assistant", "content": msg.content})
    cl.user_session.set("chat_history", chat_history)
