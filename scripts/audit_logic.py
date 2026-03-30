"""
audit_logic.py — Subscription pattern matching and financial analysis for CEO briefings.

This module provides the SUBSCRIPTION_PATTERNS dictionary and analysis functions
used by the generate-briefing skill and weekly audit process.

Matches the exact pattern shown in the hackathon docs (Section 4).
"""

from datetime import datetime, timedelta
from pathlib import Path


# ─── Subscription Pattern Matching ─────────────────────────────────────────────

SUBSCRIPTION_PATTERNS = {
    # Productivity & Collaboration
    "netflix.com": "Netflix",
    "spotify.com": "Spotify",
    "adobe.com": "Adobe Creative Cloud",
    "notion.so": "Notion",
    "slack.com": "Slack",
    "zoom.us": "Zoom",
    "dropbox.com": "Dropbox",
    "box.com": "Box",
    "atlassian.com": "Atlassian (Jira/Confluence)",
    "figma.com": "Figma",
    "canva.com": "Canva",
    "loom.com": "Loom",
    "calendly.com": "Calendly",

    # Development & Tech
    "github.com": "GitHub",
    "gitlab.com": "GitLab",
    "vercel.com": "Vercel",
    "netlify.com": "Netlify",
    "digitalocean.com": "DigitalOcean",
    "heroku.com": "Heroku",
    "aws.amazon.com": "AWS",
    "azure.microsoft.com": "Microsoft Azure",
    "cloud.google.com": "Google Cloud",
    "cloudflare.com": "Cloudflare",
    "datadog.com": "Datadog",
    "sentry.io": "Sentry",
    "linear.app": "Linear",

    # Marketing & Sales
    "mailchimp.com": "Mailchimp",
    "hubspot.com": "HubSpot",
    "salesforce.com": "Salesforce",
    "pipedrive.com": "Pipedrive",
    "lemlist.com": "Lemlist",
    "ahrefs.com": "Ahrefs",
    "semrush.com": "SEMrush",
    "buffer.com": "Buffer",
    "hootsuite.com": "Hootsuite",

    # Finance & Accounting
    "quickbooks.intuit.com": "QuickBooks",
    "xero.com": "Xero",
    "freshbooks.com": "FreshBooks",
    "stripe.com": "Stripe",
    "wave.com": "Wave Accounting",

    # AI & Productivity
    "openai.com": "OpenAI",
    "anthropic.com": "Anthropic/Claude",
    "midjourney.com": "Midjourney",
    "grammarly.com": "Grammarly",
    "otter.ai": "Otter.ai",
    "jasper.ai": "Jasper AI",

    # Communication
    "twilio.com": "Twilio",
    "sendgrid.com": "SendGrid",
    "intercom.com": "Intercom",
    "zendesk.com": "Zendesk",

    # Storage & Backup
    "icloud.com": "iCloud",
    "backblaze.com": "Backblaze",
    "google.com/drive": "Google Drive/Workspace",
    "microsoft.com/365": "Microsoft 365",

    # E-commerce
    "shopify.com": "Shopify",
    "woocommerce.com": "WooCommerce",
    "bigcommerce.com": "BigCommerce",
}


def analyze_transaction(transaction: dict) -> dict | None:
    """
    Analyze a single transaction and identify if it's a subscription.

    Args:
        transaction: Dict with keys: description, amount, date, id (optional)

    Returns:
        Dict with subscription info, or None if not a subscription.

    Example:
        transaction = {
            "description": "NETFLIX.COM MONTHLY SUBSCRIPTION",
            "amount": -15.99,
            "date": "2026-03-15"
        }
        result = analyze_transaction(transaction)
        # Returns: {"type": "subscription", "name": "Netflix", "amount": -15.99, ...}
    """
    description = transaction.get("description", "").lower()
    amount = transaction.get("amount", 0)
    date = transaction.get("date", "")

    for pattern, name in SUBSCRIPTION_PATTERNS.items():
        if pattern.lower() in description:
            return {
                "type": "subscription",
                "name": name,
                "pattern_matched": pattern,
                "amount": amount,
                "date": date,
                "description": transaction.get("description", ""),
                "transaction_id": transaction.get("id", ""),
            }

    return None


