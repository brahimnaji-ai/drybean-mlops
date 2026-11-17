from pathlib import Path

import pytest

from drybean.params import Params, load_params

VALID_PARAMS_YAML = """\
seed: 42
data:
  golden_ratio: 0.20
  base_ratio: 0.40
  n_batches: 6
train:
  algorithm: logreg
  logreg:
    C: 1.0
    max_iter: 1000
  random_forest:
    n_estimators: 200
    max_depth: null
promotion:
  metric: macro_f1
  min_delta: 0.0
  min_f1_floor: 0.0
monitoring:
  window_days: 7
  drift_share_threshold: 0.3
  min_samples: 200
"""


def write_params(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "params.yaml"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_params_valid_file(tmp_path: Path) -> None:
    path = write_params(tmp_path, VALID_PARAMS_YAML)

    params = load_params(path)

    assert isinstance(params, Params)
    assert params.seed == 42
    assert params.data.golden_ratio == 0.2
    assert params.train.algorithm == "logreg"
    assert params.train.logreg.c == 1.0
    assert params.train.random_forest.max_depth is None
    assert params.promotion.metric == "macro_f1"
    assert params.monitoring.min_samples == 200


def test_load_params_rejects_unknown_key(tmp_path: Path) -> None:
    path = write_params(tmp_path, VALID_PARAMS_YAML + "unknown: true\n")

    with pytest.raises(ValueError, match=r"params\.yaml: .*unknown"):
        load_params(path)


def test_load_params_rejects_split_ratios_that_leave_no_data(tmp_path: Path) -> None:
    content = VALID_PARAMS_YAML.replace("golden_ratio: 0.20", "golden_ratio: 0.60")
    path = write_params(tmp_path, content)

    with pytest.raises(ValueError, match=r"params\.yaml: data: .*less than 1"):
        load_params(path)


def test_load_params_rejects_invalid_algorithm(tmp_path: Path) -> None:
    path = write_params(tmp_path, VALID_PARAMS_YAML.replace("algorithm: logreg", "algorithm: svm"))

    with pytest.raises(ValueError, match=r"params\.yaml: train\.algorithm"):
        load_params(path)


def test_load_params_rejects_out_of_range_threshold(tmp_path: Path) -> None:
    content = VALID_PARAMS_YAML.replace("drift_share_threshold: 0.3", "drift_share_threshold: 1.1")
    path = write_params(tmp_path, content)

    with pytest.raises(ValueError, match=r"params\.yaml: monitoring\.drift_share_threshold"):
        load_params(path)


def test_load_params_reports_yaml_parse_error(tmp_path: Path) -> None:
    path = write_params(tmp_path, "data: [unclosed\n")

    with pytest.raises(ValueError, match=r"Invalid YAML in parameters file .*params\.yaml"):
        load_params(path)


def test_load_params_reports_missing_file_path(tmp_path: Path) -> None:
    path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError, match=r"Parameters file not found: .*missing\.yaml"):
        load_params(path)
