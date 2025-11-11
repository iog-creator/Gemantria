# Pattern Forecast Analytics Schema

JSON schema for forecasting temporal patterns using statistical models

## Schema Definition

**File**: `pattern-forecast.schema.json`

**JSON Schema Version**: https://json-schema.org/draft/2020-12/schema

## Properties

### `forecasts`
**Required**
**Type**: `array`
**Description**: Array of forecast records for temporal series

**Items**:
- Type: `object`
- Properties:
  - `series_id`: Identifier for the concept or cluster being forecasted
  - `horizon`: Number of time steps to forecast ahead
  - `model`: Forecasting model used (naive, simple moving average, or ARIMA)
  - `predictions`: Array of forecasted values for each horizon step
  - `book`: Biblical book this forecast belongs to
  - `prediction_intervals`: Prediction intervals for uncertainty quantification
  - `rmse`: Root Mean Square Error of the forecast model
  - `mae`: Mean Absolute Error of the forecast model
  - `metadata`: Additional metadata about the forecast

### `metadata`
**Required**
**Type**: `object`

**Properties**:

### `generated_at`
**Type**: `string`
**Description**: Timestamp when forecasts were generated

### `forecast_parameters`
**Type**: `object`

**Properties**:

### `default_horizon`
**Type**: `integer`

### `default_model`
**Type**: `string`
**Allowed values**: naive, sma, arima

### `min_training_length`
**Type**: `integer`

### `total_forecasts`
**Type**: `integer`
**Description**: Total number of forecasts generated

### `books_forecasted`
**Type**: `array`
**Description**: List of biblical books with forecasts

**Items**:
- Type: `string`

### `model_distribution`
**Type**: `object`
**Description**: Distribution of forecasting models used

**Properties**:

### `naive`
**Type**: `integer`
**Description**: Number of naive model forecasts

### `sma`
**Type**: `integer`
**Description**: Number of simple moving average forecasts

### `arima`
**Type**: `integer`
**Description**: Number of ARIMA model forecasts

### `average_metrics`
**Type**: `object`
**Description**: Average performance metrics

**Properties**:

### `rmse`
**Type**: `number`
**Description**: Average RMSE across all forecasts

### `mae`
**Type**: `number`
**Description**: Average MAE across all forecasts