def find_subscriptions(transactions: list[dict]) -> list[dict]:
    """
    Filter a list of transactions to find all subscriptions.

    Args:
        transactions: List of transaction dicts

    Returns:
        List of subscription transactions with analysis data
    """
    subscriptions = []
    for txn in transactions:
        result = analyze_transaction(txn)
        if result:
            subscriptions.append(result)
    return subscriptions


def detect_duplicate_subscriptions(subscriptions: list[dict]) -> list[dict]:
    """
    Find subscriptions that appear to be duplicates (same name, charged twice).

    Returns list of duplicate groups.
    """
    seen = {}
    duplicates = []

    for sub in subscriptions:
        name = sub["name"]
        if name in seen:
            # Check if within same month
            try:
                date1 = datetime.fromisoformat(seen[name]["date"])
                date2 = datetime.fromisoformat(sub["date"])
                if abs((date1 - date2).days) < 35:
                    duplicates.append({
                        "name": name,
                        "occurrence_1": seen[name],
                        "occurrence_2": sub,
                        "total_charged": seen[name]["amount"] + sub["amount"],
                        "flag": "DUPLICATE_CHARGE",
                    })
            except (ValueError, TypeError):
                pass
        else:
            seen[name] = sub

    return duplicates


def detect_price_increases(
    current_month: list[dict],
    previous_month: list[dict],
    threshold_pct: float = 20.0,
) -> list[dict]:
    """
    Compare subscription costs between two months and flag increases > threshold%.

    Args:
        current_month:  This month's transactions
        previous_month: Last month's transactions
        threshold_pct:  Flag if price increased by more than this % (default: 20%)

    Returns:
        List of subscriptions with price increases above threshold
    """
    current_subs = {s["name"]: s for s in find_subscriptions(current_month)}
    previous_subs = {s["name"]: s for s in find_subscriptions(previous_month)}

    increases = []
    for name, current in current_subs.items():
        if name in previous_subs:
            prev_amount = abs(previous_subs[name]["amount"])
            curr_amount = abs(current["amount"])

            if prev_amount > 0:
                pct_change = ((curr_amount - prev_amount) / prev_amount) * 100
                if pct_change > threshold_pct:
                    increases.append({
                        "name": name,
                        "previous_amount": prev_amount,
                        "current_amount": curr_amount,
                        "increase_pct": round(pct_change, 1),
                        "increase_amount": curr_amount - prev_amount,
                        "flag": "PRICE_INCREASE",
                    })

    return increases


def flag_unused_subscriptions(
    subscriptions: list[dict],
    usage_logs: dict,
    unused_days_threshold: int = 30,
) -> list[dict]:
    """
    Flag subscriptions that haven't been used in `unused_days_threshold` days.

    Args:
        subscriptions:         List of active subscription transactions
        usage_logs:            Dict of {service_name: last_used_date_str}
        unused_days_threshold: Days without use before flagging (default: 30)

    Returns:
        List of flagged subscriptions with days_unused
    """
    flagged = []
    cutoff = datetime.now() - timedelta(days=unused_days_threshold)

    for sub in subscriptions:
        name = sub["name"]
        last_used_str = usage_logs.get(name)

        if last_used_str is None:
            # No usage data at all
            flagged.append({
                **sub,
                "days_unused": "unknown",
                "flag": "NO_USAGE_DATA",
                "recommendation": f"Verify if {name} is still being used",
            })
        else:
            try:
                last_used = datetime.fromisoformat(last_used_str)
                if last_used < cutoff:
                    days_unused = (datetime.now() - last_used).days
                    flagged.append({
                        **sub,
                        "days_unused": days_unused,
                        "flag": "UNUSED",
                        "recommendation": f"Cancel {name}? Not used in {days_unused} days. Saves ${abs(sub['amount']):.2f}/month",
                    })
            except (ValueError, TypeError):
                pass

    return flagged


