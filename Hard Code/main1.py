import json
from sentence_transformers import SentenceTransformer, util
import os

def load_knowledge_base(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {"questions": []}
    with open(file_path,'r') as file:
        data: dict = json.load(file)
    return data

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path,'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str], model) -> str | None:
    # Encode the user question and knowledge base questions into embeddings
    question_embeddings = model.encode(questions)
    user_embedding = model.encode(user_question)
    
    # Compute cosine similarity between user input and stored questions
    similarities = util.pytorch_cos_sim(user_embedding, question_embeddings)
    
    # Find the question with the highest similarity score
    best_match_index = similarities.argmax().item()
    best_match_score = similarities[0][best_match_index].item()

    # Return the best match if similarity is above a certain threshold (0.6)
    if best_match_score >= 0.6:
        return questions[best_match_index]
    return None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

def chat_bot():
    # Load knowledge base
    knowledge_base: dict = load_knowledge_base('knowledge_base.json')
    
    # Initialize sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')  # A small, fast model

    while True:
        user_inp = input('You: ')
        if user_inp.lower() == 'bye':
            print(f'Bot: Have a nice day <3')
            break
        
        # Get a list of all questions in the knowledge base
        question_texts = [q["question"] for q in knowledge_base["questions"]]
        
        # Find the best match using sentence embeddings
        best_match: str | None = find_best_match(user_inp, question_texts, model)
        
        if best_match:
            # If a match is found, return the corresponding answer
            answer: str = get_answer_for_question(best_match, knowledge_base)
            print(f'Bot: {answer}')
        else:
            # If no match is found, prompt the user to teach the bot
            print('Bot: I don\'t know the answer. Can you teach me?')
            new_ans: str = input('Type the answer or "skip" to skip: ')
            
            if new_ans.lower() != 'skip':
                # Add the new question-answer pair to the knowledge base
                knowledge_base["questions"].append({"question": user_inp, "answer": new_ans})
                save_knowledge_base('knowledge_base.json', knowledge_base)
                print('Bot: Thank you! I learned a new response')

if __name__ == '__main__':
    chat_bot()
