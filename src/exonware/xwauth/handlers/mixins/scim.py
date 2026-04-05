"""SCIM and policy explain endpoints."""

from __future__ import annotations

from dataclasses import asdict
from uuid import uuid4
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse, Response

from exonware.xwaction import XWAction
from exonware.xwaction.defs import ActionProfile
from exonware.xwsystem.security.contracts import AuthContext

from exonware.xwauth.oauth_http.errors import oauth_error_to_http
from exonware.xwauth.ops_hooks import track_critical_handler
from .._common import (
    AUTHZ_TAGS,
    SCIM_TAGS,
    get_auth,
    get_bearer_token,
    get_scim_group_service,
    get_scim_user_service,
)
from ...scim import ScimPatchOperation


async def _resolve_auth_context_or_none(request: Request) -> AuthContext | None:
    token = get_bearer_token(request)
    if not token:
        return None
    auth = get_auth(request)
    return await auth.resolve_auth_context(token)


def _scim_unauthorized() -> JSONResponse:
    return JSONResponse(
        content={"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": "401", "detail": "Authentication required"},
        status_code=401,
    )

def _scim_error(status: int, detail: str) -> JSONResponse:
    return JSONResponse(
        content={"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": str(status), "detail": detail},
        status_code=status,
    )

def _etag_headers_from_resource(resource: Any) -> dict[str, str]:
    meta = getattr(resource, "meta", None)
    version = getattr(meta, "version", None) if meta is not None else None
    if isinstance(version, str) and version.strip():
        return {"ETag": version}
    return {}

def _scim_org_query_matches_token(request: Request, context: AuthContext) -> bool:
    """Optional org_id query param must match token org when the token is org-bound (tenant-safe SCIM)."""
    org_q = (request.query_params.get("org_id") or "").strip()
    if not org_q:
        return True
    token_org = context.org_id
    if token_org is None or not str(token_org).strip():
        return True
    return str(token_org).strip() == org_q


def _matches_if_match(if_match_header: str | None, current_etag: str | None) -> bool:
    if if_match_header is None or not if_match_header.strip():
        return True
    if current_etag is None:
        return False
    if_match = if_match_header.strip()
    return if_match == "*" or if_match == current_etag


def _extract_scim_query_paging(request: Request) -> tuple[str | None, int, int]:
    filter_expression = request.query_params.get("filter")
    try:
        start_index = int(request.query_params.get("startIndex", 1))
    except Exception:
        start_index = 1
    try:
        count = int(request.query_params.get("count", 100))
    except Exception:
        count = 100
    return filter_expression, start_index, count


@XWAction(
    operationId="policy_explain",
    summary="Explain Authorization Decision",
    method="POST",
    description="Return an explainable authorization decision trace for resource/action.",
    tags=AUTHZ_TAGS,
    engine="fastapi",
    profile=ActionProfile.ENDPOINT,
    security="Bearer",
    responses={200: {"description": "Decision and trace"}, 401: {"description": "Authentication required"}},
)
async def policy_explain(request: Request) -> Any:
    auth = get_auth(request)
    context = await _resolve_auth_context_or_none(request)
    body_data = await request.json() if hasattr(request, "json") else {}
    if context is None:
        raw_context = body_data.get("context")
        if isinstance(raw_context, dict):
            claims_map = dict(raw_context.get("claims") or {})
            org_fallback = raw_context.get("org_id") or raw_context.get("organization_id")
            proj_fallback = raw_context.get("project_id") or raw_context.get("application_id")
            context = AuthContext(
                subject_id=str(raw_context.get("subject_id") or raw_context.get("sub") or raw_context.get("user_id") or "anonymous"),
                tenant_id=raw_context.get("tenant_id"),
                org_id=org_fallback or claims_map.get("org_id") or claims_map.get("organization_id"),
                project_id=proj_fallback or claims_map.get("project_id") or claims_map.get("application_id"),
                scopes=list(raw_context.get("scopes") or []),
                roles=list(raw_context.get("roles") or []),
                claims=claims_map,
            )
    if context is None:
        return JSONResponse(
            content={"error": "unauthorized", "error_description": "Authentication required or context payload"},
            status_code=401,
        )
    resource = str(body_data.get("resource") or "").strip()
    action = str(body_data.get("action") or "").strip()
    if not resource or not action:
        return JSONResponse(
            content={"error": "invalid_request", "error_description": "resource and action are required"},
            status_code=400,
        )
    try:
        async with track_critical_handler(request, "policy_explain"):
            decision = auth.policy_decision_service.explain(
                context,
                resource=resource,
                action=action,
                org_id=body_data.get("org_id"),
                project_id=body_data.get("project_id"),
            )
            return {"allowed": decision.allowed, "trace": asdict(decision.trace)}
    except Exception as e:
        body, status = oauth_error_to_http(e)
        return JSONResponse(content=body, status_code=status)


