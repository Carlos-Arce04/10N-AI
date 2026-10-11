# Schemas Pydantic para los modelos de Machine Learning
from .avocado_api_models import (
    AvocadoPredictionRequest,
    AvocadoPredictionResponse,
    AvocadoHealthResponse,
    AvocadoRegionsResponse,
    AvocadoTypesResponse
)
from .wine_api_models import (
    WinePredictionRequest,
    WinePredictionResponse,
    WineHealthResponse
)
from .car_api_models import (
    CarPredictionRequest,
    CarPredictionResponse,
    CarHealthResponse,
    CarOptionsResponse
)
from .churn_api_models import (
    ChurnPredictionRequest,
    ChurnPredictionResponse,
    ChurnHealthResponse,
    ChurnOptionsResponse
)
from .stroke_api_models import (
    StrokePredictionRequest,
    StrokePredictionResponse,
    StrokeHealthResponse,
    StrokeOptionsResponse
)
