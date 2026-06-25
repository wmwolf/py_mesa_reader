import os

import numpy as np
import pytest

import mesa_reader as mr

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LOGS = os.path.join(DATA_DIR, "LOGS")


def test_reads_history_and_index():
    log = mr.MesaLogDir(LOGS)
    assert log.history.is_history()
    np.testing.assert_array_equal(log.profile_numbers, [1, 2])
    np.testing.assert_array_equal(log.model_numbers, [10, 20])


def test_profile_model_number_mapping():
    log = mr.MesaLogDir(LOGS)
    assert log.profile_with_model_number(20) == 2
    assert log.model_with_profile_number(1) == 10
    assert log.have_profile_with_model_number(10)
    assert not log.have_profile_with_model_number(999)


def test_profile_data_defaults_to_last_profile():
    log = mr.MesaLogDir(LOGS)
    p = log.profile_data()
    assert p.model_number == 20


def test_profile_data_by_model_number():
    log = mr.MesaLogDir(LOGS)
    p = log.profile_data(model_number=10)
    assert p.model_number == 10
    np.testing.assert_allclose(p.data("logRho"), [2.0, 1.0, 0.0])


def test_memoization_returns_same_object():
    log = mr.MesaLogDir(LOGS, memoize_profiles=True)
    assert log.profile_data(profile_number=1) is log.profile_data(profile_number=1)

    log_no_memo = mr.MesaLogDir(LOGS, memoize_profiles=False)
    first = log_no_memo.profile_data(profile_number=1)
    second = log_no_memo.profile_data(profile_number=1)
    assert first is not second


def test_select_models():
    log = mr.MesaLogDir(LOGS)
    selected = log.select_models(lambda age: age > 1200.0, "star_age")
    np.testing.assert_array_equal(selected, [20])


def test_bad_path_raises():
    with pytest.raises(mr.BadPathError):
        mr.MesaLogDir(os.path.join(DATA_DIR, "does_not_exist"))
