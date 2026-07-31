import os
import sys
import argparse
import json
import anthropic

# Default System Instructions to enforce strict anti-fabrication
SYSTEM_PROMPT = """
You are an expert recruitment consultant and career agent. Your task is to customize a candidate's master resume to fit a target job description.

CRITICAL INSTRUCTION FOR TRUTHFULNESS:
1. You MUST NEVER fabricate, exaggerate, or invent any experience, metrics, skills, projects, or job titles.
2. You can ONLY highlight, rephrase, and prioritize existing facts already listed in the candidate's master resume.
3. If a key skill is required in the job description but NOT present in the master resume, do NOT add it. Keep it missing.
4. All adjusted metrics (percentages, values) must exactly match the ones present in the master resume.
5. If the resume is tailored, output the result in clean Markdown format matching the section layouts.
"""

def load_text_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        sys.exit(1)

def tailor_resume(api_key, master_resume_path, job_desc_path, output_path):
    print("Loading source documents...")
    master_resume = load_text_file(master_resume_path)
    job_description = load_text_file(job_desc_path)
    
    print("Initializing Anthropic client...")
    client = anthropic.Anthropic(api_key=api_key)
    
    prompt = f"""
Here is my Master Resume:
<master_resume>
{master_resume}
</master_resume>

Here is the Target Job Description:
<job_description>
{job_description}
</job_description>

Please customize my resume by highlighting my most relevant operations, data, and AI experiences that align with the job description. Follow the strict anti-fabrication rules provided in the system prompt.
"""
    
    print("Calling Claude API (claude-3-5-sonnet)...")
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet",
            max_tokens=2000,
            temperature=0.2, # Low temperature to ensure factual consistency
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        
        tailored_content = message.content[0].text
        
        # Save output
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tailored_content)
        print(f"Successfully saved tailored resume to: {output_path}")
        
    except Exception as e:
        print(f"API Error or file write error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Job-Search & Resume-Tailoring Agent")
    parser.add_argument("--resume", required=True, help="Path to Master Resume file (TXT/MD)")
    parser.add_argument("--job", required=True, help="Path to Target Job Description file (TXT)")
    parser.add_argument("--output", default="Tailored_Resume.md", help="Path to save tailored resume")
    
    args = parser.parse_args()
    
    # Retrieve Anthropic API Key
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is not set.")
        print("Please set it using: export ANTHROPIC_API_KEY='your_key'")
        sys.exit(1)
        
    tailor_resume(api_key, args.resume, args.job, args.output)
