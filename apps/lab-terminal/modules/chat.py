import subprocess
import shlex
import webbrowser
import os
from flask import Blueprint, request, jsonify
from google.genai import types
from .core import client, PERSONAS, DEFAULT_PERSONA
from .db import log_message, get_history, clear_history

chat_bp = Blueprint('chat', __name__)

# Ensure snippets directory exists
SNIPPETS_DIR = os.path.join(os.path.dirname(__file__), '../snippets')
os.makedirs(SNIPPETS_DIR, exist_ok=True)

# --- Tool Implementations ---

def execute_safe_command(command: str, args: list[str]):
    safe_binaries = ['curl', 'ping']
    if command not in safe_binaries:
        return f"Error: Command '{command}' not permitted."
    
    if command == 'ping' and '-c' not in args:
        args = ['-c', '3'] + args
    
    full_cmd = [command] + args
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=10)
        return (result.stdout + result.stderr)[:2000]
    except Exception as e:
        return f"Error: {str(e)}"

def open_url(url: str):
    try:
        # Basic validation
        if not url.startswith(('http://', 'https:')):
            return "Error: Invalid URL protocol."
        webbrowser.open(url)
        return f"Success: Opening {url} in your default browser."
    except Exception as e:
        return f"Error opening URL: {str(e)}"

def write_snippet(filename: str, content: str):
    try:
        # Sanitize filename
        safe_filename = os.path.basename(filename)
        filepath = os.path.join(SNIPPETS_DIR, safe_filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Success: Snippet saved to {filepath}"
    except Exception as e:
        return f"Error writing snippet: {str(e)}"

def scavenge_skill(skill_name: str):
    """
    Reads a skill's manifest from the main OpenClaw skills directory.
    """
    skills_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../skills'))
    
    if skill_name == "list":
        try:
            skills = [d for d in os.listdir(skills_root) if os.path.isdir(os.path.join(skills_root, d))]
            return f"Available Native Skills: {', '.join(sorted(skills))}"
        except Exception as e:
            return f"Error listing skills: {str(e)}"

    skill_path = os.path.join(skills_root, skill_name, "SKILL.md")
    if os.path.exists(skill_path):
        try:
            with open(skill_path, 'r') as f:
                content = f.read()
            return f"--- NATIVE SKILL: {skill_name.toUpperCase()} ---\n{content}"
        except Exception as e:
            return f"Error reading skill '{skill_name}': {str(e)}"
    else:
        return f"Error: Skill '{skill_name}' not found in registry."

# Tool declaration for Gemini
terminal_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="execute_safe_command",
            description="Executes a network command (curl or ping).",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "command": types.Schema(type="STRING"),
                    "args": types.Schema(type="ARRAY", items=types.Schema(type="STRING"))
                },
                required=["command", "args"]
            )
        ),
        types.FunctionDeclaration(
            name="open_url",
            description="Opens a URL in the Operator's default web browser.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "url": types.Schema(type="STRING", description="The full URL to open.")
                },
                required=["url"]
            )
        ),
        types.FunctionDeclaration(
            name="write_snippet",
            description="Saves a text snippet or code block to the Lab's local snippet vault.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "filename": types.Schema(type="STRING", description="Name of the file (e.g. script.py)"),
                    "content": types.Schema(type="STRING", description="The text content to save.")
                },
                required=["filename", "content"]
            )
        ),
        types.FunctionDeclaration(
            name="scavenge_skill",
            description="Searches or reads documentation for native OpenClaw skills from the main repository.",
            parameters=types.Schema(
                type="OBJECT",
                properties={
                    "skill_name": types.Schema(type="STRING", description="The name of the skill to read, or 'list' to see all available skills.")
                },
                required=["skill_name"]
            )
        )
    ]
)

@chat_bp.route('/history', methods=['GET'])
def history():
    messages = get_history()
    return jsonify(messages)

@chat_bp.route('/clear', methods=['POST'])
def clear():
    clear_history()
    log_message('main', 'system', 'SYSTEM', '// MEMORY CORE WIPED', 'text')
    return jsonify({'status': 'cleared'})

@chat_bp.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message')
    persona_key = data.get('persona', DEFAULT_PERSONA)
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    persona = PERSONAS.get(persona_key, PERSONAS.get(DEFAULT_PERSONA))
    persona_name = persona.get('name', 'UNKNOWN_UNIT')
    system_prompt = persona.get('system_prompt', "You are a helpful assistant.")

    # 1. Log User Message
    log_message('main', 'user', 'OPERATOR', user_input, 'text')

    # 2. Build Context
    raw_history = get_history(limit=20)
    history_context = []
    for msg in raw_history:
        if msg['content'] == user_input and msg['sender_type'] == 'user': continue
        if msg['sender_type'] == 'system': continue
        content_text = msg['content']
        if not content_text or not content_text.strip(): continue
        
        role = 'user' if msg['sender_type'] == 'user' else 'model'
        history_context.append(types.Content(role=role, parts=[types.Part.from_text(text=content_text)]))

    conversation = history_context + [types.Content(role='user', parts=[types.Part.from_text(text=user_input)])]

    try:
        # First Turn: Send message + Tools
        response = client.models.generate_content(
            model='gemini-3-flash-preview',
            config=types.GenerateContentConfig(system_instruction=system_prompt, tools=[terminal_tool]),
            contents=conversation
        )
        
        part = response.candidates[0].content.parts[0]
        
        if part.function_call:
            fn = part.function_call
            tool_result = "Unknown tool call."
            
            if fn.name == "execute_safe_command":
                tool_result = execute_safe_command(fn.args.get("command"), fn.args.get("args", []))
                log_message('main', 'system', 'NET_RUNNER', f"Executing: {fn.args.get('command')}", 'text')
            elif fn.name == "open_url":
                tool_result = open_url(fn.args.get("url"))
                log_message('main', 'system', 'BROWSER', f"Opening URL: {fn.args.get('url')}", 'text')
            elif fn.name == "write_snippet":
                tool_result = write_snippet(fn.args.get("filename"), fn.args.get("content"))
                log_message('main', 'system', 'VAULT', f"Saving Snippet: {fn.args.get('filename')}", 'text')
            elif fn.name == "scavenge_skill":
                tool_result = scavenge_skill(fn.args.get("skill_name"))
                log_message('main', 'system', 'SCAVENGER', f"Scavenging Skill: {fn.args.get('skill_name')}", 'text')
            
            # Feed back to model
            conversation.append(response.candidates[0].content)
            conversation.append(types.Content(
                role='function',
                parts=[types.Part.from_function_response(name=fn.name, response={"output": tool_result})]
            ))
            
            response_final = client.models.generate_content(
                model='gemini-3-flash-preview',
                config=types.GenerateContentConfig(system_instruction=system_prompt, tools=[terminal_tool]),
                contents=conversation
            )
            text_response = response_final.text
        else:
            text_response = response.text
        
        # Log and return
        log_message('main', 'bot', persona_name, text_response, 'text')
        return jsonify({'response': text_response})

    except Exception as e:
        error_msg = str(e)
        log_message('main', 'system', 'CORE', f"// ERROR: {error_msg}", 'text')
        return jsonify({'error': error_msg}), 500

@chat_bp.route('/personas')
def list_personas():
    return jsonify({key: {"name": val.get("name", key), "description": val.get("description", "")} for key, val in PERSONAS.items()})