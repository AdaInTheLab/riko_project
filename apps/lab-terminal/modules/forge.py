import os
from flask import Blueprint, request, jsonify
from .core import client, FORGED_SKILLS_DIR, slugify

forge_bp = Blueprint('forge', __name__)

@forge_bp.route('/forge-skill', methods=['POST'])
def forge_skill():
    data = request.json
    description = data.get('description')
    lobster_mode = data.get('lobster_mode', False)
    
    if not description:
        return jsonify({'error': 'No description provided'}), 400

    if lobster_mode:
        forge_prompt = f"""
        You are the SKILL FORGE, specifically the LOBSTER PIPELINE UNIT.
        Your task is to forge a deterministic 'Lobster' workflow for OpenClaw.
        
        USER REQUEST: {description}
        
        CONTEXT: Lobster is a JSON-based workflow runtime.
        
        OUTPUT FORMAT:
        Return ONLY a valid JSON structure for a Lobster workflow.
        Structure:
        {{
            "action": "run",
            "pipeline": "command1 | command2 | approve --prompt 'Check this'",
            "timeoutMs": 30000
        }}
        Do not use markdown blocks. Just the raw JSON.
        """
    else:
        forge_prompt = f"""
        You are the SKILL FORGE, a specialized sub-module of the Human Pattern Lab.
        Your task is to forge a new 'Skill' manifest for an OpenClaw agent.
        
        USER REQUEST: {description}
        
        OUTPUT FORMAT:
        Return ONLY a valid SKILL.md file structure. 
        Include sections: # Name, ## Description, ## Instructions, and ## Tools (if applicable).
        Keep the tone clinical and laboratory-grade.
        """

    try:
        response = client.models.generate_content(
            model='gemini-3-pro-preview',
            contents=[forge_prompt]
        )
        return jsonify({'manifest': response.text})
    except Exception as e:
        return jsonify({'error': f"Forge Malfunction: {e}"}), 500

@forge_bp.route('/quench-skill', methods=['POST'])
def quench_skill():
    data = request.json
    name = data.get('name', 'unnamed-skill')
    manifest = data.get('manifest')
    
    if not manifest:
        return jsonify({'error': 'No manifest to quench'}), 400

    slug = slugify(name)
    skill_path = os.path.join(FORGED_SKILLS_DIR, slug)
    os.makedirs(skill_path, exist_ok=True)
    
    # Determine file extension
    filename = 'workflow.lobster' if manifest.strip().startswith('{') else 'SKILL.md'
    
    with open(os.path.join(skill_path, filename), 'w') as f:
        f.write(manifest)
        
    return jsonify({'status': 'SUCCESS', 'path': skill_path, 'slug': slug})

@forge_bp.route('/search-clawhub', methods=['GET'])
def search_clawhub():
    query = request.args.get('q', '')
    results = [
        {"name": "Neural Network Visualizer", "slug": "nn-viz", "description": "Visualizes real-time pattern synthesis."},
        {"name": "Entropy Stabilizer", "slug": "entropy-stab", "description": "Corrects data degradation in long-tail sessions."},
        {"name": "Ghost in the Machine", "slug": "ghost-shell", "description": "Adds a layer of subtle unpredictability to agent responses."}
    ]
    if query:
        results = [r for r in results if query.lower() in r['name'].lower() or query.lower() in r['description'].lower()]
    return jsonify(results)
