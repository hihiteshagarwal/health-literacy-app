# 1. Imports and Setup
import ssl
import getpass
import os
import json
import random
import requests
import io
import wave
import numpy as np
from scipy.io import wavfile
import sounddevice as sd
from typing import List, Dict, Union
from dotenv import load_dotenv
from openai import OpenAI
from llama_index.legacy import SimpleDirectoryReader, StorageContext, ServiceContext
from llama_index.legacy.indices.vector_store import VectorStoreIndex
from llama_iris import IRISVectorStore

# 2. SSL Configuration
def configure_ssl():
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

# 3. Environment Setup
def setup_environment():
    load_dotenv(override=True)
    if not os.environ.get("OPENAI_API_KEY"):
        os.environ["OPENAI_API_KEY"] = getpass.getpass("OpenAI API Key:")

# 4. IRIS Database Connection
def setup_iris_connection():
    username = 'demo'
    password = 'demo' 
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = '1972' 
    namespace = 'USER'
    return f"iris://{username}:{password}@{hostname}:{port}/{namespace}"

# 5. Vector Store Setup
def setup_vector_store(connection_string):
    return IRISVectorStore.from_params(
        connection_string=connection_string,
        table_name="health",
        embed_dim=1536
    )

# 6. Document Processing
def process_documents():
    documents = SimpleDirectoryReader("./data/health").load_data()
    return documents

# 7. Course Generation
def generate_course(query_engine, condition, subtopic, description=''):
    course_prompt = "Create a structured course based on "+condition+" related to "+subtopic+" with description "+description+". Ensure that each section is well-structured, with clear objectives and content outline. Use a consistent format for each section and provide details that can be used to design a course that is educational, engaging, and comprehensive. The output should include the following details in the specified order in a JSON format: Course Title, Section Titles with Objectives and Content Outline, and Conclusion. \'Section Titles with Objectives and Content Outline\' should be a list of dictionaries with keys Section Title, Objectives, and Content Outline"
    response = query_engine.query(course_prompt)
    return json.loads(response.response)

def json_to_text(section):
    return "Section title is "+section['Section Title'] + \
    " where the objectives are: "+", ".join(section['Objectives']) + \
    " and the content outline is: "+", ".join(section['Content Outline']) + \
    " in the mentioned order."

def get_prompt(topic):
    return({
        "gen_exp": "Create a concise and engaging script for a general healthcare explainer video where "+topic+". The script should use simple language, engaging visuals, and real-life analogies to make the concept easy to understand. Use Singapore-specific statistics, healthcare policies, or lifestyle examples where relevant. Break the script into clear sections: introduction, explanation, examples, and conclusion. Ensure the tone is educational yet engaging, and the duration should be around 8-10 minutes. Return the output in a well-structured, machine-readable JSON format where each subsection has a title and text.",
        "avatar_exp": "Write a script for an avatar-based explainer video where "+topic+". The tone should be friendly and conversational, as if a virtual doctor or AI assistant in Singapore is explaining the topic to a patient. Use short, clear sentences, and include natural pauses for emphasis. Add subtle engagement elements like rhetorical questions or quick check-ins (e.g., ‘Did you know that…?’). Include culturally relevant examples, such as local diet and lifestyle habits. Keep it within a 2-minute duration. Return the output in a well-structured, machine-readable JSON format.",
        "two_person_podcast": "Generate a fully scripted 5-minute two-person podcast discussion where "+topic+". One speaker should be a Singapore-based healthcare expert (Doctor/Researcher from MOH, NUH, or a local clinic), and the other should be a curious host or patient asking relatable questions. The script must include exact, word-for-word dialogues for both speakers, formatted clearly with their names before each line. The conversation should feel natural, engaging, and informative, with occasional humor or relatable examples. Include a mix of explanations, myth-busting, and practical takeaways. Where relevant, refer to Singapore’s healthcare policies, lifestyle habits, or common health concerns. Ensure smooth transitions between topics and a clear conclusion that summarizes key points. Return the output in a well-structured, machine-readable JSON format.",
        "two_person_podcast2": "Generate a fully scripted 5-minute two-person podcast discussion where "+topic+". One speaker should be a Singapore-based healthcare expert (Doctor/Researcher from MOH, NUH, or a local clinic), and the other should be a curious host or patient asking relatable questions. The script must include exact, word-for-word dialogues for both speakers, formatted clearly with their names before each line. The conversation should feel natural, engaging, and informative, with occasional humor or relatable examples. Include a mix of explanations, myth-busting, and practical takeaways. Where relevant, refer to Singapore’s healthcare policies, lifestyle habits, or common health concerns. Ensure smooth transitions between topics and a clear conclusion that summarizes key points. Return the output in a well-structured, machine-readable JSON format.",
        "blog_article": "Write a 600-800 word blog article where "+topic+". Start with a compelling introduction that highlights why this topic is important for people in Singapore. Structure the article with subheadings for clarity. Use a mix of scientific explanations, real-life examples, and actionable takeaways. Include Singapore-specific data, policies, or trends where relevant. Maintain an engaging and informative tone, ensuring accessibility for a general audience. Return the output in a well-structured, machine-readable JSON format.",
    })