def generate_subscription_report(
    transactions: list[dict],
    usage_logs: dict = None,
) -> dict:
    """
    Generate a complete subscription analysis report for the CEO briefing.

    Args:
        transactions: This month's transactions
        usage_logs:   Optional dict of {service_name: last_used_date_str}

    Returns:
        Report dict with all subscription analysis results
    """
    if usage_logs is None:
        usage_logs = {}

    subscriptions = find_subscriptions(transactions)
    total_monthly = sum(abs(s["amount"]) for s in subscriptions)

    duplicates = detect_duplicate_subscriptions(subscriptions)
    unused = flag_unused_subscriptions(subscriptions, usage_logs)

    # Calculate potential savings
    potential_savings = sum(abs(s["amount"]) for s in unused)

    return {
        "total_subscriptions": len(subscriptions),
        "total_monthly_cost": round(total_monthly, 2),
        "subscriptions": subscriptions,
        "duplicates_found": duplicates,
        "unused_subscriptions": unused,
        "potential_monthly_savings": round(potential_savings, 2),
        "generated_at": datetime.now().isoformat(),
    }


# ─── Markdown Report Generator ────────────────────────────────────────────────

def format_subscription_report_md(report: dict) -> str:
    """
    Format a subscription report as Markdown for the CEO briefing.
    """
    lines = [
        "## 💳 Subscription Analysis",
        "",
        f"**Total active subscriptions**: {report['total_subscriptions']}",
        f"**Total monthly cost**: ${report['total_monthly_cost']:.2f}",
        f"**Potential savings**: ${report['potential_monthly_savings']:.2f}/month",
        "",
    ]

    if report["unused_subscriptions"]:
        lines.append("### 🚨 Unused Subscriptions (Action Required)")
        for sub in report["unused_subscriptions"]:
            lines.append(
                f"- **{sub['name']}**: ${abs(sub['amount']):.2f}/month — "
                f"{sub.get('days_unused', '?')} days unused. "
                f"→ {sub.get('recommendation', 'Review')}"
            )
        lines.append("")

    if report["duplicates_found"]:
        lines.append("### ⚠️ Duplicate Charges Detected")
        for dup in report["duplicates_found"]:
            lines.append(
                f"- **{dup['name']}**: Charged ${abs(dup['total_charged']):.2f} "
                f"(appears twice this month) → Review immediately"
            )
        lines.append("")

    if not report["unused_subscriptions"] and not report["duplicates_found"]:
        lines.append("✅ No subscription issues detected this period.")

    return "\n".join(lines)


# ─── Example usage ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Test with sample transactions
    sample_transactions = [
        {"description": "NETFLIX.COM MONTHLY", "amount": -15.99, "date": "2026-03-01"},
        {"description": "SPOTIFY PREMIUM", "amount": -9.99, "date": "2026-03-05"},
        {"description": "NOTION.SO TEAM PLAN", "amount": -16.00, "date": "2026-03-10"},
        {"description": "CLIENT PAYMENT - INV001", "amount": 1500.00, "date": "2026-03-12"},
        {"description": "ADOBE CREATIVE CLOUD", "amount": -54.99, "date": "2026-03-15"},
        {"description": "GITHUB PRO PLAN", "amount": -4.00, "date": "2026-03-20"},
    ]

    # Simulate usage logs (service_name -> last used date)
    usage_logs = {
        "Netflix": "2026-02-01",   # 48 days ago — should flag
        "Spotify": "2026-03-20",   # Recent — OK
        "Notion": "2026-01-15",    # 65 days ago — should flag
        "Adobe Creative Cloud": "2026-03-18",  # Recent — OK
    }

    report = generate_subscription_report(sample_transactions, usage_logs)
    print(format_subscription_report_md(report))
    print(f"\nFull report: {report}")
