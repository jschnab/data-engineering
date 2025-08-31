CREATE MODEL sentiment_analysis_model
INPUT (text STRING COMMENT 'Input text for sentiment analysis')
OUTPUT (sentiment STRING COMMENT 'Predicted sentiment (positive/negative/neutral/mixed)')
COMMENT 'A model for sentiment analysis of text'
WITH (
    'provider' = 'googleai'
    , 'endpoint' = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'
    , 'api-key' = '<api-key>'
    , 'system-prompt' = 'Classify the text below into one of the following labels: [positive, negative, neutral, mixed]. Output only the label.'
);
