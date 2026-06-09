import base64
import gzip
import json

import pytest

from tools.validate_trace_export import account_symbols, load_exported_document, validate_symbol_contract


def write_encoded_payload(tmp_path, payload):
    path = tmp_path / "trace.json.b64"
    path.write_bytes(base64.b64encode(gzip.compress(json.dumps(payload).encode("utf-8"))))
    return path


def test_load_exported_document_rehydrates_named_records(tmp_path):
    payload = [
        [{"domainname": "node001", "np": "1", "state": "-", "qname": ["debug"], "core_job_map": {"0": "1"}}],
        {"1": ["alice", "R", "debug"]},
        {"debug": ["1", 0, 1, "E"]},
        1,
        0,
    ]

    document = load_exported_document(write_encoded_payload(tmp_path, payload))

    assert document.jobs_dict["1"].user_name == "alice"
    assert document.jobs_dict["1"].job_state == "R"
    assert document.queues_dict["debug"].run == 1
    assert document.total_running_jobs == 1


def test_account_symbols_reads_qtop_symbol_column():
    class WNOccupancy:
        account_jobs_table = [["0", 1], ["*", 2]]

    assert account_symbols(WNOccupancy()) == ["0", "*"]


def test_validate_symbol_contract_accepts_long_tail_without_reserved_symbols():
    validate_symbol_contract(["0", "1", "*"])


@pytest.mark.parametrize("reserved", ["_", "#", "?"])
def test_validate_symbol_contract_rejects_reserved_account_symbols(reserved):
    with pytest.raises(ValueError, match="reserved symbols"):
        validate_symbol_contract(["0", reserved, "*"])