@XWAction(
    operationId="scim_service_provider_config",
    summary="SCIM Service Provider Config",
    method="GET",
    description="Return SCIM service provider capabilities.",
    tags=SCIM_TAGS,
    engine="fastapi",
    profile=ActionProfile.ENDPOINT,
    security="Bearer",
    responses={200: {"description": "SCIM provider config"}, 401: {"description": "Authentication required"}},
)
async def scim_service_provider_config(request: Request) -> Any:
    if await _resolve_auth_context_or_none(request) is None:
        return _scim_unauthorized()
    async with track_critical_handler(request, "scim_service_provider_config"):
        return {
            "schemas": ["urn:ietf:params:scim:schemas:core:2.0:ServiceProviderConfig"],
            "patch": {"supported": True},
            "bulk": {"supported": False, "maxOperations": 0, "maxPayloadSize": 0},
            "filter": {"supported": True, "maxResults": 200},
            "changePassword": {"supported": True},
            "sort": {"supported": False},
            "etag": {"supported": True},
            "authenticationSchemes": [
                {
                    "name": "OAuth Bearer Token",
                    "description": "Authentication scheme using OAuth Bearer Token.",
                    "type": "oauthbearertoken",
                    "primary": True,
                }
            ],
        }


@XWAction(operationId="scim_users_list", summary="List SCIM Users", method="GET", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_users_list(request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_user_service(auth)
    try:
        async with track_critical_handler(request, "scim_users_list"):
            filter_expression, start_index, count = _extract_scim_query_paging(request)
            return service.list_response(filter_expression=filter_expression, start_index=start_index, count=count)
    except ValueError as exc:
        return _scim_error(400, str(exc))
    except Exception as e:
        body, status = oauth_error_to_http(e)
        return JSONResponse(content=body, status_code=status)


@XWAction(operationId="scim_users_create", summary="Create SCIM User", method="POST", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_users_create(request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_user_service(auth)
    body_data = await request.json() if hasattr(request, "json") else {}
    resource_id = str(body_data.get("id") or uuid4())
    attributes = {k: v for k, v in body_data.items() if k not in {"schemas", "id", "externalId", "meta"}}
    try:
        async with track_critical_handler(request, "scim_users_create"):
            created = service.create(resource_id=resource_id, attributes=attributes, external_id=body_data.get("externalId"))
            return JSONResponse(content=created.to_dict(), status_code=201, headers=_etag_headers_from_resource(created))
    except ValueError as exc:
        return JSONResponse(
            content={"schemas": ["urn:ietf:params:scim:api:messages:2.0:Error"], "status": "409", "detail": str(exc)},
            status_code=409,
        )
    except Exception as e:
        body, status = oauth_error_to_http(e)
        return JSONResponse(content=body, status_code=status)


@XWAction(operationId="scim_users_get", summary="Get SCIM User", method="GET", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_users_get(resource_id: str, request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_user_service(auth)
    async with track_critical_handler(request, "scim_users_get"):
        found = service.get(resource_id)
        if found is None:
            return _scim_error(404, "Resource not found")
        return JSONResponse(content=found.to_dict(), headers=_etag_headers_from_resource(found))


@XWAction(operationId="scim_users_patch", summary="Patch SCIM User", method="PATCH", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_users_patch(resource_id: str, request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_user_service(auth)
    existing = service.get(resource_id)
    if existing is None:
        return _scim_error(404, "Resource not found")
    current_etag = getattr(getattr(existing, "meta", None), "version", None)
    if_match = request.headers.get("if-match")
    if not _matches_if_match(if_match, current_etag):
        return _scim_error(412, "If-Match precondition failed")

    body_data = await request.json() if hasattr(request, "json") else {}
    schemas = body_data.get("schemas")
    if schemas is not None:
        required_schema = "urn:ietf:params:scim:api:messages:2.0:PatchOp"
        if not isinstance(schemas, list) or required_schema not in schemas:
            return _scim_error(400, "SCIM PATCH requires PatchOp schema")
    raw_operations = body_data.get("Operations") or []
    operations: list[ScimPatchOperation] = []
    if not isinstance(raw_operations, list):
        return _scim_error(400, "Operations must be an array")
    for operation in raw_operations:
        if not isinstance(operation, dict):
            return _scim_error(400, "Each operation must be an object")
        operations.append(
            ScimPatchOperation(
                op=str(operation.get("op") or ""),
                path=operation.get("path"),
                value=operation.get("value"),
            )
        )
    try:
        async with track_critical_handler(request, "scim_users_patch"):
            updated = service.patch(resource_id=resource_id, operations=operations)
            return JSONResponse(content=updated.to_dict(), headers=_etag_headers_from_resource(updated))
    except KeyError:
        return _scim_error(404, "Resource not found")
    except ValueError as exc:
        return _scim_error(400, str(exc))
    except Exception as e:
        body, status = oauth_error_to_http(e)
        return JSONResponse(content=body, status_code=status)


@XWAction(operationId="scim_users_delete", summary="Delete SCIM User", method="DELETE", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_users_delete(resource_id: str, request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_user_service(auth)
    existing = service.get(resource_id)
    if existing is None:
        return _scim_error(404, "Resource not found")
    current_etag = getattr(getattr(existing, "meta", None), "version", None)
    if_match = request.headers.get("if-match")
    if not _matches_if_match(if_match, current_etag):
        return _scim_error(412, "If-Match precondition failed")
    async with track_critical_handler(request, "scim_users_delete"):
        if not service.delete(resource_id):
            return _scim_error(404, "Resource not found")
        return Response(status_code=204)


@XWAction(operationId="scim_groups_list", summary="List SCIM Groups", method="GET", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_groups_list(request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_group_service(auth)
    try:
        async with track_critical_handler(request, "scim_groups_list"):
            filter_expression, start_index, count = _extract_scim_query_paging(request)
            return service.list_response(filter_expression=filter_expression, start_index=start_index, count=count)
    except ValueError as exc:
        return _scim_error(400, str(exc))
    except Exception as e:
        body, status = oauth_error_to_http(e)
        return JSONResponse(content=body, status_code=status)


@XWAction(operationId="scim_groups_create", summary="Create SCIM Group", method="POST", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_groups_create(request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_group_service(auth)
    body_data = await request.json() if hasattr(request, "json") else {}
    resource_id = str(body_data.get("id") or uuid4())
    attributes = {k: v for k, v in body_data.items() if k not in {"schemas", "id", "externalId", "meta"}}
    try:
        async with track_critical_handler(request, "scim_groups_create"):
            created = service.create(resource_id=resource_id, attributes=attributes, external_id=body_data.get("externalId"))
            return JSONResponse(content=created.to_dict(), status_code=201, headers=_etag_headers_from_resource(created))
    except ValueError as exc:
        return _scim_error(409, str(exc))
    except Exception as e:
        body, status = oauth_error_to_http(e)
        return JSONResponse(content=body, status_code=status)


@XWAction(operationId="scim_groups_get", summary="Get SCIM Group", method="GET", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_groups_get(resource_id: str, request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_group_service(auth)
    async with track_critical_handler(request, "scim_groups_get"):
        found = service.get(resource_id)
        if found is None:
            return _scim_error(404, "Resource not found")
        return JSONResponse(content=found.to_dict(), headers=_etag_headers_from_resource(found))


@XWAction(operationId="scim_groups_patch", summary="Patch SCIM Group", method="PATCH", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_groups_patch(resource_id: str, request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_group_service(auth)
    existing = service.get(resource_id)
    if existing is None:
        return _scim_error(404, "Resource not found")
    current_etag = getattr(getattr(existing, "meta", None), "version", None)
    if_match = request.headers.get("if-match")
    if not _matches_if_match(if_match, current_etag):
        return _scim_error(412, "If-Match precondition failed")

    body_data = await request.json() if hasattr(request, "json") else {}
    raw_operations = body_data.get("Operations") or []
    if not isinstance(raw_operations, list):
        return _scim_error(400, "Operations must be an array")
    operations = [
        ScimPatchOperation(op=str(operation.get("op") or ""), path=operation.get("path"), value=operation.get("value"))
        for operation in raw_operations
        if isinstance(operation, dict)
    ]
    if len(operations) != len(raw_operations):
        return _scim_error(400, "Each operation must be an object")
    try:
        async with track_critical_handler(request, "scim_groups_patch"):
            updated = service.patch(resource_id=resource_id, operations=operations)
            return JSONResponse(content=updated.to_dict(), headers=_etag_headers_from_resource(updated))
    except ValueError as exc:
        return _scim_error(400, str(exc))


@XWAction(operationId="scim_groups_delete", summary="Delete SCIM Group", method="DELETE", tags=SCIM_TAGS, engine="fastapi", profile=ActionProfile.ENDPOINT)
async def scim_groups_delete(resource_id: str, request: Request) -> Any:
    ctx = await _resolve_auth_context_or_none(request)
    if ctx is None:
        return _scim_unauthorized()
    if not _scim_org_query_matches_token(request, ctx):
        return _scim_error(403, "org_id query does not match token organization context")
    auth = get_auth(request)
    service = get_scim_group_service(auth)
    existing = service.get(resource_id)
    if existing is None:
        return _scim_error(404, "Resource not found")
    current_etag = getattr(getattr(existing, "meta", None), "version", None)
    if_match = request.headers.get("if-match")
    if not _matches_if_match(if_match, current_etag):
        return _scim_error(412, "If-Match precondition failed")
    async with track_critical_handler(request, "scim_groups_delete"):
        if not service.delete(resource_id):
            return _scim_error(404, "Resource not found")
        return Response(status_code=204)
