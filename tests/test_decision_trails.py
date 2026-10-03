import os
import tempfile
import pytest
from openbrain.memory_engine import MemoryEngine


def test_record_and_ingest_decision_trail():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    chroma_dir = tempfile.mkdtemp()

    try:
        me = MemoryEngine(db_path=db_path, chroma_path=chroma_dir)
        trail_id = me.record_decision_trail(
            decision_summary="Use SQLite DAG over Redis",
            rationale="Eliminates external daemon dependency and provides ACID transaction boundaries",
            alternatives="Redis, RabbitMQ, Kafka",
            tradeoffs="Single-host lock contention at high concurrency",
            task_id="sc-101"
        )
        assert trail_id is not None
        assert len(trail_id) > 10

        # Query memory
        res = me.retrieve_similar("SQLite DAG ACID transaction", top_k=2)
        assert len(res) >= 1
        assert "SQLite" in res[0]["content"]

        # Test TSV ingestion
        tsv_path = os.path.join(chroma_dir, "decisions.tsv")
        with open(tsv_path, "w", encoding="utf-8") as f:
            f.write("timestamp\ttask_id\tdecision\talternatives\trationale\ttradeoffs\n")
            f.write("2026-10-03T08:00:00\tsc-202\tAdopt Emil Kowalski motion physics\tStandard CSS easing\tSpring physics feel organic and tactile\tSlightly larger runtime bundle\n")

        count = me.ingest_decision_tsv(tsv_path)
        assert count == 1
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
        import shutil
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir, ignore_errors=True)
