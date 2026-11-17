"""Validated pipeline parameters loaded from YAML."""

from pathlib import Path
from typing import Literal, Self

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator


class _StrictModel(BaseModel):
    """Base model that rejects unrecognized configuration fields."""

    model_config = ConfigDict(extra="forbid")


class DataParams(_StrictModel):
    """Parameters for preparing the dataset splits and batches."""

    golden_ratio: float = Field(gt=0, lt=1)
    base_ratio: float = Field(gt=0, lt=1)
    n_batches: int = Field(ge=1)

    @model_validator(mode="after")
    def validate_split_ratios(self) -> Self:
        """Require the reserved split ratios to leave data for later batches."""
        if self.golden_ratio + self.base_ratio >= 1:
            raise ValueError("golden_ratio + base_ratio must be less than 1")
        return self


class LogRegParams(_StrictModel):
    """Hyperparameters for logistic regression."""

    c: float = Field(validation_alias="C", gt=0)
    max_iter: int = Field(ge=1)


class RandomForestParams(_StrictModel):
    """Hyperparameters for a random forest classifier."""

    n_estimators: int = Field(ge=1)
    max_depth: int | None = Field(default=None, ge=1)


class TrainParams(_StrictModel):
    """Algorithm selection and model hyperparameters."""

    algorithm: Literal["logreg", "random_forest"]
    logreg: LogRegParams
    random_forest: RandomForestParams


class PromotionParams(_StrictModel):
    """Metric thresholds used when deciding whether to promote a model."""

    metric: Literal["macro_f1"]
    min_delta: float = Field(ge=0, le=1)
    min_f1_floor: float = Field(ge=0, le=1)


class MonitoringParams(_StrictModel):
    """Window and threshold settings for drift monitoring."""

    window_days: int = Field(ge=1)
    drift_share_threshold: float = Field(ge=0, le=1)
    min_samples: int = Field(ge=1)


class Params(_StrictModel):
    """Complete pipeline parameter document."""

    seed: int = Field(ge=0)
    data: DataParams
    train: TrainParams
    promotion: PromotionParams
    monitoring: MonitoringParams


def load_params(path: Path) -> Params:
    """Load and validate pipeline parameters from a YAML file."""
    try:
        raw_params = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"Parameters file not found: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in parameters file {path}: {exc}") from exc

    try:
        return Params.model_validate(raw_params)
    except ValidationError as exc:
        field_errors = "; ".join(
            f"{'.'.join(str(part) for part in error['loc']) or '<root>'}: {error['msg']}"
            for error in exc.errors()
        )
        raise ValueError(f"Invalid parameters in {path}: {field_errors}") from exc
