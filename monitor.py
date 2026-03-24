from analyzer import analyze_website
from database import get_active_sites, save_analysis


def run_monitoring_cycle():

    sites = get_active_sites()
    messages = []

    if not sites:
        return ["No active sites to monitor."]

    for url in sites:
        try:
            results = analyze_website(url)

            save_analysis(
                url,
                results["score"],
                results["risk_level"],
                results["total_snippets"],
                results["dark_count"]
            )

            messages.append(f"✔ Saved result for {url}")

        except Exception as e:
            messages.append(f"❌ Error analyzing {url}: {e}")

    return messages