from collections import defaultdict
from app.models.feedback import Feedback


class RankingService:
    def build_issue_summary(self, feedback_rows: list[Feedback]) -> list[dict]:
        grouped: dict[str, dict] = defaultdict(lambda: {
            "issue_label": "other",
            "total_mentions": 0,
            "negative_mentions": 0,
            "channels": set(),
        })

        for row in feedback_rows:
            issue = row.issue_label or "other"
            grouped[issue]["issue_label"] = issue
            grouped[issue]["total_mentions"] += 1
            if (row.sentiment or "").lower() == "negative":
                grouped[issue]["negative_mentions"] += 1
            grouped[issue]["channels"].add(row.channel)

        summary = []
        for item in grouped.values():
            summary.append({
                "issue_label": item["issue_label"],
                "total_mentions": item["total_mentions"],
                "negative_mentions": item["negative_mentions"],
                "channels": sorted(item["channels"]),
            })

        summary.sort(key=lambda x: (x["negative_mentions"], x["total_mentions"]), reverse=True)
        return summary