def get_quiz_prompt(topic):
    return "Create a 5-question interactive quiz where "+topic+". Each question should test understanding in an engaging way, with multiple-choice options. Provide immediate, informative feedback for each answer, whether correct or incorrect, to educate users as they progress. Where possible, include localized examples (e.g., common health misconceptions in Singapore, government initiatives like the Healthier SG programme). Ensure the questions vary in difficulty and reinforce key takeaways about the topic. Return the output in a well-structured, machine-readable JSON format."

# 8. Content Generation
def generate_content(sections, query_engine):
    content = []
    for sec in sections:
        topic = json_to_text(sec)
        prompts = get_prompt(topic)
        content_type = random.choice(list(prompts.keys()))
        response = query_engine.query(prompts[content_type])
        quiz_response = query_engine.query(get_quiz_prompt(topic))
        try:
            content.append({
                "topic": sec['Section Title'],
                "content": json.loads(response.response),
                "quiz": json.loads(quiz_response.response)
            })
        except:
            content.append({
                "topic": sec['Section Title'],
                "content": response.response,
                "quiz": json.loads(quiz_response.response)
            })
    return content

# 9. Translation Functions
from openai import OpenAI
from typing import List, Dict, Union

def translate_to_chinese(text: str, client: OpenAI) -> str:
    """Translate a single text string to Chinese"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a translator. Translate the following text to Chinese."},
                {"role": "user", "content": str(text)}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error translating '{text}': {str(e)}")
        return text

def translate_nested_structure(data: Union[Dict, List, str], client: OpenAI) -> Union[Dict, List, str]:
    """
    Recursively translate all string values in a nested structure to Chinese
    """
    if isinstance(data, dict):
        return {k: translate_nested_structure(v, client) for k, v in data.items()}
    elif isinstance(data, list):
        return [translate_nested_structure(item, client) for item in data]
    elif isinstance(data, str):
        return translate_to_chinese(data, client)
    else:
        return data

def translate_content(content_list: List[Dict]) -> List[Dict]:
    """
    Translate the entire content structure to Chinese
    """
    client = OpenAI()
    translated_content = translate_nested_structure(content_list, client)
    return translated_content

# 10. Audio Processing
def process_audio(text, voice_id, api_key):
    url = "https://waves-api.smallest.ai/api/v1/lightning-large/get_speech"
    payload = {
        "add_wav_header": True,
        "sample_rate": 24000,
        "speed": 1,
        "language": "en",
        "consistency": 0.5,
        "similarity": 0,
        "enhancement": 1,
        "voice_id": voice_id,
        "text": text
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    return requests.request("POST", url, json=payload, headers=headers)

def process_wav_response(response):
    """
    Process WAV file from API response
    Args:
        response: requests response containing WAV file data
    Returns:
        audio_data: numpy array of audio samples
        sample_rate: sampling rate of audio
    """
    # Method 1: Using scipy
    try:
        # Create BytesIO object from response content
        wav_bytes = io.BytesIO(response.content)
        sample_rate, audio_data = wavfile.read(wav_bytes)
        return audio_data, sample_rate
    except Exception as e:
        print(f"Error with scipy method: {e}")
        
        # Method 2: Fallback to wave module
        try:
            wav_bytes = io.BytesIO(response.content)
            with wave.open(wav_bytes, 'rb') as wav_file:
                frames = wav_file.readframes(wav_file.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                sample_rate = wav_file.getframerate()
                return audio_data, sample_rate
        except Exception as e:
            print(f"Error with wave method: {e}")
            return None, None

def save_wav_file(audio_data, sample_rate, filename="output.wav"):
    """Save audio data to WAV file"""
    wavfile.write(filename, sample_rate, audio_data)

# 11. Main Execution
def main():
    # Initialize
    configure_ssl()
    setup_environment()
    
    # Setup connections
    connection_string = setup_iris_connection()
    vector_store = setup_vector_store(connection_string)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    # Process documents
    documents = process_documents()
    
    # Create index
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context, 
        show_progress=True
    )
    
    # Setup query engine
    query_engine = index.as_query_engine()
    
    # Generate course content
    # Add your specific implementation here
    
    # Process translations
    # Add your specific implementation here
    
    # Generate audio
    # Add your specific implementation here

if __name__ == "__main__":
    main()
