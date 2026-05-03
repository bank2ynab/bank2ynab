import pytest


class TestBankHandler:
    @pytest.mark.skip(reason="Not tested yet.")
    def test_preprocess_file(self):
        """Test that preprocess file returns the unchanged filepath."""
        path = "test"
        assert path == "test_path"

    @pytest.mark.skip(reason="Not tested yet.")
    def test_get_output_path(self):
        raise NotImplementedError
