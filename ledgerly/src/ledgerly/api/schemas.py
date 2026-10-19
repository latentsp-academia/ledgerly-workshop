"""Request/response models for the HTTP API."""

from __future__ import annotations

from pydantic import BaseModel, Field


class LineIn(BaseModel):
    description: str
    quantity: int = Field(gt=0)
    unit_cents: int = Field(ge=0)


class InvoiceIn(BaseModel):
    customer: str
    currency: str
    lines: list[LineIn]
    vat_rate_bp: int = 1_700


class InvoiceOut(BaseModel):
    id: int
    number: str
    customer: str
    currency: str
    status: str
    net_cents: int
    vat_cents: int
    total_cents: int
    captured_cents: int


class RefundOut(BaseModel):
    invoice_id: int
    refunded_cents: int
    currency: str
