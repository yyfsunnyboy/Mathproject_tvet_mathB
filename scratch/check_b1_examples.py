import sys
import os

# Ensure we can import app and models
sys.path.append(os.getcwd())

from app import app
from models import db, TextbookExample

def check_examples():
    with app.app_context():
        print("| example_id | problem_text_snippet | skill_id | source_type | chapter | section | issue |")
        print("|---|---|---|---|---|---|---|")
        
        # Query B1 examples
        examples = TextbookExample.query.filter(
            (TextbookExample.skill_id.like('vh_mathB1_%')) | 
            (TextbookExample.skill_id.like('vh_數學B1_%'))
        ).all()
        
        for ex in examples:
            issue = ""
            if ex.skill_id.startswith('vh_mathB1_'):
                issue = "Old prefix"
            
            # Use problem_text snippet
            snippet = str(ex.problem_text)[:30].replace("\n", " ") + "..."
            
            # Map columns to output (assuming column names based on model snippet)
            print(f"| {ex.id} | {snippet} | {ex.skill_id} | {ex.source_curriculum} | {ex.source_chapter} | {ex.source_section} | {issue} |")

if __name__ == "__main__":
    check_examples()
