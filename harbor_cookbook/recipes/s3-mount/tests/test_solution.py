from pathlib import Path


def test_result_file_exists():
    result_path = Path("/app/result.txt")
    assert result_path.exists(), "result.txt was not created"


def test_result_is_correct():
    data_path = Path("/app/data.txt")
    assert data_path.exists(), "/app/data.txt not found — S3 download may have failed"
    numbers = [int(line.strip()) for line in data_path.read_text().strip().splitlines()]
    expected = sum(numbers)

    result = Path("/app/result.txt").read_text().strip()
    assert result == str(expected), f"Expected sum {expected}, got '{result}'"
