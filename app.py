import os
from flask import Flask, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import openai
import json


app = Flask(__name__)
openai.api_key = os.environ.get('OPENAI_API_KEY')
# SQLAlchemy setup
Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    user_input = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    output = Column(String, nullable=False)

engine = create_engine('sqlite:///tasks.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@app.route('/create_task', methods=['POST'])
def create_task():
    data = request.get_json()
    user_input = data.get('user_input')
    print(user_input)
    # Make a request to OpenAI API
    openai_response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "For the user input, generate output in the following format: {\"output\": \"\""},
            {"role": "user", "content": user_input}
        ],
    )["choices"][0]["message"]["content"]
    print(openai_response)
    loaded_response = json.loads(openai_response)
    user_id=1
    print("!", loaded_response)
    # Save task to database
    session = Session()
    new_task = Task(user_input=user_input, user_id=user_id, **loaded_response)
    session.add(new_task)
    session.commit()
    session.close()

    return jsonify({"message": "Task created successfully!"})

@app.route('/get_tasks', methods=['GET'])
def get_tasks():
    session = Session()
    tasks = session.query(Task).all()
    session.close()

    task_list = [{'id': task.id, 'user_input': task.user_input, 'openai_response': json.loads(task.openai_response)} for task in tasks]

    return jsonify(task_list)

if __name__ == '__main__':
    app.run(debug=True)
