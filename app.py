from flask import Flask, render_template, request, jsonify
from datetime import datetime
from src.pipeline.training import TrainingPipeline
from src.entity.config_entity import TrainingPipelineConfig

app = Flask(__name__)

# Initialize training pipeline
training_pipeline_config = TrainingPipelineConfig()
tr = TrainingPipeline(training_pipeline_config=training_pipeline_config)

def start_training():
    try:
        tr.start()
        return "Training started successfully"
    except Exception as e:
        return f"Error starting training: {str(e)}"

def make_prediction():
    try:
        # Placeholder for prediction logic
        return "Prediction executed successfully"
    except Exception as e:
        return f"Error making prediction: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train():
    message = start_training()
    return jsonify({"message": message})

@app.route('/predict', methods=['POST'])
def predict():
    message = make_prediction()
    return jsonify({"message": message})

if __name__ == '__main__':
    app.run(debug=True)