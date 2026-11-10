import pytest

from bank2ynab.bank_handler import get_output_path


class TestGetOutputPath:
    def test_strips_xlsx_extension(self, tmp_path):
        """XLSX inputs must not leave a stray character in the output name."""
        src = tmp_path / "statement.xlsx"
        src.touch()
        result = get_output_path(
            input_path=str(src), prefix="Converted XLS_Test_", ext=".csv"
        )
        assert result == str(tmp_path / "Converted XLS_Test_statement.csv")

    def test_strips_csv_extension(self, tmp_path):
        """CSV inputs keep working exactly as before."""
        src = tmp_path / "statement.csv"
        src.touch()
        result = get_output_path(
            input_path=str(src), prefix="Test_", ext=".csv"
        )
        assert result == str(tmp_path / "Test_statement.csv")


class TestBankHandler:
    @pytest.mark.skip(reason="Not tested yet.")
    def test_preprocess_file(self):
        """Test that preprocess file returns the unchanged filepath."""
        path = "test"
        assert path == "test_path"

    @pytest.mark.skip(reason="Not tested yet.")
    def test_get_output_path(self):
        raise NotImplementedError
