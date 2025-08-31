SELECT * FROM
ML_PREDICT(
  TABLE mytable,
  MODEL sentiment_analysis_model,
  DESCRIPTOR(message)
);
