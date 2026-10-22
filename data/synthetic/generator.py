import json
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any


def generate_rj_kitchen_fixtures(seed: int = 42) -> Dict[str, Any]:
    random.seed(seed)
    
    # Base reference date: October 20, 2026
    now = datetime(2026, 10, 20, 14, 0, 0, tzinfo=timezone.utc)
    
    merchant = {
        "id": "mer_rjkitchen_01",
        "name": "RJ Kitchen - Cyber Hub",
        "legal_entity_name": "RJ Gourmet Foods Pvt. Ltd.",
        "default_currency": "INR",
        "timezone": "Asia/Kolkata",
        "created_at": (now - timedelta(days=180)).isoformat(),
        "updated_at": now.isoformat()
    }
    
    users = [
        {
            "id": "usr_rohit_01",
            "merchant_id": merchant["id"],
            "email": "rohit.jain@rjkitchen.in",
            "name": "Rohit Jain",
            "role": "admin",
            "is_active": True,
            "created_at": (now - timedelta(days=180)).isoformat()
        },
        {
            "id": "usr_priya_02",
            "merchant_id": merchant["id"],
            "email": "priya.sharma@rjkitchen.in",
            "name": "Priya Sharma",
            "role": "risk_analyst",
            "is_active": True,
            "created_at": (now - timedelta(days=120)).isoformat()
        }
    ]
    
    menu_items = [
        {"name": "Butter Chicken Gourmet Bowl", "price": 42900},
        {"name": "Paneer Tikka Biryani Feast", "price": 38900},
        {"name": "Dal Makhani & Garlic Naan Combo", "price": 32900},
        {"name": "Truffle Mushroom Risotto", "price": 49900},
        {"name": "Artisanal Gulab Jamun (4 pcs)", "price": 18900},
        {"name": "Mango Lassi Jar", "price": 14900},
        {"name": "Kashmiri Mutton Rogan Josh Bowl", "price": 54900},
        {"name": "Classic Chicken Dum Biryani (Family Pack)", "price": 89900},
    ]
    
    customer_names = [
        ("Aarav Mehta", "aarav.m@example.com", "+919820112233"),
        ("Sneha Iyer", "sneha.iyer@example.com", "+919830223344"),
        ("Vikram Malhotra", "vikram.m@example.com", "+919840334455"),
        ("Ananya Deshmukh", "ananya.d@example.com", "+919850445566"),
        ("Kabir Verma", "kabir.v@example.com", "+919860556677"),
        ("Rohan Khanna", "rohan.k@example.com", "+919870667788"),
        ("Meera Sen", "meera.sen@example.com", "+919880778899"),
        ("Aditya Nair", "aditya.n@example.com", "+919890889900"),
        ("Tanvi Bhatia", "tanvi.b@example.com", "+919810990011"),
        ("Ishaan Gupta", "ishaan.g@example.com", "+919821001122"),
        ("Dia Kapoor", "dia.k@example.com", "+919832112233"),
        ("Kunal Singhania", "kunal.s@example.com", "+919843223344"),
        ("Pooja Hegde", "pooja.h@example.com", "+919854334455"),
        ("Rahul Dravid", "rahul.d@example.com", "+919865445566"),
        ("Simran Kaur", "simran.k@example.com", "+919876556677"),
    ]
    
    categories = [
        {"code": "product_not_received", "name": "Product Not Received", "count": 15},
        {"code": "cancelled_charge", "name": "Order Cancelled But Charged", "count": 10},
        {"code": "fraud_unauthorized", "name": "Fraud / Unauthorized Charge", "count": 10},
        {"code": "not_as_described", "name": "Product Not As Described", "count": 10},
        {"code": "duplicate_charge", "name": "Duplicate Charge Claim", "count": 5},
    ]
    
    customers = []
    orders = []
    payments = []
    fulfilments = []
    messages = []
    disputes = []
    evidence_items = []
    evidence_links = []
    ai_investigations = []
    response_drafts = []
    scoring_results = []
    dispute_outcomes = []
    
    dispute_counter = 1000
    
    for cat in categories:
        cat_code = cat["code"]
        count = cat["count"]
        
        for i in range(count):
            dispute_counter += 1
            idx_str = str(dispute_counter)
            
            # Select customer
            c_name, c_email, c_phone = customer_names[(dispute_counter) % len(customer_names)]
            cust_id = f"cust_synth_{idx_str}"
            cust = {
                "id": cust_id,
                "merchant_id": merchant["id"],
                "name": c_name,
                "email": c_email,
                "phone": c_phone,
                "is_synthetic": True,
                "created_at": (now - timedelta(days=random.randint(10, 90))).isoformat()
            }
            customers.append(cust)
            
            # Order items & pricing
            num_items = random.randint(1, 3)
            selected_items = random.sample(menu_items, num_items)
            order_total = sum(item["price"] for item in selected_items)
            order_time = now - timedelta(days=random.randint(2, 28), hours=random.randint(1, 12))
            
            order_id = f"order_synth_{idx_str}"
            order = {
                "id": order_id,
                "merchant_id": merchant["id"],
                "customer_id": cust_id,
                "order_number": f"RJK-{idx_str}",
                "amount": order_total,
                "currency": "INR",
                "status": "fulfilled",
                "item_summary": {"items": selected_items, "subtotal": order_total, "tax": int(order_total * 0.05)},
                "ordered_at": order_time.isoformat(),
                "cancelled_at": None,
                "cancellation_reason": None
            }
            
            # Payment record
            pay_id = f"pay_synth_{idx_str}"
            pay_method = random.choice(["upi", "card", "card", "netbanking"])
            card_last4 = str(random.randint(1000, 9999)) if pay_method == "card" else None
            card_net = random.choice(["Visa", "MasterCard", "RuPay"]) if pay_method == "card" else None
            upi_vpa = f"{c_name.lower().replace(' ', '')}@oksbi" if pay_method == "upi" else None
            
            payment = {
                "id": pay_id,
                "merchant_id": merchant["id"],
                "order_id": order_id,
                "provider": "mock",
                "gateway_payment_id": f"pay_gateway_{idx_str}",
                "amount": order_total,
                "currency": "INR",
                "method": pay_method,
                "card_network": card_net,
                "card_last4": card_last4,
                "bank_name": "HDFC Bank" if pay_method == "netbanking" else None,
                "upi_vpa": upi_vpa,
                "status": "captured",
                "captured_at": (order_time + timedelta(minutes=2)).isoformat(),
                "refund_status": None,
                "amount_refunded": 0,
                "is_synthetic": True
            }
            
            # Fulfilment
            fulfil_id = f"ful_{idx_str}"
            del_time = order_time + timedelta(minutes=random.randint(25, 45))
            proof_type = random.choice(["otp_verified", "signature", "photo", "geo_fence_ping"])
            otp = str(random.randint(1000, 9999)) if proof_type == "otp_verified" else None
            
            fulfilment = {
                "id": fulfil_id,
                "order_id": order_id,
                "carrier": random.choice(["Dunzo Express", "Shadowfax Fleet", "RJ Direct Rider"]),
                "tracking_number": f"TRK-{random.randint(100000, 999999)}",
                "status": "delivered",
                "dispatch_at": (order_time + timedelta(minutes=15)).isoformat(),
                "delivered_at": del_time.isoformat(),
                "delivery_proof_type": proof_type,
                "delivery_otp_entered": otp,
                "delivery_address": f"Flat {random.randint(101, 804)}, Tower {random.choice(['A','B','C'])}, DLF Phase {random.randint(1,5)}, Gurugram, Haryana",
                "recipient_name": c_name,
                "notes": "Delivered to customer doorstep."
            }
            
            # Dispute status & dates
            # 60% open/under_review/evidence_ready, 40% won/lost
            is_closed = (i % 3 == 0)
            disp_status = random.choice(["won", "lost"]) if is_closed else random.choice(["open", "under_review", "evidence_ready"])
            created_at = order_time + timedelta(days=random.randint(1, 5))
            deadline = created_at + timedelta(days=7)
            
            # Specific edge cases setup
            contradiction_cases = []
            facts_list = []
            msg_list = []
            evi_list = []
            
            # Category-specific narrative injection
            if cat_code == "product_not_received":
                reason_desc = "Customer claims food package was never delivered by courier."
                # Edge case 1: Customer confirmed receipt in chat
                if i % 3 == 1:
                    msg = {
                        "id": f"msg_{idx_str}_1",
                        "dispute_id": f"disp_synth_{idx_str}",
                        "order_id": order_id,
                        "customer_id": cust_id,
                        "direction": "inbound",
                        "channel": "chat",
                        "sender_name": c_name,
                        "content": "Thanks, received the Butter Chicken warm! Delicious as always.",
                        "sent_at": (del_time + timedelta(minutes=10)).isoformat()
                    }
                    messages.append(msg)
                    contradiction_cases.append({
                        "code": "RECEIPT_CONFIRMED_IN_CHAT",
                        "severity": "high",
                        "title": "Customer Explicitly Confirmed Receipt in Chat",
                        "description": f"Customer sent inbound message confirming order delivery at {(del_time + timedelta(minutes=10)).strftime('%H:%M UTC')}, but later filed non-delivery dispute.",
                        "conflicting_records": [f"msg_{idx_str}_1", f"disp_synth_{idx_str}"]
                    })
                # Edge case 2: Timestamp conflict between courier and kitchen
                elif i % 3 == 2:
                    fulfilment["delivered_at"] = (order_time - timedelta(minutes=10)).isoformat() # Del timestamp earlier than order
                    contradiction_cases.append({
                        "code": "FULFILMENT_PREDATES_ORDER",
                        "severity": "high",
                        "title": "Delivery Timestamp Inconsistent With Order Placement",
                        "description": "Courier API logged delivery status 10 minutes prior to order checkout timestamp. Possible courier sync latency or clock drift.",
                        "conflicting_records": [order_id, fulfil_id]
                    })
                
                # Evidence: Delivery proof
                evi_pod = {
                    "id": f"evi_{idx_str}_pod",
                    "merchant_id": merchant["id"],
                    "evidence_type": "delivery_proof",
                    "title": f"Proof of Delivery - {fulfilment['carrier']}",
                    "description": f"Courier delivery confirmation with proof type {proof_type} at {fulfilment['delivery_address']}.",
                    "file_path": f"/uploads/pod_{idx_str}.pdf",
                    "file_name": f"pod_{idx_str}.pdf",
                    "file_size_bytes": 142800,
                    "mime_type": "application/pdf",
                    "sha256_hash": f"e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
                    "verification_status": "verified" if proof_type in ["otp_verified", "signature"] else "pending_review",
                    "source": "logistics_api",
                    "created_at": del_time.isoformat()
                }
                evidence_items.append(evi_pod)
                evi_list.append(evi_pod["id"])
                
            elif cat_code == "cancelled_charge":
                reason_desc = "Customer cancelled order after placement but states payment was not refunded."
                # Cancellation simulation
                cancel_time = order_time + timedelta(minutes=random.randint(5, 20))
                order["status"] = "cancelled"
                order["cancelled_at"] = cancel_time.isoformat()
                order["cancellation_reason"] = "Customer changed mind before kitchen prep"
                
                # Edge case: Refund initiated or pending
                if i % 2 == 0:
                    payment["refund_status"] = "processed"
                    payment["amount_refunded"] = order_total
                    facts_list.append({
                        "claim": f"Gateway refund of INR {order_total/100:.2f} was already processed successfully on {cancel_time.strftime('%Y-%m-%d')}.",
                        "source_type": "payment",
                        "source_id": pay_id,
                        "verified": True
                    })
                else:
                    payment["refund_status"] = "failed"
                    contradiction_cases.append({
                        "code": "REFUND_GATEWAY_PENDING",
                        "severity": "medium",
                        "title": "Refund Initiated But Unconfirmed by Bank",
                        "description": "Internal merchant records show refund initiated upon cancellation, but acquiring gateway failed to complete ledger reversal.",
                        "conflicting_records": [pay_id, order_id]
                    })
                
                # Evidence: Policy & Refund Receipt
                evi_pol = {
                    "id": f"evi_{idx_str}_pol",
                    "merchant_id": merchant["id"],
                    "evidence_type": "cancellation_policy",
                    "title": "RJ Kitchen Cancellation & Refund Terms (v2026.1)",
                    "description": "Standard terms specifying full refund for cancellations prior to order dispatch.",
                    "file_path": f"/uploads/policy_{idx_str}.pdf",
                    "file_name": f"policy_{idx_str}.pdf",
                    "file_size_bytes": 98200,
                    "mime_type": "application/pdf",
                    "sha256_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
                    "verification_status": "verified",
                    "source": "pos_system",
                    "created_at": merchant["created_at"]
                }
                evidence_items.append(evi_pol)
                evi_list.append(evi_pol["id"])
                
            elif cat_code == "fraud_unauthorized":
                reason_desc = "Cardholder disputes charge as unauthorized / fraudulent card usage."
                # 3DS authentication logs
                auth_success = (i % 2 == 0)
                facts_list.append({
                    "claim": f"Transaction completed via {'3D-Secure 2.2 SMS OTP' if auth_success else 'UPI PIN authorization'} from registered device IP.",
                    "source_type": "payment",
                    "source_id": pay_id,
                    "verified": auth_success
                })
                
                evi_auth = {
                    "id": f"evi_{idx_str}_auth",
                    "merchant_id": merchant["id"],
                    "evidence_type": "ip_geo_log",
                    "title": "Gateway 2-Factor Authentication Audit Trail",
                    "description": f"Risk assessment audit: 3DS authenticated, Device IP matches Gurugram residential ISP, 0 prior chargebacks on customer profile.",
                    "file_path": f"/uploads/auth_log_{idx_str}.pdf",
                    "file_name": f"auth_log_{idx_str}.pdf",
                    "file_size_bytes": 112000,
                    "mime_type": "application/pdf",
                    "sha256_hash": "f0e1d2c3b4a5968778695a4b3c2d1e0f0e1d2c3b4a5968778695a4b3c2d1e0f",
                    "verification_status": "verified" if auth_success else "pending_review",
                    "source": "payment_gateway",
                    "created_at": order_time.isoformat()
                }
                evidence_items.append(evi_auth)
                evi_list.append(evi_auth["id"])
                
            elif cat_code == "not_as_described":
                reason_desc = "Customer states meal items were incorrect or portions differed from menu description."
                msg = {
                    "id": f"msg_{idx_str}_nad",
                    "dispute_id": f"disp_synth_{idx_str}",
                    "order_id": order_id,
                    "customer_id": cust_id,
                    "direction": "inbound",
                    "channel": "chat",
                    "sender_name": c_name,
                    "content": "I ordered Butter Chicken but received vegetarian Dal Makhani combo instead.",
                    "sent_at": (del_time + timedelta(minutes=25)).isoformat()
                }
                messages.append(msg)
                
                evi_inv = {
                    "id": f"evi_{idx_str}_inv",
                    "merchant_id": merchant["id"],
                    "evidence_type": "order_invoice",
                    "title": f"Kitchen POS Order Slip & KOT #{idx_str}",
                    "description": "Itemized Kitchen Order Ticket with kitchen preparation checklist and sealed packaging sticker verified.",
                    "file_path": f"/uploads/kot_{idx_str}.pdf",
                    "file_name": f"kot_{idx_str}.pdf",
                    "file_size_bytes": 84500,
                    "mime_type": "application/pdf",
                    "sha256_hash": "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef",
                    "verification_status": "verified",
                    "source": "pos_system",
                    "created_at": order_time.isoformat()
                }
                evidence_items.append(evi_inv)
                evi_list.append(evi_inv["id"])
                
            else: # duplicate_charge
                reason_desc = "Cardholder claims card was debited multiple times for a single order."
                # Duplicate check
                evi_dup = {
                    "id": f"evi_{idx_str}_dup",
                    "merchant_id": merchant["id"],
                    "evidence_type": "duplicate_audit_log",
                    "title": "Merchant Settlement Ledger Audit",
                    "description": f"Ledger audit confirms only single payment capture ({pay_id}) recorded for Order RJK-{idx_str}. No parallel authorization exists.",
                    "file_path": f"/uploads/dup_ledger_{idx_str}.pdf",
                    "file_name": f"dup_ledger_{idx_str}.pdf",
                    "file_size_bytes": 105400,
                    "mime_type": "application/pdf",
                    "sha256_hash": "deadbeefcafebabe0123456789abcdefdeadbeefcafebabe0123456789abcdef",
                    "verification_status": "verified",
                    "source": "pos_system",
                    "created_at": order_time.isoformat()
                }
                evidence_items.append(evi_dup)
                evi_list.append(evi_dup["id"])
            
            # Universal Evidence: Tax Invoice
            evi_tax = {
                "id": f"evi_{idx_str}_tax",
                "merchant_id": merchant["id"],
                "evidence_type": "order_invoice",
                "title": f"GST Tax Invoice RJK-INV-{idx_str}",
                "description": f"Official GST Tax Invoice showing billed amount INR {order_total/100:.2f} with customer address and GSTIN.",
                "file_path": f"/uploads/tax_inv_{idx_str}.pdf",
                "file_name": f"tax_inv_{idx_str}.pdf",
                "file_size_bytes": 164000,
                "mime_type": "application/pdf",
                "sha256_hash": "fedcba9876543210fedcba9876543210fedcba9876543210fedcba9876543210",
                "verification_status": "verified",
                "source": "pos_system",
                "created_at": order_time.isoformat()
            }
            evidence_items.append(evi_tax)
            evi_list.append(evi_tax["id"])
            
            # Calculate evidence completeness percentage
            completeness = 80.0 if len(evi_list) >= 2 and not contradiction_cases else (45.0 if contradiction_cases else 65.0)
            
            # Score estimation (logistic regression baseline simulation)
            base_score = 75.0 if len(evi_list) >= 2 else 45.0
            if contradiction_cases:
                base_score -= 25.0
            if proof_type in ["otp_verified", "signature"]:
                base_score += 15.0
            if cat_code == "fraud_unauthorized" and pay_method == "card":
                base_score -= 10.0
            win_score = max(5.0, min(95.0, base_score + random.uniform(-4.0, 4.0)))
            
            tier = "very_high" if win_score >= 80 else ("high" if win_score >= 65 else ("medium" if win_score >= 45 else "low"))
            readiness = "ready_to_submit" if completeness >= 75 and not contradiction_cases else ("contradictions_detected" if contradiction_cases else "gathering")
            
            disp_id = f"disp_synth_{idx_str}"
            dispute = {
                "id": disp_id,
                "merchant_id": merchant["id"],
                "payment_id": pay_id,
                "order_id": order_id,
                "customer_id": cust_id,
                "gateway_dispute_id": f"disp_gw_{idx_str}",
                "provider": "mock",
                "amount": order_total,
                "currency": "INR",
                "reason_code": cat_code,
                "reason_description": reason_desc,
                "status": disp_status,
                "phase": "chargeback",
                "evidence_readiness": readiness,
                "evidence_completeness_pct": round(completeness, 1),
                "win_probability_score": round(win_score, 1),
                "win_score_tier": tier,
                "response_deadline": deadline.isoformat(),
                "contested_at": (created_at + timedelta(days=2)).isoformat() if disp_status in ["contested", "won", "lost"] else None,
                "closed_at": (created_at + timedelta(days=6)).isoformat() if is_closed else None,
                "is_synthetic": True,
                "created_at": created_at.isoformat(),
                "updated_at": (created_at + timedelta(days=1)).isoformat()
            }
            disputes.append(dispute)
            
            # Evidence links
            for evi_id in evi_list:
                evidence_links.append({
                    "id": f"link_{idx_str}_{evi_id}",
                    "dispute_id": disp_id,
                    "evidence_id": evi_id,
                    "linked_by": "usr_priya_02",
                    "relevance_note": f"Auto-attached for dispute category {cat_code}.",
                    "linked_at": created_at.isoformat()
                })
            
            # AI Investigation record
            checklist_items = [
                {"code": "DELIVERY_PROOF", "label": "Courier delivery verification", "is_mandatory": True, "status": "fulfilled" if proof_type != "none" else "missing"},
                {"code": "TAX_INVOICE", "label": "Itemized Tax Invoice with GSTIN", "is_mandatory": True, "status": "fulfilled"},
                {"code": "COMMUNICATION_LOG", "label": "Customer chat & support records", "is_mandatory": False, "status": "fulfilled" if messages else "missing"},
            ]
            
            ai_inv = {
                "id": f"inv_{idx_str}",
                "dispute_id": disp_id,
                "investigation_status": "completed",
                "normalized_reason": cat_code,
                "findings_summary": f"Investigation for {cat['name']} (Order RJK-{idx_str}). Order amount INR {order_total/100:.2f}. Evidence completeness {completeness:.0f}%. Found {len(contradiction_cases)} conflicting temporal or factual items.",
                "checklist_audit": {"items": checklist_items, "summary": f"{sum(1 for c in checklist_items if c['status']=='fulfilled')}/{len(checklist_items)} criteria satisfied."},
                "contradictions": contradiction_cases,
                "facts_extracted": facts_list or [{"claim": f"Order #{idx_str} successfully completed via {fulfilment['carrier']}.", "source_type": "fulfilment", "source_id": fulfil_id, "verified": True}],
                "model_provider": "deterministic_fallback",
                "model_version": "v1.2",
                "execution_duration_ms": random.randint(420, 890),
                "created_at": created_at.isoformat(),
                "updated_at": created_at.isoformat()
            }
            ai_investigations.append(ai_inv)
            
            # Response Draft (Strictly <= 1000 characters for Razorpay contest summary)
            contest_summary = (
                f"Contesting dispute {disp_id} for Order RJK-{idx_str} (INR {order_total/100:.2f}). "
                f"Merchant RJ Kitchen fulfilled this order on {order_time.strftime('%Y-%m-%d')} via {fulfilment['carrier']} "
                f"(Tracking: {fulfilment['tracking_number']}). Delivery proof type: {proof_type.upper()}. "
                f"Goods were delivered to registered destination: {fulfilment['delivery_address']}. "
                f"Itemized GST invoice and courier verification logs attached. "
                f"Customer claim of {cat['name'].lower()} is inconsistent with verified courier telematics and system logs. "
                f"Kindly reverse the provisional debit in merchant favor."
            )
            # Ensure strict length limit
            if len(contest_summary) > 990:
                contest_summary = contest_summary[:990]
            
            letter = (
                f"FORMAL REPRESENTATION AND REBUTTAL\n\n"
                f"To: Dispute Operations / Card Scheme Arbitration Committee\n"
                f"Merchant: RJ Kitchen (RJ Gourmet Foods Pvt. Ltd.)\n"
                f"Dispute Reference: {disp_id} | Order Reference: RJK-{idx_str}\n"
                f"Transaction Amount: INR {order_total/100:.2f} | Payment ID: {pay_id}\n\n"
                f"1. TRANSACTION BACKGROUND\n"
                f"On {order_time.strftime('%B %d, %Y at %H:%M UTC')}, customer {c_name} placed order #{idx_str} through RJ Kitchen's online ordering portal. "
                f"Payment was successfully captured through {pay_method.upper()} with gateway authentication.\n\n"
                f"2. FULFILMENT & EVIDENCE SUMMARY\n"
                f"The order was prepared and handed over to logistics partner {fulfilment['carrier']}. "
                f"Delivery was confirmed at {fulfilment['delivered_at']} using {proof_type.replace('_', ' ').title()}.\n"
                f"Attached documents:\n"
                f"- Exhibit A: Courier Proof of Delivery\n"
                f"- Exhibit B: GST Tax Invoice and KOT Preparation Record\n\n"
                f"3. CONCLUSION\n"
                f"Merchant has fully complied with all delivery and billing commitments. We respectfully request dismissal of this chargeback."
            )
            
            draft = {
                "id": f"draft_{idx_str}",
                "dispute_id": disp_id,
                "contest_summary": contest_summary,
                "representation_letter": letter,
                "cited_evidence_ids": evi_list,
                "version": 1,
                "is_approved": is_closed,
                "approved_by": "usr_rohit_01" if is_closed else None,
                "last_edited_by": "usr_priya_02",
                "created_at": (created_at + timedelta(hours=1)).isoformat(),
                "updated_at": (created_at + timedelta(hours=1)).isoformat()
            }
            response_drafts.append(draft)
            
            # Scoring Result
            pos_factors = [
                {"feature_name": "f_delivery_otp_verified", "description": "Delivery verified with OTP or signature proof", "weight": 0.42, "impact_points": 18.5},
                {"feature_name": "f_evidence_completeness", "description": f"Evidence checklist completeness ({completeness:.0f}%)", "weight": 0.35, "impact_points": 15.2}
            ]
            neg_factors = []
            if contradiction_cases:
                neg_factors.append({
                    "feature_name": "f_contradiction_count",
                    "description": f"Detected {len(contradiction_cases)} temporal or factual contradiction(s)",
                    "weight": -0.65,
                    "impact_points": -22.0
                })
            
            scoring = {
                "id": f"score_{idx_str}",
                "dispute_id": disp_id,
                "score": round(win_score, 1),
                "tier": tier,
                "model_name": "LogisticRegression_Baseline_v1",
                "model_version": "1.0.0",
                "top_positive_factors": pos_factors,
                "top_negative_factors": neg_factors,
                "missing_information_penalties": [{"feature_name": "f_geofence_ping", "description": "Courier geofence GPS coordinates not attached", "weight": -0.15, "impact_points": -6.0}],
                "feature_vector": {
                    "f_evidence_completeness": completeness / 100.0,
                    "f_delivery_otp_verified": 1 if proof_type in ["otp_verified", "signature"] else 0,
                    "f_contradiction_count": len(contradiction_cases),
                    "f_amount_paise": order_total,
                    "f_reason_code": cat_code
                },
                "is_calibrated": True,
                "calibration_note": "Calibrated with Platt scaling against historical synthetic disputes baseline.",
                "evaluated_at": created_at.isoformat()
            }
            scoring_results.append(scoring)
            
            # Dispute Outcome for closed disputes
            if is_closed:
                outcome = {
                    "id": f"out_{idx_str}",
                    "dispute_id": disp_id,
                    "outcome": disp_status,
                    "amount_deducted": 0 if disp_status == "won" else order_total,
                    "fee_deducted": 0 if disp_status == "won" else 15000, # 150 INR dispute fee on loss
                    "decided_at": (created_at + timedelta(days=6)).isoformat(),
                    "resolution_remarks": f"Card scheme resolved dispute in favor of {'merchant based on evidence submitted' if disp_status == 'won' else 'cardholder due to insufficient delivery telemetry'}."
                }
                dispute_outcomes.append(outcome)
            
            orders.append(order)
            payments.append(payment)
            fulfilments.append(fulfilment)

    # Integration configs
    integrations = [
        {
            "id": "cfg_razorpay_01",
            "merchant_id": merchant["id"],
            "provider": "razorpay",
            "is_enabled": False,
            "key_id_masked": "rzp_test_****1234",
            "encrypted_secret": None,
            "webhook_secret_masked": "whsec_****5678",
            "environment": "test",
            "last_synced_at": now.isoformat(),
            "sync_status": "healthy"
        },
        {
            "id": "cfg_mock_01",
            "merchant_id": merchant["id"],
            "provider": "mock",
            "is_enabled": True,
            "key_id_masked": "mock_internal_key",
            "encrypted_secret": None,
            "webhook_secret_masked": None,
            "environment": "mock",
            "last_synced_at": now.isoformat(),
            "sync_status": "healthy"
        }
    ]

    return {
        "merchant": merchant,
        "users": users,
        "customers": customers,
        "orders": orders,
        "payments": payments,
        "fulfilments": fulfilments,
        "customer_messages": messages,
        "disputes": disputes,
        "evidence_items": evidence_items,
        "evidence_links": evidence_links,
        "ai_investigations": ai_investigations,
        "response_drafts": response_drafts,
        "scoring_results": scoring_results,
        "dispute_outcomes": dispute_outcomes,
        "integrations": integrations
    }


if __name__ == "__main__":
    fixtures = generate_rj_kitchen_fixtures(seed=42)
    with open("data/synthetic/fixtures.json", "w") as f:
        json.dump(fixtures, f, indent=2)
    print(f"Generated {len(fixtures['disputes'])} synthetic disputes for RJ Kitchen successfully.")
