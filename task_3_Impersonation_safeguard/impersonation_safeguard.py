import pytest
import logging
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('impersonation_audit.log'), logging.StreamHandler()]
)

@dataclass
class User:
    user_id: str
    role: str 
    org_id: str

class ImpersonationSystem:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self.impersonation_logs: list = []
        self.current_sessions: Dict[str, str] = {}

    def add_user(self, user_id: str, role: str, org_id: str):
        self.users[user_id] = User(user_id, role, org_id)
        logging.info(f"Added user: {user_id} with role: {role}")

    def can_impersonate(self, actor_id: str, target_id: str) -> bool:
        if actor_id not in self.users or target_id not in self.users:
            return False
        actor = self.users[actor_id]
        if actor.role not in ['admin', 'support']:
            return False
        if actor.user_id == target_id:  
            return False
        return True

    def start_impersonation(self, actor_id: str, target_id: str) -> Dict[str, Any]:
        result = {
            "success": False,
            "session_id": None,
            "message": "",
            "timestamp": datetime.now()
        }

        if not self.can_impersonate(actor_id, target_id):
            result["message"] = "Unauthorized: Insufficient privileges or invalid target."
            self._log_impersonation_attempt(actor_id, target_id, "FAILED", result["message"])
            return result

        session_id = f"session_{datetime.now().timestamp()}"
        self.current_sessions[session_id] = target_id
        result["success"] = True
        result["session_id"] = session_id
        result["message"] = f"Impersonation started for {target_id}"
        self._log_impersonation_attempt(actor_id, target_id, "SUCCESS", result["message"])


        return result

    def end_impersonation(self, session_id: str) -> bool:
        if session_id in self.current_sessions:
            target_id = self.current_sessions.pop(session_id)
            logging.info(f"Impersonation ended for session {session_id}, target {target_id}")
            self._log_impersonation_attempt(None, target_id, "ENDED", f"Session {session_id} ended")
            return True
        return False

    def get_user_data(self, session_id: str) -> Dict[str, Any]:
        if session_id not in self.current_sessions:
            return {"error": "No active impersonation session"}
        target_id = self.current_sessions[session_id]
        # Simulate accessing user data
        return {"user_id": target_id, "sensitive_data": "users info", "org_id": self.users[target_id].org_id}

    def _log_impersonation_attempt(self, actor_id: str, target_id: str, status: str, message: str):
        log_entry = {
            "actor_id": actor_id,
            "target_id": target_id,
            "status": status,
            "message": message,
            "timestamp": datetime.now()
        }
        self.impersonation_logs.append(log_entry)
        logging.info(f"Impersonation log: {log_entry}")

    def get_logs(self) -> list:
        return self.impersonation_logs


@pytest.fixture
def impersonation_system():
    system = ImpersonationSystem()
    # Setup test users
    system.add_user("admin1", "admin", "org1")
    system.add_user("support1", "support", "org1")
    system.add_user("user1", "user", "org1")
    system.add_user("user2", "user", "org2")
    return system

def test_authorized_impersonation_admin(impersonation_system):
    result = impersonation_system.start_impersonation("admin1", "user1")
    assert result["success"] is True
    assert result["session_id"] is not None

    # access data
    data = impersonation_system.get_user_data(result["session_id"])
    assert "error" not in data
    assert data["user_id"] == "user1"

    # end session
    assert impersonation_system.end_impersonation(result["session_id"])

def test_authorized_impersonation_support(impersonation_system):
    result = impersonation_system.start_impersonation("support1", "user1")
    assert result["success"] is True

def test_unauthorized_impersonation_by_user(impersonation_system):
    result = impersonation_system.start_impersonation("user1", "user2")
    assert result["success"] is False
    assert "Unauthorized" in result["message"]

def test_unauthorized_impersonation_invalid_target(impersonation_system):
    result = impersonation_system.start_impersonation("admin1", "nonexistent")
    assert result["success"] is False

def test_access_without_session(impersonation_system):
    data = impersonation_system.get_user_data("invalid_session")
    assert "error" in data

def test_logging_successful_impersonation(impersonation_system):
    impersonation_system.start_impersonation("admin1", "user1")
    logs = impersonation_system.get_logs()
    assert len(logs) > 0
    success_log = next((log for log in logs if log["status"] == "SUCCESS"), None)
    assert success_log is not None
    assert success_log["actor_id"] == "admin1"
    assert success_log["target_id"] == "user1"

def test_logging_failed_impersonation(impersonation_system):
    impersonation_system.start_impersonation("user1", "user2")
    logs = impersonation_system.get_logs()
    failed_log = next((log for log in logs if log["status"] == "FAILED"), None)
    assert failed_log is not None
    assert "Insufficient" in failed_log["message"]

def test_concurrent_impersonation(impersonation_system):
    session1 = impersonation_system.start_impersonation("admin1", "user1")["session_id"]
    session2 = impersonation_system.start_impersonation("support1", "user2")["session_id"]
    assert session1 != session2
    assert impersonation_system.current_sessions.get(session1) == "user1"
    assert impersonation_system.current_sessions.get(session2) == "user2"

def test_end_nonexistent_session(impersonation_system):
    assert impersonation_system.end_impersonation("fake_session") is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])