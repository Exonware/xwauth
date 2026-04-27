#!/usr/bin/env python3
"""
Unit tests for SAML manager trust and strict validation hooks.
"""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from exonware.xwauth.identity.facade import XWAuth
from exonware.xwauth.identity.config.config import XWAuthConfig
from exonware.xwauth.identity.core.saml import SAMLManager
from exonware.xwauth.identity.errors import XWAuthError

# signxml/lxml: importing these repeatedly in one process can access-violate on Windows
# after several SAML tests; load once and reuse (GUIDE_53_FIX).
_signxml_loaded: bool = False
_signxml_unavailable: bool = False
_signxml_etree: type | None = None
_signxml_XMLSigner: type | None = None


def _self_signed_key_cert() -> tuple[bytes, bytes, x509.Certificate]:
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "test-idp")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.now(timezone.utc))
        .not_valid_after(datetime.now(timezone.utc) + timedelta(days=1))
        .sign(key, hashes.SHA256())
    )
    cert_pem = cert.public_bytes(serialization.Encoding.PEM)
    key_pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    return key_pem, cert_pem, cert


def _require_signxml() -> None:
    global _signxml_loaded, _signxml_unavailable, _signxml_etree, _signxml_XMLSigner
    if _signxml_unavailable:
        pytest.skip("signxml/XML stack not available (earlier import failed)")
    if _signxml_loaded:
        return
    try:
        from lxml import etree
        from signxml import XMLSigner

        _signxml_etree = etree
        _signxml_XMLSigner = XMLSigner
        _signxml_loaded = True
    except ImportError as exc:
        _signxml_unavailable = True
        pytest.skip(f"signxml extra not installed: {exc}")
    except SyntaxError as exc:
        _signxml_unavailable = True
        pytest.skip(f"lxml/signxml dependency chain invalid (e.g. stray PyPI rpython): {exc}")


def _signed_assertion_b64() -> tuple[str, str, str]:
    _require_signxml()
    assert _signxml_etree is not None and _signxml_XMLSigner is not None
    etree = _signxml_etree
    XMLSigner = _signxml_XMLSigner

    key_pem, cert_pem, cert = _self_signed_key_cert()
    xml = b"""<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_signed1" IssueInstant="2026-01-01T00:00:00Z" Version="2.0">
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <saml:Subject><saml:NameID>sig-user</saml:NameID></saml:Subject>
</saml:Assertion>"""
    root = etree.fromstring(xml)
    signed = XMLSigner().sign(root, key=key_pem, cert=cert_pem)
    raw = etree.tostring(signed)
    fp = sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
    return base64.b64encode(raw).decode("ascii"), cert_pem.decode("ascii"), fp


@pytest.mark.xwauth_unit
def test_parse_idp_metadata_xml_rejects_malformed_xml() -> None:
    auth = XWAuth(
        config=XWAuthConfig(
            jwt_secret="test-secret", allow_mock_storage_fallback=True
        )
    )
    manager = SAMLManager(auth)
    with pytest.raises(XWAuthError) as exc_info:
        manager.parse_idp_metadata_xml("<not-xml", source_url="https://idp.example.com/metadata")
    assert exc_info.value.error_code == "invalid_saml_metadata_xml"


