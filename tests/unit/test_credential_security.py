"""Security regressions: authentication must never persist plaintext files."""
from unittest.mock import MagicMock

import pytest

import src.auth as auth


@pytest.fixture
def vault(monkeypatch, tmp_path):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    store = {}
    backend = MagicMock()
    backend.get_password.side_effect = lambda service, account: store.get((service, account))
    backend.set_password.side_effect = lambda service, account, value: store.__setitem__((service, account), value)
    backend.delete_password.side_effect = lambda service, account: store.pop((service, account), None)
    monkeypatch.setattr(auth.TickTickAuth, "_keyring", staticmethod(lambda: backend), raising=False)
    monkeypatch.setattr(auth, "TickTickClient", MagicMock())
    return tmp_path, backend


def test_login_persists_only_in_vault(vault):
    directory, backend = vault
    manager = auth.TickTickAuth()
    assert manager.authenticate("alice", "secret")
    assert not list(directory.iterdir())
    assert backend.set_password.called
    other = auth.TickTickAuth()
    assert other.is_authenticated()
    assert other.get_username() == "alice"
    other.get_client()
    auth.TickTickClient.assert_called_with("alice", "secret")
    assert other.logout()
    assert not manager.is_authenticated()
    assert not list(directory.iterdir())


def test_no_plaintext_fallback(vault):
    directory, backend = vault
    backend.set_password.side_effect = RuntimeError("vault unavailable")
    assert not auth.TickTickAuth().authenticate("alice", "secret")
    assert not list(directory.iterdir())


def test_legacy_credentials_are_not_loaded(vault):
    directory, _ = vault
    old = directory / ".ticktick-mcp"
    old.mkdir()
    (old / "credentials.json").write_text('{"username":"alice","password":"secret","authenticated":true}')
    assert not auth.TickTickAuth().is_authenticated()


def test_failed_login_does_not_save(vault):
    _, backend = vault
    auth.TickTickClient.side_effect = RuntimeError("rejected")
    assert not auth.TickTickAuth().authenticate("alice", "secret")
    backend.set_password.assert_not_called()


def test_rejects_insecure_backend(monkeypatch):
    backend = MagicMock()
    
    monkeypatch.setattr(auth.keyring, "get_keyring", lambda: backend)
    with pytest.raises(RuntimeError, match="No secure OS keyring"):
        auth.TickTickAuth._keyring()
    backend.set_password.assert_not_called()


def test_existing_env_is_untouched(vault):
    directory, _ = vault
    env = directory / ".env"
    env.write_text("UNRELATED=value\n")
    manager = auth.TickTickAuth()
    assert manager.authenticate("alice", "secret")
    assert manager.logout()
    assert env.read_text() == "UNRELATED=value\n"


def test_helpers_use_vault(vault, monkeypatch):
    import auth as runtime_auth
    from src.utils.helpers import load_credentials, save_credentials
    monkeypatch.setattr(runtime_auth.TickTickAuth, "_keyring", staticmethod(auth.TickTickAuth._keyring))
    directory, _ = vault
    assert save_credentials("alice", "secret")
    assert load_credentials()["username"] == "alice"
    assert not list(directory.iterdir())


def test_environment_password_cannot_reauthenticate(monkeypatch):
    from src import server
    manager = MagicMock()
    manager.is_authenticated.return_value = False
    monkeypatch.setattr(server, "TickTickAuth", lambda: manager)
    monkeypatch.setenv("TICKTICK_USERNAME", "alice")
    monkeypatch.setenv("TICKTICK_PASSWORD", "secret")
    assert not server.ensure_authenticated()
    manager.authenticate.assert_not_called()


def test_vault_read_error_is_unauthenticated(vault):
    _, backend = vault
    backend.get_password.side_effect = RuntimeError("locked")
    assert not auth.TickTickAuth().is_authenticated()


def test_logout_reports_vault_failure(vault):
    _, backend = vault
    manager = auth.TickTickAuth()
    assert manager.authenticate("alice", "secret")
    backend.delete_password.side_effect = RuntimeError("locked")
    assert not manager.logout()


def test_malformed_vault_record_is_unauthenticated(vault):
    _, backend = vault
    backend.get_password.side_effect = None
    backend.get_password.return_value = '{"authenticated":true}'
    assert not auth.TickTickAuth().is_authenticated()
