from transfer_benchmark import run_transfer_benchmark


def test_transfer_benchmark_verifies_quality_and_deduplication(tmp_path):
    report = run_transfer_benchmark(tmp_path / "transfer.json")

    assert report["benchmark"] == "sentinel-transfer-v1"
    assert report["transfer_verified"] is True
    assert report["passed"] == report["total"] == 3
    assert report["cases"]["provider_failure_diagnosis"]["passed"] is True
