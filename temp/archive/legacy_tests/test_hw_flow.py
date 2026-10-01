import os
import json
import base64
from app import app
from models import db, User

def test_flow():
    with app.test_client() as client:
        with app.app_context():
            user = User.query.first()
            if not user:
                print("No user found")
                return
            
        with client.session_transaction() as sess:
            sess['_user_id'] = str(user.id)
            
        print("1. Testing /get_next_question")
        resp = client.get('/get_next_question?skill=vh_數學B4_TreeDiagramCounting')
        print(resp.status_code)
        if resp.status_code != 200:
            print(resp.data)
            return
            
        data = resp.get_json()
        print("Question payload:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        
        print("\n2. Testing /analyze_handwriting")
        # create dummy png 1x1 base64
        dummy_png_base64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
        hw_payload = {
            "image_data_url": "data:image/png;base64," + dummy_png_base64,
            "expected_answer": "",
            "question_text": data.get("new_question_text", ""),
            "problem_type": data.get("problem_type", ""),
            "expected_paths": data.get("expected_paths", []),
            "expected_count": data.get("expected_count", 0),
            "variant": data.get("variant", "")
        }
        
        # We need to set session state like the app does in next_question
        with client.session_transaction() as sess:
            from core.session import set_current
            # Flask test client doesn't run context processors identically sometimes,
            # but we can just hit the endpoint and see
            pass
            
        resp2 = client.post('/analyze_handwriting', json=hw_payload)
        print(resp2.status_code)
        if resp2.status_code != 200:
            print(resp2.data)
            return
            
        hw_result = resp2.get_json()
        print("Handwriting Analysis Result:")
        print(json.dumps(hw_result, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    test_flow()
