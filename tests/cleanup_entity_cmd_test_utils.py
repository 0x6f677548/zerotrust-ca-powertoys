from click.testing import CliRunner
import json
from click.core import BaseCommand
from .utils import assert_valid_output_file


def _test_cleanup_entity(test_data: list[dict], cli: BaseCommand):
    runner = CliRunner()

    # we might receive a list of policies or a single policy
    if isinstance(test_data, list):
        first_entity = test_data[0]
    else:
        first_entity = test_data

    # check that the test data has id, createdDateTime and modifiedDateTime
    assert "id" in first_entity
    assert "createdDateTime" in first_entity
    assert "modifiedDateTime" in first_entity

    with runner.isolated_filesystem():
        # write the test data to a file
        test_data_file = "test_data.json"
        with open(test_data_file, "w") as f:
            # convert the test data to a string
            f.write(json.dumps(test_data, indent=4))

        assert_valid_output_file(test_data_file)

        result = runner.invoke(
            cli,
            [
                "--input_file",
                test_data_file,
                "--output_file",
                test_data_file,
            ],
        )
        assert result is not None
        assert result.exit_code == 0
        assert_valid_output_file(test_data_file)

        # check if the file was cleaned up, by checking if the id, createdDateTime and modifiedDateTime are gone
        with open(test_data_file) as f:
            data = json.load(f)

            # check if the expected node is present
            assert "id" not in data[0]
            assert "createdDateTime" not in data[0]
            assert "modifiedDateTime" not in data[0]