@pytest.mark.xwauth_unit
def test_parse_idp_metadata_xml_extracts_fingerprints() -> None:
    auth = XWAuth(
        config=XWAuthConfig(
            jwt_secret="test-secret", allow_mock_storage_fallback=True
        )
    )
    manager = SAMLManager(auth)
    metadata_xml = """<?xml version="1.0"?>
<EntityDescriptor xmlns="urn:oasis:names:tc:SAML:2.0:metadata" entityID="https://idp.example.com" validUntil="2030-01-01T00:00:00Z">
  <IDPSSODescriptor protocolSupportEnumeration="urn:oasis:names:tc:SAML:2.0:protocol">
    <KeyDescriptor use="signing">
      <ds:KeyInfo xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
        <ds:X509Data>
          <ds:X509Certificate>QUJDREVGRw==</ds:X509Certificate>
        </ds:X509Data>
      </ds:KeyInfo>
    </KeyDescriptor>
  </IDPSSODescriptor>
</EntityDescriptor>
"""
    snapshot = manager.parse_idp_metadata_xml(metadata_xml, source_url="https://idp.example.com/metadata")
    assert snapshot.entity_id == "https://idp.example.com"
    assert snapshot.source_url == "https://idp.example.com/metadata"
    assert snapshot.valid_until == "2030-01-01T00:00:00Z"
    assert len(snapshot.signing_cert_fingerprints_sha256) == 1


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_strict_validation_requires_audience() -> None:
    config = XWAuthConfig(jwt_secret="test-secret", allow_mock_storage_fallback=True)
    setattr(config, "saml_strict_validation", True)
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)

    saml_xml = """<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_resp1" InResponseTo="_req1">
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_assert1">
    <saml:Subject>
      <saml:NameID>user-1</saml:NameID>
      <saml:SubjectConfirmation>
        <saml:SubjectConfirmationData Recipient="https://sp.example.com/acs" NotOnOrAfter="2030-01-01T00:00:00Z" InResponseTo="_req1"/>
      </saml:SubjectConfirmation>
    </saml:Subject>
  </saml:Assertion>
</samlp:Response>"""
    encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")

    with pytest.raises(XWAuthError) as exc_info:
        await manager.process_acs(encoded)
    assert exc_info.value.error_code == "saml_strict_validation_failed"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_strict_validation_audience_mismatch_when_entity_configured() -> None:
    config = XWAuthConfig(
        jwt_secret="test-secret",
        saml_strict_validation=True,
        saml_entity_id="https://expected-sp.example.com",
        allow_mock_storage_fallback=True,
    )
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    saml_xml = """<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_resp_aud" InResponseTo="_req_aud">
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_assert_aud">
    <saml:Subject>
      <saml:NameID>user-aud</saml:NameID>
      <saml:SubjectConfirmation>
        <saml:SubjectConfirmationData Recipient="https://sp.example.com/acs" NotOnOrAfter="2030-01-01T00:00:00Z" InResponseTo="_req_aud"/>
      </saml:SubjectConfirmation>
    </saml:Subject>
    <saml:Conditions>
      <saml:AudienceRestriction>
        <saml:Audience>https://other-sp.example.com</saml:Audience>
      </saml:AudienceRestriction>
    </saml:Conditions>
  </saml:Assertion>
</samlp:Response>"""
    encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")
    with pytest.raises(XWAuthError, match="audience mismatch"):
        await manager.process_acs(encoded)


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_strict_validation_rejects_expired_assertion() -> None:
    config = XWAuthConfig(
        jwt_secret="test-secret",
        saml_strict_validation=True,
        allow_mock_storage_fallback=True,
    )
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    saml_xml = """<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_resp_expired" InResponseTo="_req2">
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_assert_expired">
    <saml:Subject>
      <saml:NameID>user-2</saml:NameID>
      <saml:SubjectConfirmation>
        <saml:SubjectConfirmationData Recipient="https://sp.example.com/acs" NotOnOrAfter="2000-01-01T00:00:00Z" InResponseTo="_req2"/>
      </saml:SubjectConfirmation>
    </saml:Subject>
    <saml:Conditions>
      <saml:AudienceRestriction>
        <saml:Audience>https://sp.example.com</saml:Audience>
      </saml:AudienceRestriction>
    </saml:Conditions>
  </saml:Assertion>
</samlp:Response>"""
    encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")
    with pytest.raises(XWAuthError, match="assertion expired"):
        await manager.process_acs(encoded)


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_strict_validation_rejects_replay() -> None:
    config = XWAuthConfig(
        jwt_secret="test-secret",
        saml_strict_validation=True,
        allow_mock_storage_fallback=True,
    )
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    saml_xml = """<samlp:Response xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol" ID="_resp_replay" InResponseTo="_req3">
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>
  <saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_assert_replay">
    <saml:Subject>
      <saml:NameID>user-3</saml:NameID>
      <saml:SubjectConfirmation>
        <saml:SubjectConfirmationData Recipient="https://sp.example.com/acs" NotOnOrAfter="2030-01-01T00:00:00Z" InResponseTo="_req3"/>
      </saml:SubjectConfirmation>
    </saml:Subject>
    <saml:Conditions>
      <saml:AudienceRestriction>
        <saml:Audience>https://sp.example.com</saml:Audience>
      </saml:AudienceRestriction>
    </saml:Conditions>
  </saml:Assertion>
</samlp:Response>"""
    encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("utf-8")
    first = await manager.process_acs(encoded)
    assert first["user_id"] == "user-3"
    with pytest.raises(XWAuthError, match="replayed response id"):
        await manager.process_acs(encoded)


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_xml_signature_accepted_with_trusted_pem() -> None:
    _require_signxml()
    encoded, cert_pem, _ = _signed_assertion_b64()
    config = XWAuthConfig(jwt_secret="test-secret", saml_idp_signing_certificates_pem=[cert_pem], allow_mock_storage_fallback=True)
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    out = await manager.process_acs(encoded)
    assert out["user_id"] == "sig-user"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_xml_signature_accepted_with_pin_only() -> None:
    _require_signxml()
    encoded, _, fp = _signed_assertion_b64()
    config = XWAuthConfig(jwt_secret="test-secret", saml_idp_certificate_pins_sha256=[fp], allow_mock_storage_fallback=True)
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    out = await manager.process_acs(encoded)
    assert out["user_id"] == "sig-user"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_xml_signature_rejects_unsigned_when_trust_configured() -> None:
    _require_signxml()
    saml_xml = """<saml:Assertion xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion" ID="_u1" Version="2.0">
  <saml:Issuer>https://idp.example.com</saml:Issuer>
  <saml:Subject><saml:NameID>x</saml:NameID></saml:Subject>
</saml:Assertion>"""
    encoded = base64.b64encode(saml_xml.encode("utf-8")).decode("ascii")
    _, cert_pem, _ = _self_signed_key_cert()
    config = XWAuthConfig(
        jwt_secret="test-secret",
        saml_idp_signing_certificates_pem=[cert_pem.decode("ascii")],
        allow_mock_storage_fallback=True,
    )
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    with pytest.raises(XWAuthError) as ei:
        await manager.process_acs(encoded)
    assert ei.value.error_code == "saml_signature_missing"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_xml_signature_rejects_wrong_pem() -> None:
    _require_signxml()
    encoded, _, _ = _signed_assertion_b64()
    _, wrong_pem, _ = _self_signed_key_cert()
    config = XWAuthConfig(
        jwt_secret="test-secret",
        saml_idp_signing_certificates_pem=[wrong_pem.decode("ascii")],
        allow_mock_storage_fallback=True,
    )
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    with pytest.raises(XWAuthError) as ei:
        await manager.process_acs(encoded)
    assert ei.value.error_code == "saml_signature_invalid"


@pytest.mark.xwauth_unit
@pytest.mark.asyncio
async def test_process_acs_xml_signature_rejects_bad_pin() -> None:
    _require_signxml()
    encoded, _, _ = _signed_assertion_b64()
    bad = "a" * 64
    config = XWAuthConfig(jwt_secret="test-secret", saml_idp_certificate_pins_sha256=[bad], allow_mock_storage_fallback=True)
    auth = XWAuth(config=config)
    manager = SAMLManager(auth)
    with pytest.raises(XWAuthError) as ei:
        await manager.process_acs(encoded)
    assert ei.value.error_code == "saml_cert_pin_mismatch"

