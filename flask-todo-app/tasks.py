from flask import Flask, render_template, request, redirect, url_for
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

# ✅ Correct region (don’t include availability zone letter)
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
tasks_table = dynamodb.Table('todo_tasks')

@app.route('/')
def home():
    try:
        response = tasks_table.scan()
        tasks = response.get('Items', [])
        return render_template('index.html', tasks=tasks)
    except ClientError as e:
        print(f"AWS Error: {e.response['Error']['Message']}")
        return f"<h3>Unable to connect to DynamoDB: {e.response['Error']['Message']}</h3>", 500
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return f"<h3>Server Error: {str(e)}</h3>", 500

@app.route('/add', methods=['POST'])
def add_task():
    task_name = request.form['task']
    if not task_name.strip():
        return redirect(url_for('home'))
    try:
        tasks_table.put_item(Item={'task_id': task_name, 'task_name': task_name})
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Error adding task: {str(e)}")
        return f"<h3>Failed to add task: {str(e)}</h3>", 500

@app.route('/delete/<string:task_id>')
def delete_task(task_id):
    try:
        tasks_table.delete_item(Key={'task_id': task_id})
        return redirect(url_for('home'))
    except Exception as e:
        print(f"Error deleting task: {str(e)}")
        return f"<h3>Failed to delete task: {str(e)}</h3>", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
