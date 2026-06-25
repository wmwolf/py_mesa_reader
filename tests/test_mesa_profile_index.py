import os

import numpy as np
import pytest

import mesa_reader as mr

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INDEX = os.path.join(DATA_DIR, "LOGS", "profiles.index")


def test_reads_index_columns():
    idx = mr.MesaProfileIndex(INDEX)
    np.testing.assert_array_equal(idx.model_numbers, [10, 20])
    np.testing.assert_array_equal(idx.profile_numbers, [1, 2])
    np.testing.assert_array_equal(idx.data("priorities"), [2, 2])
    # Integer columns must stay integers, matching the old genfromtxt path.
    assert np.issubdtype(idx.data("model_numbers").dtype, np.integer)


def test_model_profile_mapping():
    idx = mr.MesaProfileIndex(INDEX)
    assert idx.profile_with_model_number(20) == 2
    assert idx.model_with_profile_number(1) == 10
    assert idx.have_profile_with_model_number(10)
    assert not idx.have_profile_with_model_number(999)
    assert idx.have_profile_with_profile_number(2)
    assert not idx.have_profile_with_profile_number(999)


def test_missing_profile_raises():
    idx = mr.MesaProfileIndex(INDEX)
    with pytest.raises(mr.ProfileError):
        idx.profile_with_model_number(999)
    with pytest.raises(mr.ProfileError):
        idx.model_with_profile_number(999)


def test_invalid_column_raises():
    idx = mr.MesaProfileIndex(INDEX)
    with pytest.raises(KeyError):
        idx.data("not_a_column")


def test_preserves_file_order(tmp_path):
    # Rows are kept in file order (the index is not re-sorted by model number);
    # the mapping must still resolve correctly regardless of row order.
    index_file = tmp_path / "profiles.index"
    index_file.write_text(
        "# comment line\n"
        "          20            2            2\n"
        "          10            2            1\n"
    )
    idx = mr.MesaProfileIndex(str(index_file))
    np.testing.assert_array_equal(idx.model_numbers, [20, 10])
    np.testing.assert_array_equal(idx.profile_numbers, [2, 1])
    assert idx.profile_with_model_number(10) == 1
    assert idx.model_with_profile_number(2) == 20
