import os

import numpy as np
import pytest

import mesa_reader as mr

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
HISTORY = os.path.join(DATA_DIR, "LOGS", "history.data")
RESTART_HISTORY = os.path.join(DATA_DIR, "restart_history.data")
PROFILE = os.path.join(DATA_DIR, "LOGS", "profile1.data")


def test_reads_bulk_data():
    m = mr.MesaData(HISTORY)
    assert m.is_history()
    assert "model_number" in m.bulk_names
    assert isinstance(m.bulk_names, tuple)
    np.testing.assert_array_equal(m.model_number, [5, 10, 15, 20])
    np.testing.assert_allclose(m.star_age, [500.0, 1000.0, 1500.0, 2000.0])


def test_header_values_are_typed():
    # The header row must be parsed into native Python values, not left as raw
    # strings (regression guard for the pandas backend dropping eval()).
    m = mr.MesaData(HISTORY)
    assert m.initial_mass == 1.0
    assert isinstance(m.initial_mass, float)
    assert m.initial_z == 0.02
    assert m.version_number == "24.08.1"


def test_attribute_access_matches_data_method():
    m = mr.MesaData(HISTORY)
    np.testing.assert_array_equal(m.star_age, m.data("star_age"))
    assert m.initial_mass == m.header("initial_mass")


def test_log_linear_inference():
    m = mr.MesaData(PROFILE)
    # logRho is present; requesting Rho should exponentiate it.
    np.testing.assert_allclose(m.data("Rho"), 10 ** m.data("logRho"))
    # L is present; requesting log_L should take its log10.
    np.testing.assert_allclose(m.data("log_L"), np.log10(m.data("L")))


def test_invalid_key_raises():
    m = mr.MesaData(HISTORY)
    with pytest.raises(KeyError):
        m.data("not_a_real_column")


def test_remove_backups_restores_monotonic_model_numbers():
    # The file contains a run to model 21 followed by a restart from model 10
    # (1..21, then 10, 15, 20, 25). After scrubbing, model_number must be the
    # surviving monotonic sequence with all superseded rows obliterated.
    m = mr.MesaData(RESTART_HISTORY)
    expected = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25]
    np.testing.assert_array_equal(m.model_number, expected)
    assert np.all(np.diff(m.model_number) > 0)
    # Bulk columns must stay row-aligned with the kept model numbers.
    np.testing.assert_allclose(m.star_age, np.array(expected) * 100.0)


def test_remove_backups_noop_on_clean_history():
    m = mr.MesaData(HISTORY)
    before = m.model_number.copy()
    m.remove_backups()
    np.testing.assert_array_equal(m.model_number, before)


def test_data_at_model_number():
    m = mr.MesaData(HISTORY)
    assert m.data_at_model_number("star_age", 15) == 1500.0
    assert m.index_of_model_number(15) == 2


def test_profile_is_not_history():
    p = mr.MesaData(PROFILE)
    assert not p.is_history()
    assert p.model_number == 10  # from the header, not bulk data


def test_unknown_file_type_raises(tmp_path):
    bogus = tmp_path / "data.unknown"
    bogus.write_text("nothing useful\n")
    with pytest.raises(mr.UnknownFileTypeError):
        mr.MesaData(str(bogus))
