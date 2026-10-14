from backend.app.security import create_otp, create_session_token, read_session_token, verify_otp


def test_otp_is_hashed_and_one_time_code_verifies():
    code, digest = create_otp()
    assert code != digest
    assert verify_otp(code, digest)
    assert not verify_otp("000000" if code != "000000" else "111111", digest)


def test_session_token_rejects_tampering():
    token = create_session_token("user-1", "test-secret")
    assert read_session_token(token, "test-secret") == "user-1"
    assert read_session_token(token + "x", "test-secret") is None
    assert read_session_token(token, "other-secret") is None
