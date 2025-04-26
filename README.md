# Personalized Nutrition Recommender

A comprehensive microservices-based application for personalized nutrition analysis and glucose response prediction.

## Overview

This project uses modern microservices architecture to analyze meals, predict glucose responses, and provide nutrition recommendations based on:
- Visual food analysis
- User clinical data
- Microbiome profiles
- Meal characteristics

## System Architecture

The system consists of multiple microservices that work together:

1. **Nutrition Controller (API Gateway)**: Central controller that coordinates between all services
2. **Food Analyzer**: Analyzes meal images to identify ingredients
3. **Nutrition Predictor**: Predicts nutritional content of meals
4. **Microbiome Analyzer**: Processes user microbiome data for gut health insights
5. **Glucose Monitor**: Predicts personalized glucose responses to meals
6. **User Interface**: Modern web interface for interacting with the system

## Features

- **Meal Analysis**: Upload images of meals and get detailed nutritional breakdown
- **Glucose Prediction**: Personalized glucose response predictions based on meal content, user biology, and microbiome
- **Microbiome Analysis**: Gain insights about gut health based on microbiome profiles
- **Monitoring Dashboard**: Real-time system metrics using Prometheus and Grafana

## Database Schema

The system uses PostgreSQL with the following tables:
- `user_profile`: User authentication and profile information
- `meal_log`: History of analyzed meals and predictions
- `microbiome_data`: User microbiome test results
- `clinical_user_data`: User health metrics (BMI, glucose levels, etc.)

## Getting Started

### Prerequisites
- Docker and Docker Compose
- API keys for external services (Clarifai, OpenAI, etc.)

### Environment Configuration
Create a `.env` file with the following variables

DB_HOST
DB_NAME
DB_USER
DB_PASSWORD
DB_PORT
CLARIFAI_PAT
CLARIFAI_USER_ID
CLARIFAI_APP_ID
OPENAI_API_KEY
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY

avaible as github secrets in our repository.
```

### Running the Application
```bash
docker-compose up
```

The application will be available at http://localhost:8000, with the UI at http://localhost:3000.

## Using the Different Services

### Analyze a Meal
After navigating to the analyze meal page the user should first input a meal photo by either dragging and dropping or by browsing through the device and selecting an image of type .jpg or .png after inputing the user selects a meal category then presses the Analyze Meal button to get the results if the image not clear error is displayed then the user must enter a brief description to help the model asses the meal image accuratly.

### Predict Glucose Response
In the first section of the Glucose Response Predictor the user should input his clinical data and microbiome data both are .csv files then proceeds to the next section by pressing Next, the user is then required to follow a similar procedure to the Analyze Meal functionality, then the user presses Complete prediction to view the predicted glucose spike after 60 minutes.

### Gut Health Analyzer
The user enters his microbiome data as a .csv file and then presses Analyze Gut Health, and then the predicted gut health should be outputed and if the gut health is bad a small recomendation on how to improve it is also displayed.

## Architecture Diagram

```

┌───────────────────┐     ┌─────────────────┐
│    UI Frontend    │◄────┤ API Gateway     │
└───────────────────┘     │(NutritionController)
                          └────────┬────────┘
                                  ▲│▲
                  ┌───────────────┘│└──────────────┬──────────────┐
                  │                │               │              │
        ┌─────────▼────────┐ ┌─────▼─────────┐ ┌───▼────────┐ ┌──▼──────────┐
        │   Food Analyzer  │ │ Nutrition     │ │ Microbiome │ │ Glucose     │
        │                  │ │ Predictor     │ │ Analyzer   │ │ Monitor     │
        └──────────────────┘ └───────────────┘ └────────────┘ └─────────────┘
                  │                │               │              │
                  └────────────────┴───────────────┴──────────────┘
                                       │
                                   ┌───▼───┐
                                   │ DB    │
                                   └───────┘
```

## Monitoring

The system includes Prometheus metrics and a Grafana dashboard for monitoring:
- Request counts
- Latency metrics
- Prediction values
- Service health

## Troubleshooting

Common issues:
- **Column name mismatches**: Ensure CSV files for clinical/microbiome data use the expected column names (`clinical_Age`, `clinical_Weight`, etc.)
- **Service connectivity**: Check that all services can communicate with each other
- **Database connection**: Verify database credentials and connection parameters
