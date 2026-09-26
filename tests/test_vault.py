import os
import tempfile
import pytest
from openbrain.vault import Vault
from openbrain.memory_engine import MemoryEngine
from openbrain.engine import OpenbrainEngine

def test_vault_fresh_database():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_openbrain.db")
        
        # Test vault directly on a fresh db without prior table creation
        v = Vault(db_path)
        assert v.unlock("super_secret_password") is True
        
        v.set_secret("TEST_API_KEY", "sk-live-123456789")
        decrypted = v.get_secret("TEST_API_KEY")
        assert decrypted == "sk-live-123456789"
        
        # Non-existent secret
        assert v.get_secret("NON_EXISTENT") is None

def test_vault_wrong_password():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_openbrain.db")
        v1 = Vault(db_path)
        v1.unlock("correct_pass")
        v1.set_secret("SECRET", "classified_info")
        
        # Try unlocking with wrong password
        v2 = Vault(db_path)
        v2.unlock("wrong_pass")
        with pytest.raises(Exception):
            v2.get_secret("SECRET")

def test_memory_engine_vault_table_creation():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_openbrain.db")
        chroma_path = os.path.join(tmpdir, "chroma_db")
        
        # MemoryEngine initializes SQLite schema including secrets_vault
        mem = MemoryEngine(db_path, chroma_path)
        
        v = Vault(db_path)
        v.unlock("pass123")
        v.set_secret("KEY", "val")
        assert v.get_secret("KEY") == "val"

def test_openbrain_engine_compatibility():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
        db_path = os.path.join(tmpdir, "test_openbrain.db")
        chroma_path = os.path.join(tmpdir, "chroma_db")
        
        engine = OpenbrainEngine(db_path, chroma_path)
        mem_id = engine.save_memory("Test memory content", tier="Shortterm")
        assert mem_id is not None
        
        engine.update_kanban("proj1", "TASK-1", "open")
        kanban = engine.get_kanban("proj1")
        assert "TASK-1" in kanban
        assert kanban["TASK-1"]["status"] == "open"
