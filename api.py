from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory storage for the API key (Team working with servers remember to replace this with a more secure solution (use a database))
api_key_storage = {}

@app.route('/api/set_api_key', methods=['POST'])
def set_api_key():
    """
    Sets the OpenAI API key.

    Expects a JSON payload with the 'api_key' key containing the API key value.

    Returns:
        JSON response with a success message or an error message.
    """
    data = request.get_json()
    if 'api_key' in data:
        api_key_storage['api_key'] = data['api_key']
        return jsonify({'message': 'API key set successfully'}), 200
    else:
        return jsonify({'message': 'API key not provided'}), 400

@app.route('/api/get_api_key', methods=['GET'])
def get_api_key():
    """
    Retrieves the OpenAI API key.

    Returns:
        JSON response with the API key if it has been set, or an error message.
    """
    if 'api_key' in api_key_storage:
        return jsonify({'api_key': api_key_storage['api_key']}), 200
    else:
        return jsonify({'message': 'API key not set'}), 404

if __name__ == '__main__':
    app.run(debug=True)
