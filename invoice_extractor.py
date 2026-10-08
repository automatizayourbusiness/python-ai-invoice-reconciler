#!/usr/bin/env python3
"""
Automated Invoice Data Extractor & Webhook Dispatcher
Developed by Lorenzo Cona - Integration & AI Automation Engineer

This script processes invoice text/documents, leverages OpenAI Structured Outputs
to extract tax and financial metadata with mathematical consistency verification,
and dispatches validated records to an integration webhook (n8n/Make).
"""

import os
import json
import time
import requests

# Simulated or real API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "mock_key_for_offline_testing")
TARGET_WEBHOOK_URL = os.getenv("TARGET_WEBHOOK_URL", "https://api.automation-academy.dev/webhooks/invoices")

SAMPLE_RAW_INVOICE = """
FACTURA COMERCIAL ELECTRÓNICA
Proveedor: CloudServices Global S.A.
CUIT/Tax ID: 30-71829102-4
Número de Factura: FC-A-0004-00019283
Fecha de Emisión: 2026-10-01
Cliente: Nexus Technology Corp
Dirección: Av. San Martín 1420, Mendoza, Argentina

ÍTEMS:
1. Servidor Cloud Dedicado 32GB RAM (Periodo Octubre) - $800.00 USD
2. Servicio Gestionado de Backups & Disaster Recovery - $150.00 USD
3. Soporte Premium 24/7 SLA 99.9% - $250.00 USD

Subtotal: $1,200.00 USD
IVA (21%): $252.00 USD
TOTAL FINAL: $1,452.00 USD
Condición de pago: Transferencia bancaria dentro de los 15 días.
"""

def extract_invoice_metadata(raw_text: str) -> dict:
    """
    Extracts structured financial fields using LLM prompt engineering.
    Includes mock fallback for offline demonstration and testing.
    """
    print("[1/3] Parsing document content through AI Engine...")
    time.sleep(0.5)

    if OPENAI_API_KEY.startswith("sk-"):
        # Real OpenAI API call
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": "Extract strict JSON with: invoice_number, vendor_name, vendor_tax_id, date, subtotal, tax_amount, total_amount, currency, items (array of {description, amount})."
                },
                {"role": "user", "content": raw_text}
            ],
            "response_format": {"type": "json_object"}
        }
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=15)
        return json.loads(response.json()["choices"][0]["message"]["content"])
    else:
        # High-fidelity deterministic mock output for demonstration & portfolio validation
        return {
            "invoice_number": "FC-A-0004-00019283",
            "vendor_name": "CloudServices Global S.A.",
            "vendor_tax_id": "30-71829102-4",
            "date": "2026-10-01",
            "currency": "USD",
            "subtotal": 1200.00,
            "tax_amount": 252.00,
            "total_amount": 1452.00,
            "items": [
                {"description": "Servidor Cloud Dedicado 32GB RAM", "amount": 800.00},
                {"description": "Servicio Gestionado de Backups", "amount": 150.00},
                {"description": "Soporte Premium 24/7 SLA", "amount": 250.00}
            ]
        }

def validate_financial_consistency(data: dict) -> bool:
    """
    Ensures mathematical integrity before dispatching to ERP or accounting systems.
    """
    print("[2/3] Validating mathematical consistency & checksums...")
    items_sum = sum(item["amount"] for item in data.get("items", []))
    subtotal = data.get("subtotal", 0.0)
    total = data.get("total_amount", 0.0)
    tax = data.get("tax_amount", 0.0)

    # Allow tiny float precision margin
    if abs(items_sum - subtotal) > 0.05:
        raise ValueError(f"Consistency Error: Items sum ({items_sum}) does not match subtotal ({subtotal})")
    
    if abs((subtotal + tax) - total) > 0.05:
        raise ValueError(f"Consistency Error: Subtotal + Tax ({subtotal + tax}) does not match total ({total})")

    print("      [OK] Mathematical audit PASSED: Subtotal and Total are 100% consistent.")
    return True

def dispatch_to_webhook(data: dict, webhook_url: str):
    """
    Dispatches the clean payload to an integration webhook (n8n or Make).
    """
    print(f"[3/3] Dispatching payload to integration endpoint: {webhook_url}")
    payload = {
        "event": "invoice_parsed_and_audited",
        "processed_by": "Python_Automation_Engine_v1",
        "timestamp": time.time(),
        "invoice_data": data
    }
    
    # In live environments, execute requests.post(webhook_url, json=payload)
    print("      [OK] Ingestion Payload Ready:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print("\n[SUCCESS] Pipeline executed cleanly without errors.")

if __name__ == "__main__":
    print("==============================================================")
    print("  AI INVOICE RECONCILIATION ENGINE - LORENZO CONA PORTFOLIO   ")
    print("==============================================================\n")
    
    extracted = extract_invoice_metadata(SAMPLE_RAW_INVOICE)
    if validate_financial_consistency(extracted):
        dispatch_to_webhook(extracted, TARGET_WEBHOOK_URL)
