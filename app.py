from flask import Flask, jsonify, request
from eventRepository import eventRepository

app = Flask(__name__)
repo = eventRepository()

'''
Sample Request Body
{
    "summary"
    "start"
    "end"
}

'''

@app.route('/', methods=['GET'])
def get_events():
    todos = repo.get_all()
    response = jsonify(todos)
    response.status_code = 200
    return response


@app.route('/<string:event_id>', methods=['GET'])
def get_event(event_id):
    event = repo.get_id(event_id)
    response = jsonify(event)
    response.status_code = 200
    return response


@app.route('/', methods=['POST'])
def save_event():
    event = request.get_json()
    new_event = repo.save(event)
    response = jsonify(repo.get_id(new_event))
    response.status_code = 201
    return response

@app.route('/', methods=['PUT'])
def update_event():
    body = request.get_json()
    event_id = body["_id"]
    updated = repo.update(body)
    if updated >= 1:
        response = jsonify(repo.get_id(event_id))
        response.status_code = 200
    else:
        response = jsonify({"status_code": 404})
    return response


@app.route('/<string:event_id>', methods=['DELETE'])
def delete_event(event_id):
    deleted = repo.delete(event_id)
    if deleted >= 1:
        response = jsonify({"status_code": 200})
    else:
        response = jsonify({"status_code": 404})
    return response




if __name__ == '__main__':
    app.run(port=8080)
